from collections import Counter
import os
import shutil

from config import Config

cfg = Config()
vocab = Counter()
with open('vocab.txt') as f:
  for line in f:
    line = line.strip('\n').split('<SEP>')
    vocab[line[0]] = int(line[1])

    # If count is lower than 3, skip those words:
    if int(line[1]) < 3:
      break

all_words = sum([value for key, value in vocab.items()])

for filename in os.listdir(cfg.directory):

  file_vocab = Counter()
  with open(cfg.directory + filename, errors='ignore', encoding='utf-8') as f:
    for line in f:
      file_vocab.update(line.strip('\n').split())

  total_words = sum([value for key, value in file_vocab.items()])
  for key, value in file_vocab.items():
    file_vocab[key] *= int(all_words / total_words)
  file_vocab.subtract(vocab)

  difference = 0
  for key, value in file_vocab.items():
    if value > 0:
      difference += value

  # We need to let small books through because the distribution might be skewed.
  if difference / all_words < cfg.old_vocab_threshold or total_words < cfg.old_size_threshold:
    shutil.copy('en/' + filename, cfg.out_dir + filename)
  else:
    print(filename)
