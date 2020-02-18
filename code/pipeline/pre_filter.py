from collections import Counter
import os
import shutil
import math
import numpy as np
import re
import unicodedata
import nltk
from matplotlib import pyplot as plt

from pipeline.dialog_extractor import extract


def build_vocab(path, out_path):
  vocab = Counter()

  if not os.path.exists(out_path):
    os.mkdir(out_path)
    os.mkdir(os.path.join(out_path, 'books'))

  for i, filename in enumerate(os.listdir(path)):
    filename = os.path.join(path, filename)

    words = []
    with open(filename, errors='ignore', encoding='utf-8') as f:
      for line in f:
        words.extend(line.strip('\n').split())

    vocab.update(words)

  with open(
    os.path.join(out_path, 'book_vocab.txt'), 'w', encoding='utf-8') as f:
    for word, count in vocab.most_common():
      f.write(word + '<SEP>' + str(count) + '\n')


def pre_filter(cfg, directory=os.path.join('data', 'raw')):
  for lang in cfg.languages:
    print('Filtering old books based on vocabulary for ' + lang + ' language.')
    path = os.path.join(directory, lang)
    out_path = os.path.join(directory, '..', 'filtered', lang)

    if not os.path.exists(os.path.join(directory, '..', 'filtered')):
      os.mkdir(os.path.join(directory, '..', 'filtered'))

    if not os.path.exists(os.path.join(out_path, 'book_vocab.txt')):
      build_vocab(path, out_path)

    # Open a file to write filtered book numbers.
    filtered_books = open(os.path.join(out_path, 'filtered.txt'), 'w')

    vocab = Counter()
    with open(os.path.join(out_path, 'book_vocab.txt'), encoding='utf-8') as f:
      for line in f:
        line = line.strip('\n').split('<SEP>')
        vocab[line[0]] = int(line[1])

    total_words = sum([value for key, value in vocab.items()])
    total_distro = dict([(k, v / total_words) for k, v in vocab.items()])

    kl_divs = []
    # Go through individual books and calculate KL-divergence from total vocab.
    for i, filename in enumerate(os.listdir(path)):
      if i > cfg.max_books:
        break

      words = []
      file_path = os.path.join(path, filename)
      with open(file_path, errors='ignore', encoding='utf-8') as f:
        for line in f:
          words.extend(line.strip('\n').split())

      book_vocab = Counter(words)
      total_words = sum([value for key, value in book_vocab.items()])
      book_distro = dict([(k, v / total_words) for k, v in book_vocab.items()])

      kl_div = 0
      for key, value in book_distro.items():
        kl_div += value * math.log(value / total_distro[key])

      #kl_divs.append(kl_div)
      if not i % 1000:
        print('Filtered ' + str(i) + ' books.')

      # Let small books through because the distribution might be skewed.
      if kl_div < cfg.kl_threshold or total_words < cfg.size_threshold:
        shutil.copy(file_path, os.path.join(out_path, 'books', filename))
      else:
        filtered_books.write(filename + '\n')

    filtered_books.close()

  # Continue with the next step in pipeline.
  extract(cfg, os.path.join(directory, '..', 'filtered'))

  '''
  # plot kl div
  fig, (plt1) = plt.subplots(nrows=1, ncols=1)
  bins = np.arange(0, 10, 0.1)
  plt1.hist(np.array(kl_divs), bins=bins)
  plt.show()
  '''