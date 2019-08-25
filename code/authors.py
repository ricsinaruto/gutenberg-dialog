from goodreads import client
import os
import time

from config import Config

# Goodreads client.
gc = client.GoodreadsClient(
  'SmWaBIc7D6RUpsZ2PHRQ', 'LoRL6vG6BgBdrp7UTmohITi8s2BOSch7QsAWwHKg')
cfg = Config()
authors = {}

for filename in os.listdir(cfg.directory):
  author = ''
  with open('texts/' + filename, errors='ignore') as f:
    for i, line in enumerate(f):
      # Find the line where there is author information.
      if 'Author:' in line:
        try:
          author = line.split(': ')[1]
          author = author.strip('\n')
        except:
          pass

      # Quit if we found the author or too many lines checked already.
      if author or i > cfg.max_first_lines:
        break

  try:
    # Try to find the author in Goodreads, and get his/her death date.
    if authors.get(author, 0) == 0:
      author_obj = gc.find_author(author)
      authors[author] = author_obj.died_at.split('/')[0]
      print(author)
      print(authors[author])
  except:
    pass

  # Goodreads limits request to 1/second, so sleep a bit.
  time.sleep(0.5)

with open('authors.txt', 'w') as f:
  f.write('\n'.join([k + ':' + str(v) for k, v in authors.items()]))
