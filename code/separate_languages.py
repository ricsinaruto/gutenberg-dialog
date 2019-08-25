import os

from config import Config

cfg = Config()
for ind, filename in enumerate(os.listdir(cfg.directory)):
  filename = cfg.directory + filename
  with open(filename, errors='ignore', encoding='utf-8') as f:
    for i, line in enumerate(f):
      # Find the line where there is language information.
      if 'Language:' in line:
        lang = line.split(': ')[1].lower().strip('\n')
        break

      # Quit if too many lines checked already.
      if i > cfg.max_first_lines:
        break

  # Move the file to language specific folder.
  if lang in cfg.languages:
    destination = 'curated_' + lang
    if not os.path.exists(destination):
      os.mkdir(destination)
    os.rename(filename, destination + '/' + filename.split('/')[1])
  else:
    print(lang)

  if ind % 1000 == 0:
    print(ind)
