import os
from gutenberg.query import get_metadata


# Go through all books.
for directory in os.listdir('texts'):
  for filename in os.listdir('texts/' + directory):
    try:
      r = get_metadata('rights', int(filename.split('.txt')[0]))
      r = iter(r).next().encode('utf-8')
    except:
      r = 'EMPTY'

    if 'Copyrighted.' in r or r == 'EMPTY' or r == 'None':
      os.remove(os.path.join('texts', directory, filename))
      print(filename)