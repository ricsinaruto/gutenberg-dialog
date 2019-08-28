import os
from collections import Counter

from config import Config


cfg = Config()
vocab = Counter()

for i, filename in enumerate(os.listdir(cfg.directory)):
  filename = cfg.directory + filename

  words = []
  with open(filename, errors='ignore', encoding='utf-8') as f:
    for line in f:
      words.extend(line.strip('\n').split())

  vocab.update(words)

  if i % 1000 == 0:
    print(i)

with open('vocab_en.txt', 'w', encoding='utf-8') as f:
  for word, count in vocab.most_common():
    f.write(word + '<SEP>' + str(count) + '\n')
