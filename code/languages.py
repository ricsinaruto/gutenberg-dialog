import os

from config import Config

cfg = Config()
filenames = {}
language_stats = {}

for ind, filename in enumerate(os.listdir(cfg.directory)):
  language = False
  with open(cfg.directory + filename, errors='ignore') as f:
    for i, line in enumerate(f):
      # Find the line where there is language information.
      if 'Language:' in line:
        lang = line.split(': ')[1]
        language_stats[lang] = language_stats.get(lang, 0) + 1
        language = True

      # Quit if we found the language or too many lines checked already.
      if language or i > cfg.max_first_lines:
        break

  if ind % 1000 == 0:
    print(ind)

with open('languages.txt', 'w') as f:
  f.write('\n'.join([key.strip('\n') + ':' + str(value)
                     for key, value in language_stats.items()]))
