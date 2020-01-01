import re
import unicodedata
import nltk
from collections import Counter
import random

from config import Config




def create(dialogs, filename, indices):
  train = open('train' + filename + '.txt', 'w', encoding='utf-8')
  dev = open('dev' + filename + '.txt', 'w', encoding='utf-8')
  test = open('test' + filename + '.txt', 'w', encoding='utf-8')


  with open(split + 'dialogs_clean.txt', encoding='utf-8') as f:
    dialogs = [[]]
    for line in f:
      if line == '\n':
        dialogs.append([])

      else:
        dialogs[-1].append(line.strip('\n'))

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




def main():
  #clean_dialogs()
  build_vocab()
  filter_dialogs()


if __name__ == "__main__":
  main()