import re
import unicodedata
import nltk
from collections import Counter

from config import Config


cfg = Config()


def clean_dialogs():
  text = []
  with open('dialogs.txt', encoding='utf-8') as f:
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
      text.append(line)

      if i % 100000 == 0:
        print(i)

  with open('dialogs_clean.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(text))


vocab = Counter()
def build_vocab():
  with open('dialogs_clean.txt', encoding='utf-8') as f:
    for i, line in enumerate(f):
      vocab.update(line.strip('\n').split())

    if i % 1000000 == 0:
      print(i)

  with open('vocab_big.txt', 'w', encoding='utf-8') as f:
    for word, count in vocab.most_common():
      f.write(word + '<SEP>' + str(count) + '\n')


def filter_dialogs():
  swap_vocab = {}
  for i, word, count in enumerate(vocab.most_common()):
    swap_vocab[word] = word
    if i >= 100000:
      swap_vocab[word] = '<unk>'

  dialogs = [[]]
  with open('dialogs_clean.txt', encoding='utf-8') as f:
    for line in f:
      if line == '\n':
        dialogs.append([])

      else:
        dialogs[-1].append(line.strip('\n'))

  filtered_dialogs = []
  for i, d in enumerate(dialogs):
    text = []
    for u in d:
      text.extend([swap_vocab[word] for word in u.split()])

    if len(text) > 5 * text.count('<unk>'):
      filtered_dialogs.append(d)

  


def main():
  build_vocab()
  #filter_dialogs()


if __name__ == "__main__":
  main()