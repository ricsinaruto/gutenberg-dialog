# Copyright (c) 2019-present, HuggingFace Inc.
# All rights reserved. This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
import os
import math
import logging
from pprint import pformat
from argparse import ArgumentParser
from collections import defaultdict
from itertools import chain
import sys

import torch
from torch.nn.parallel import DistributedDataParallel, DataParallel
from torch.utils.data import DataLoader, Dataset
from ignite.engine import Engine, Events
from ignite.handlers import ModelCheckpoint
from ignite.metrics import Accuracy, Loss, MetricsLambda, RunningAverage
from ignite.contrib.handlers import ProgressBar, PiecewiseLinear
from ignite.contrib.handlers.tensorboard_logger import TensorboardLogger, OutputHandler, OptimizerParamsHandler
from transformers import (AdamW, OpenAIGPTDoubleHeadsModel, OpenAIGPTTokenizer,
                                    GPT2DoubleHeadsModel, GPT2Tokenizer, WEIGHTS_NAME, CONFIG_NAME)

from utils import get_dataset, make_logdir

SPECIAL_TOKENS = ["<bos>", "<eos>", "<speaker1>", "<speaker2>", "<pad>"]
ATTR_TO_SPECIAL_TOKEN = {'bos_token': '<bos>', 'eos_token': '<eos>', 'pad_token': '<pad>',
                         'additional_special_tokens': ['<speaker1>', '<speaker2>']}
MODEL_INPUTS = ["input_ids", "mc_token_ids", "lm_labels", "mc_labels", "token_type_ids"]
PADDED_INPUTS = ["input_ids", "lm_labels", "token_type_ids"]

logger = logging.getLogger(__file__)


def average_distributed_scalar(scalar, args):
    """ Average a scalar over the nodes if we are in distributed training. We use this for distributed evaluation. """
    if args.local_rank == -1:
        return scalar
    scalar_t = torch.tensor(scalar, dtype=torch.float, device=args.device) / torch.distributed.get_world_size()
    torch.distributed.all_reduce(scalar_t, op=torch.distributed.ReduceOp.SUM)
    return scalar_t.item()


def add_special_tokens_(model, tokenizer):
    """ Add special tokens to the tokenizer and the model if they have not already been added. """
    orig_num_tokens = len(tokenizer.encoder)
    num_added_tokens = tokenizer.add_special_tokens(ATTR_TO_SPECIAL_TOKEN) # doesn't add if they are already there
    if num_added_tokens > 0:
        model.resize_token_embeddings(new_num_tokens=orig_num_tokens + num_added_tokens)


def build_input_from_segments(history, reply, tokenizer, lm_labels=False, with_eos=True):
    """ Build a sequence of input from 3 segments: persona, history and last reply. """
    bos, eos, speaker1, speaker2 = tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS[:-1])
    sequence = [[bos]] + history + [reply + ([eos] if with_eos else [])]
    sequence = [sequence[0]] + [[speaker2 if (len(sequence)-i) % 2 else speaker1] + s for i, s in enumerate(sequence[1:])]

    input_seq = list(chain(*sequence))
    if len(input_seq) > 500:
        if len(sequence) == 3:
            sequence = [sequence[0], sequence[1][:-(len(input_seq) - 500)], sequence[2]]
        elif len(sequence) == 5:
            sequence = [sequence[0], sequence[3], sequence[4]]
        else:
            print(sequence)

    instance = {}
    instance["input_ids"] = list(chain(*sequence))
    instance["token_type_ids"] = [speaker2 if i % 2 else speaker1 for i, s in enumerate(sequence) for _ in s]
    instance["mc_token_ids"] = len(instance["input_ids"]) - 1
    instance["lm_labels"] = [-100] * len(instance["input_ids"])
    if lm_labels:
        instance["lm_labels"] = ([-100] * sum(len(s) for s in sequence[:-1])) + [-100] + sequence[-1][1:]
    return instance


def interm_gc(args, tokenizer):
    personachat = get_dataset(tokenizer, args.dataset_path, args.dataset_cache)
    num_candidates = 2

    logger.info("Build inputs and labels")
    datasets = {"train": defaultdict(list), "valid": defaultdict(list)}
    for dataset_name, dataset in personachat.items():
        for i, dialog in enumerate(dataset):

            # i don't want that much val data
            if dataset_name == 'train' or i < 100000000:
                for utterance in dialog["utterances"]:
                    for j, candidate in enumerate(utterance["candidates"][-num_candidates:]):
                        lm_labels = bool(j == num_candidates - 1)

                        instance = build_input_from_segments(utterance["history"][-3:].copy(), candidate, tokenizer, lm_labels)
                        for input_name, input_array in instance.items():
                            datasets[dataset_name][input_name].append(input_array)

                    datasets[dataset_name]["mc_labels"].append(num_candidates - 1)
                    datasets[dataset_name]["n_candidates"] = num_candidates

            if not i % 1000000:
                print(i)

    return datasets


class PaddedDataset(Dataset):
    def __init__(self, args, name, tokenizer):
        self.path = args.data_nuggets
        params = torch.load(os.path.join(self.path, 'params_' + name))
        self.padding = tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS[-1])
        self.length = params['length']
        self.name = name

    def __getitem__(self, index):
        try:
            nugget = torch.load(os.path.join(self.path, 'nuggets_' + self.name + '/' + str(index)))
        except:
            print(index)
            nugget = torch.load(os.path.join(self.path, 'nuggets_' + self.name + '/1'))

        t1 = nugget['input_ids']
        t3 = nugget['lm_labels']
        t5 = nugget['token_type_ids']

        t2 = nugget['mc_token_ids']
        t4 = nugget['mc_labels']

        return (t1, t2, t3, t4, t5, self.padding)

    def __len__(self):
        if self.length == 10000:
            return 100000
        else:
            return self.length


def save_data(args, data, tokenizer, split):

    for i, t in enumerate(data['mc_token_ids']):
        data['mc_token_ids'][i] = torch.tensor(t)

    for i, t in enumerate(data['mc_labels']):
        data['mc_labels'][i] = torch.tensor(t)

    for name in PADDED_INPUTS:
        for i, t in enumerate(data[name]):
            data[name][i] = [torch.tensor(t[0]), torch.tensor(t[1])]

    # save data to disk
    print(len(data['mc_labels']))
    for i in range(len(data['mc_labels'])):
        nug_name = os.path.join(args.data_nuggets, 'nuggets_' + split + '/' + str(i))
        if not os.path.isfile(nug_name):
            nugget = dict([(input_name, data[input_name][i]) for input_name in MODEL_INPUTS])
            torch.save(nugget, nug_name)

        if not i % 10000:
            print(i)

    # save params to disk
    torch.save({'length': len(data['input_ids'])}, os.path.join(args.data_nuggets, 'params_' + split))


def interm_gc2(args, tokenizer):
    if args.run_data:
        datasets = interm_gc(args, tokenizer)

        logger.info("Convert to tensor")
        for dataset_name in datasets:
            for input_name in MODEL_INPUTS:
                if input_name != "mc_labels":
                    new_list = []
                    for i, x in enumerate(datasets[dataset_name][input_name]):
                        if i % 2:
                            new_list.append([datasets[dataset_name][input_name][i - 1], x])

                    datasets[dataset_name][input_name] = new_list

        save_data(args, datasets['valid'], tokenizer, 'valid')
        save_data(args, datasets['train'], tokenizer, 'train')
        sys.exit()


    return PaddedDataset(args, 'train', tokenizer), PaddedDataset(args, 'valid', tokenizer)


def collate_fn(batch):
    def build_batch(ex):
        tensors = [0, 1, 2, 3, 4]
        for i, t in enumerate(ex[:5]):
            if i == 0 or i == 4:
                # change this back
                #t[0] = torch.tensor(t[0])
                #t[1] = torch.tensor(t[1])
                c1 = torch.cat((t[0], torch.tensor([ex[5]] * (max_l - len(t[0])))))
                c2 = torch.cat((t[1], torch.tensor([ex[5]] * (max_l - len(t[1])))))
                tensors[i] = torch.cat((c1.unsqueeze(0), c2.unsqueeze(0)))
            elif i == 2:
                #t[0] = torch.tensor(t[0])
                #t[1] = torch.tensor(t[1])
                c1 = torch.cat((t[0], torch.tensor([-100] * (max_l - len(t[0])))))
                c2 = torch.cat((t[1], torch.tensor([-100] * (max_l - len(t[1])))))
                tensors[i] = torch.cat((c1.unsqueeze(0), c2.unsqueeze(0)))
            else:
                tensors[i] = t

        return tuple(tensors)

    elem = batch[0]
    if isinstance(elem, torch.Tensor):
        out = None
        if torch.utils.data.get_worker_info() is not None:
            # If we're in a background process, concatenate directly into a
            # shared memory tensor to avoid an extra copy
            numel = sum([x.numel() for x in batch])
            storage = elem.storage()._new_shared(numel)
            out = elem.new(storage)
        return torch.stack(batch, 0, out=out)

    else:
        max_l = max(max([len(x[0][0]), len(x[0][1])]) for x in batch) + 1
        batch = list(map(build_batch, batch))

        transposed = zip(*batch)
        return [collate_fn(samples) for samples in transposed]


def get_data_loaders(args, tokenizer):
    """ Prepare the dataset for training and evaluation """
    train_dataset, valid_dataset = interm_gc2(args, tokenizer)

    logger.info("Build train and validation dataloaders")
    train_loader = DataLoader(train_dataset, sampler=None, collate_fn=collate_fn, batch_size=args.train_batch_size, shuffle=(not args.distributed))
    valid_loader = DataLoader(valid_dataset, sampler=None, collate_fn=collate_fn, batch_size=args.valid_batch_size, shuffle=False)
    train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset) if args.distributed else None
    valid_sampler = torch.utils.data.distributed.DistributedSampler(valid_dataset) if args.distributed else None
    return train_loader, valid_loader, train_sampler, valid_sampler


my_dataset = 'data/opensubtitles_es/'
def train():
    parser = ArgumentParser()
    parser.add_argument("--run_data", type=bool, default=False)
    parser.add_argument("--eval_freq", type=int, default=200000)
    parser.add_argument("--save_freq", type=int, default=2000)
    parser.add_argument("--data_nuggets", type=str, default=my_dataset)
    parser.add_argument("--dataset_path", type=str, default=my_dataset + 'json.txt', help="Path or url of the dataset. If empty download from S3.")
    parser.add_argument("--dataset_cache", type=str, default=my_dataset + 'cache', help="Path or url of the dataset cache")
    parser.add_argument("--model_checkpoint", type=str, default="gpt2", help="Path, url or short name of the model")
    parser.add_argument("--model", type=str, default="gpt2")
    parser.add_argument("--eval_before_start", type=bool, default=False, help="If true start with a first evaluation before training")
    parser.add_argument("--num_candidates", type=int, default=2, help="Number of candidates for training")
    parser.add_argument("--max_history", type=int, default=1, help="Number of previous exchanges to keep in history")
    parser.add_argument("--train_batch_size", type=int, default=2, help="Batch size for training")
    parser.add_argument("--valid_batch_size", type=int, default=2, help="Batch size for validation")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=8, help="Accumulate gradients on several steps")
    parser.add_argument("--lr", type=float, default=6.25e-5, help="Learning rate")
    parser.add_argument("--lm_coef", type=float, default=2.0, help="LM loss coefficient")
    parser.add_argument("--mc_coef", type=float, default=1.0, help="Multiple-choice loss coefficient")
    parser.add_argument("--max_norm", type=float, default=1.0, help="Clipping gradient norm")
    parser.add_argument("--n_epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--personality_permutations", type=int, default=1, help="Number of permutations of personality sentences")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu", help="Device (cuda or cpu)")
    parser.add_argument("--fp16", type=str, default="", help="Set to O0, O1, O2 or O3 for fp16 training (see apex documentation)")
    parser.add_argument("--local_rank", type=int, default=-1, help="Local rank for distributed training (-1: not distributed)")
    args = parser.parse_args()

    # logging is set to INFO (resp. WARN) for main (resp. auxiliary) process. logger.info => log main process only, logger.warning => log all processes
    logging.basicConfig(level=logging.INFO if args.local_rank in [-1, 0] else logging.WARN)
    logger.warning("Running process %d", args.local_rank)  # This is a logger.warning: it will be printed by all distributed processes
    logger.info("Arguments: %s", pformat(args))

    # Initialize distributed training if needed
    args.distributed = (args.local_rank != -1)
    if args.distributed:
        torch.cuda.set_device(args.local_rank)
        args.device = torch.device("cuda", args.local_rank)
        torch.distributed.init_process_group(backend='nccl', init_method='env://')

    logger.info("Prepare tokenizer, pretrained model and optimizer.")
    tokenizer_class = GPT2Tokenizer if "gpt2" in args.model else OpenAIGPTTokenizer # cant use Autotokenizer because checkpoint could be a Path
    tokenizer = tokenizer_class.from_pretrained(args.model_checkpoint)


    model_class = GPT2DoubleHeadsModel if "gpt2" in args.model else OpenAIGPTDoubleHeadsModel
    model = model_class.from_pretrained(args.model_checkpoint)
    model.to(args.device)
    # Add special tokens if they are not already added
    add_special_tokens_(model, tokenizer)
    optimizer = AdamW(model.parameters(), lr=args.lr, correct_bias=True)

    # Prepare model for FP16 and distributed training if needed (order is important, distributed should be the last)
    if args.fp16:
        from apex import amp  # Apex is only required if we use fp16 training
        model, optimizer = amp.initialize(model, optimizer, opt_level=args.fp16)
    #if args.distributed:
    #model = DistributedDataParallel(model, device_ids=[args.local_rank], output_device=args.local_rank)
    #model = DataParallel(model)

    logger.info("Prepare datasets")
    train_loader, val_loader, train_sampler, valid_sampler = get_data_loaders(args, tokenizer)

    # Training function and trainer
    def update(engine, batch):
        model.train()
        #print(batch)
        batch = tuple(input_tensor.to(args.device) for input_tensor in batch)
        input_ids, mc_token_ids, lm_labels, mc_labels, token_type_ids = batch
        (lm_loss), (mc_loss), *_ = model(
            input_ids, token_type_ids=token_type_ids, mc_token_ids=mc_token_ids,
            mc_labels=mc_labels, lm_labels=lm_labels
        )
        loss = (lm_loss * args.lm_coef + mc_loss * args.mc_coef) / args.gradient_accumulation_steps
        # DATAPARALLEL
        #loss = loss.sum()
        if args.fp16:
            with amp.scale_loss(loss, optimizer) as scaled_loss:
                scaled_loss.backward()
            torch.nn.utils.clip_grad_norm_(amp.master_params(optimizer), args.max_norm)
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_norm)
        if engine.state.iteration % args.gradient_accumulation_steps == 0:
            optimizer.step()
            optimizer.zero_grad()
        return loss.item()
    trainer = Engine(update)

    # Evaluation function and evaluator (evaluator output is the input of the metrics)
    def inference(engine, batch):
        model.eval()
        with torch.no_grad():
            batch = tuple(input_tensor.to(args.device) for input_tensor in batch)
            input_ids, mc_token_ids, lm_labels, mc_labels, token_type_ids = batch
            logger.info(tokenizer.decode(input_ids[0, -1, :].tolist()))
            # if we dont send labels to model, it doesnt return losses
            lm_logits, mc_logits, *_ = model(
                input_ids, token_type_ids=token_type_ids, mc_token_ids=mc_token_ids,
            )
            lm_logits_flat_shifted = lm_logits[..., :-1, :].contiguous().view(-1, lm_logits.size(-1))
            lm_labels_flat_shifted = lm_labels[..., 1:].contiguous().view(-1)
            return (lm_logits_flat_shifted, mc_logits), (lm_labels_flat_shifted, mc_labels)
    evaluator = Engine(inference)

    # Attach evaluation to trainer: we evaluate when we start the training and at the end of each epoch
    trainer.add_event_handler(Events.EPOCH_COMPLETED, lambda _: evaluator.run(val_loader))
    if args.n_epochs < 1:
        trainer.add_event_handler(Events.COMPLETED, lambda _: evaluator.run(val_loader))
    if args.eval_before_start:
        trainer.add_event_handler(Events.STARTED, lambda _: evaluator.run(val_loader))

    # Make sure distributed data samplers split the dataset nicely between the distributed processes
    if args.distributed:
        trainer.add_event_handler(Events.EPOCH_STARTED, lambda engine: train_sampler.set_epoch(engine.state.epoch))
        evaluator.add_event_handler(Events.EPOCH_STARTED, lambda engine: valid_sampler.set_epoch(engine.state.epoch))

    # Linearly decrease the learning rate from lr to zero
    scheduler = PiecewiseLinear(optimizer, "lr", [(0, args.lr), (args.n_epochs * len(train_loader), 0.0)])
    trainer.add_event_handler(Events.ITERATION_STARTED, scheduler)

    # Prepare metrics - note how we compute distributed metrics
    RunningAverage(output_transform=lambda x: x).attach(trainer, "loss")
    metrics = {"nll": Loss(torch.nn.CrossEntropyLoss(ignore_index=-100), output_transform=lambda x: (x[0][0], x[1][0])),
                 "accuracy": Accuracy(output_transform=lambda x: (x[0][1], x[1][1]))}
    metrics.update({"average_nll": MetricsLambda(average_distributed_scalar, metrics["nll"], args),
                    "average_accuracy": MetricsLambda(average_distributed_scalar, metrics["accuracy"], args)})
    metrics["average_ppl"] = MetricsLambda(math.exp, metrics["average_nll"])
    for name, metric in metrics.items():
        metric.attach(evaluator, name)

    # On the main process: add progress bar, tensorboard, checkpoints and save model, configuration and tokenizer before we start to train
    if args.local_rank in [-1, 0]:
        pbar = ProgressBar(persist=True)
        pbar.attach(trainer, metric_names=["loss"])
        evaluator.add_event_handler(Events.COMPLETED, lambda _: pbar.log_message("Validation: %s" % pformat(evaluator.state.metrics)))

        log_dir = make_logdir(args.model_checkpoint)
        tb_logger = TensorboardLogger(log_dir)

        tb_logger.attach(trainer, log_handler=OutputHandler(tag="training", metric_names=["loss"]), event_name=Events.ITERATION_COMPLETED)
        tb_logger.attach(trainer, log_handler=OptimizerParamsHandler(optimizer), event_name=Events.ITERATION_STARTED)
        tb_logger.attach(evaluator, log_handler=OutputHandler(tag="validation", metric_names=list(metrics.keys()), another_engine=trainer), event_name=Events.EPOCH_COMPLETED)

        checkpoint_handler = ModelCheckpoint(log_dir, 'checkpoint', save_interval=1, n_saved=100)
        trainer.add_event_handler(Events.EPOCH_COMPLETED, checkpoint_handler, {'mymodel': getattr(model, 'module', model)})  # "getattr" takes care of distributed encapsulation

        torch.save(args, log_dir + '/model_training_args.bin')
        getattr(model, 'module', model).config.to_json_file(os.path.join(log_dir, CONFIG_NAME))
        tokenizer.save_pretrained(log_dir)

    # Run the training
    trainer.run(train_loader, max_epochs=args.n_epochs)

    # On the main process: close tensorboard logger and rename the last checkpoint (for easy re-loading with OpenAIGPTModel.from_pretrained method)
    if args.local_rank in [-1, 0] and args.n_epochs > 0:
        os.rename(os.path.join(log_dir, checkpoint_handler._saved[-1][1]), os.path.join(log_dir, WEIGHTS_NAME))  # TODO: PR in ignite to have better access to saved file paths (cleaner)
        tb_logger.close()


if __name__ == "__main__":
    train()
