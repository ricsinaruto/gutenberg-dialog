import re
import unicodedata
import nltk
from collections import Counter
import random

from config import Config


cfg = Config()


# Create a cleaned version of dialogs.
def clean_dialogs():
  text = []
  with open(cfg.filename + '.txt', encoding='utf-8') as f:
    for i, line in enumerate(f):
      if line != '\n':
        line = line.split('.txt:')[1]
        line = line.strip('\n').lower()
        line = re.sub(' \' ', '\'', line)
        line = unicodedata.normalize('NFKD', line)

        # Keep some special tokens.
        line = re.sub('[^a-z .,-:?!"\'0-9]', '', line)
        line = re.sub('[.]', ' . ', line)
        line = re.sub('[?]', ' ? ', line)
        line = re.sub('[!]', ' ! ', line)
        line = re.sub('[-]', ' - ', line)
        line = re.sub('["]', ' " ', line)
        line = re.sub('[:]', ' : ', line)

        words = nltk.word_tokenize(line)
        line = ' '.join(words)
        if len(words) == 0:
          # Need this, so there are no empty lines.
          line = '<PLACEHOLDER>'
        text.append(line)
      else:
        text.append('')

      if i % 100000 == 0:
        print(i)

  with open(cfg.filename + '_clean.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(text))


# Build vocab based on cleaned dialogs.
vocab = Counter()
def build_vocab():
  with open(cfg.filename + '_clean.txt', encoding='utf-8') as f:
    for i, line in enumerate(f):
      vocab.update(line.strip('\n').split())

      if i % 1000000 == 0:
        print(i)

  with open('vocab_big.txt', 'w', encoding='utf-8') as f:
    for word, count in vocab.most_common():
      f.write(word + '<SEP>' + str(count) + '\n')


def split_and_save(dialogs, filename, indices):
  train = open('train' + filename + '.txt', 'w', encoding='utf-8')
  dev = open('dev' + filename + '.txt', 'w', encoding='utf-8')
  test = open('test' + filename + '.txt', 'w', encoding='utf-8')

  split_counter = 0
  for i in indices:
    split_counter += 1
    if split_counter <= 90:
      train.write('\n'.join(dialogs[i]))
      train.write('\n\n')
    elif split_counter <= 95:
      dev.write('\n'.join(dialogs[i]))
      dev.write('\n\n')
    elif split_counter <= 100:
      test.write('\n'.join(dialogs[i]))
      test.write('\n\n')
    else:
      split_counter = 0

  train.close()
  dev.close()
  test.close()


def filter_dialogs():
  # Fast replacement of OOV words
  swap_vocab = {}
  for i, (word, count) in enumerate(vocab.most_common()):
    swap_vocab[word] = word
    if i >= 100000:
      swap_vocab[word] = '<unk>'

  swap_vocab['<PLACEHOLDER>'] = '<unk>'

  dialogs = [[]]
  with open(cfg.filename + '_clean.txt', encoding='utf-8') as f:
    for line in f:
      if line == '\n':
        dialogs.append([])

      else:
        dialogs[-1].append(line.strip('\n'))

  good_dialogs = []
  good_indices = []
  for i, d in enumerate(dialogs):
    text = []
    for u in d:
      text.extend([swap_vocab[word] for word in u.split()])

    # If <unk> percentage is lower than 20% we can keep the dialog.
    if len(text) > 5 * text.count('<unk>'):
      good_dialogs.append(d)
      good_indices.append(i)

    if i % 100000 == 0:
      print(i)

  # Apply filtering to the original dialogs.
  dialogs = [[]]
  with open(cfg.filename + '.txt', encoding='utf-8') as f:
    for line in f:
      if line == '\n':
        dialogs.append([])

      else:
        dialogs[-1].append(line.strip('\n'))

  good_og_dialogs = []
  for i in good_indices:
    good_og_dialogs.append(dialogs[i])

  indices = [i for i in range(len(good_og_dialogs))]
  random.shuffle(indices)
  split_and_save(good_og_dialogs, cfg.filename, indices)
  split_and_save(good_dialogs, cfg.filename + '_clean', indices)


def main():
  #clean_dialogs()
  build_vocab()
  filter_dialogs()


if __name__ == "__main__":
  main()