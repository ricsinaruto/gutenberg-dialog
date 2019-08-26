from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg.query import get_metadata
import os

from config import Config


cfg = Config()
for i in range(1, 60200):
  # Get the book.
  try:
    text = strip_headers(load_etext(i)).strip().encode('utf-8')
  except:
    print(i)
    continue

  # Get the language.
  try:
    lang = iter(get_metadata('language', i)).next().encode('utf-8')
  except StopIteration:
    continue

  # Save the file to the correct directory.
  try:
    if not os.path.exists(lang):
      os.mkdir(lang)
    with open(os.path.join(lang, str(i) + '.txt'), 'wb') as f:
      f.write(text)
  except:
    print('Could not save file: ' + str(i))

  if i % 1000 == 0:
    print(i)
