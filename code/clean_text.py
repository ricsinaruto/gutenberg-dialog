import os
import re
import unicodedata
import nltk

from config import Config


cfg = Config()
for filename in os.listdir(cfg.directory):
  text = []
  with open(os.path.join(cfg.directory, filename), encoding='utf-8') as f:
    for line in f:
      line = line.strip('\n').lower()
      line = re.sub(' \' ', '\'', line)
      line = unicodedata.normalize('NFKD', line)

      # Keep some special tokens.
      line = re.sub('[^a-z .,-_”“:?!"\'0-9]', '', line)
      line = re.sub('[.]', ' . ', line)
      line = re.sub('[?]', ' ? ', line)
      line = re.sub('[!]', ' ! ', line)
      line = re.sub('[-]', ' - ', line)
      line = re.sub('[_]', ' _ ', line)
      line = re.sub('["]', ' " ', line)
      line = re.sub('[:]', ' : ', line)
      line = re.sub('[”]', ' ” ', line)
      line = re.sub('[“]', ' “ ', line)

      words = nltk.word_tokenize(line)
      line = ' '.join(words)
      text.append(line)

  with open(os.path.join('clean_' + cfg.directory, filename), 'w', encoding='utf-8') as f:
    f.write('\n'.join(text))
