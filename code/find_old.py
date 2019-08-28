from collections import Counter
import os
import shutil

from config import Config

cfg = Config()
vocab = Counter()
with open('vocab_en.txt') as f:
  for line in f:
    line = line.strip('\n').split('<SEP>')
    vocab[line[0]] = int(line[1])

    # If count is lower than 3, skip those words:
    if int(line[1]) < 3:
      break

all_words = sum([value for key, value in vocab.items()])

for i, filename in enumerate(os.listdir(cfg.directory)):

  if i >= 0 and i < 10000:
    words = []
    with open(cfg.directory + filename, errors='ignore', encoding='utf-8') as f:
      for line in f:
        words.extend(line.strip('\n').split())

    file_vocab = Counter(words)

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
      try:
        shutil.copy('texts/en/' + filename, cfg.out_dir + filename)
      except:
        print(filename)
    else:
      print(filename)

    if i % 500 == 0:
      print(i)
