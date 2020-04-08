from collections import Counter
import os
import nltk
import importlib

from pipeline.create_dataset import create


def clean_dialogs(cfg, directory, lang):
    lang_module = importlib.import_module('languages.' + lang)
    lang_class = lang_module.LANG(cfg)

    text = []
    path = os.path.join(directory, 'dialogs.txt')
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if line != '\n':
                [book, line] = line.split('.txt:')
                line = line.strip('\n').lower()

                line = lang_class.clean_line(line)

                words = nltk.word_tokenize(line)
                line = ' '.join(words)
                if len(words) == 0:
                    # Need this, so there are no empty lines.
                    line = '<PLACEHOLDER>'
                text.append(book + '.txt: ' + line)
            else:
                text.append('')

            if i % 100000 == 0:
                print('Cleaned ' + str(i) + ' lines.')

    path = os.path.join(directory, 'dialogs_clean.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text))


# Build vocab based on cleaned dialogs.
def build_vocab_dialogs(cfg, directory):
    vocab = Counter()
    print('Building vocabulary for filtering.')
    path = os.path.join(directory, 'dialogs_clean.txt')
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if line != '\n':
                vocab.update(line.strip('\n').split('.txt: ')[1].split())

    path = os.path.join(directory, 'dialogs_vocab.txt')
    with open(path, 'w', encoding='utf-8') as f:
        for word, count in vocab.most_common():
            f.write(word + '<SEP>' + str(count) + '\n')

    return vocab


def post_filter(cfg, directory=os.path.join('data', 'filtered')):
    for lang in cfg.languages:
        print('Filtering dialogs based on vocab for ' + lang + ' language.')
        path = os.path.join(directory, lang)

        clean_dialogs(cfg, path, lang)
        vocab = build_vocab_dialogs(cfg, path)

        # Fast replacement of OOV words
        swap_vocab = {}
        for i, (word, count) in enumerate(vocab.most_common()):
            swap_vocab[word] = word
            if i >= 100000:
                swap_vocab[word] = '<unk>'

        swap_vocab['<PLACEHOLDER>'] = '<unk>'

        dialogs = [[]]
        dialog_path = os.path.join(path, 'dialogs_clean.txt')
        with open(dialog_path, encoding='utf-8') as f:
            for line in f:
                if line == '\n':
                    dialogs.append([])

                else:
                    dialogs[-1].append(line.strip('\n').split('.txt: ')[1])

        indices = []
        for i, d in enumerate(dialogs):
            text = []
            for u in d:
                text.extend([swap_vocab[word] for word in u.split()])

            # If <unk> percentage is lower than 20% we can keep the dialog.
            if len(text) * cfg.vocab_threshold > text.count('<unk>'):
                indices.append(str(i))

            if i % 100000 == 0:
                print('Filtered ' + str(i) + ' dialogs.')

        indices_path = os.path.join(path, 'indices.txt')
        with open(indices_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(indices))

    create(cfg, directory)
