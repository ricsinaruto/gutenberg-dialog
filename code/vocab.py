import os
from collections import Counter

from config import Config


cfg = Config()
vocab = Counter()
for filename in os.listdir(cfg.directory):
  filename = cfg.directory + filename

  with open(filename, errors='ignore', encoding='utf-8') as f:
    for line in f:
      vocab.update(line.strip('\n').lower().split())

with open('vocab.txt', 'w', encoding='utf-8') as f:
  for word, count in vocab.most_common():
    f.write(word + ':' + str(count) + '\n')
