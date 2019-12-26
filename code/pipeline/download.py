from gutenberg.acquire import load_etext, get_metadata_cache
from gutenberg.cleanup import strip_headers
from gutenberg.query import get_metadata
import os


def download(cfg, directory=os.path.join('data', 'raw')):
  print('Downloading Gutenberg data to: ' + directory)
  try:
    for i in range(1, cfg.max_books):
      # Get the book.
      try:
        text = strip_headers(load_etext(i)).strip().encode('utf-8')
      except:
        print('Could not download book: ' + str(i))
        continue

      # Get the language.
      try:
        lang = next(iter(get_metadata('language', i)))
      except StopIteration:
        print('Could not get language of: ' + str(i) + ' (skipping).')
        continue

      # Get the rights
      try:
        r = next(iter(get_metadata('rights', i)))
      except:
        r = 'EMPTY'

      if 'Copyrighted.' in r or r == 'EMPTY' or r == 'None':
        print('File not saved because copyrighted: ' + str(i))
        continue

      # Save the file to the correct directory.
      try:
        path = os.path.join(directory, lang)
        if not os.path.exists(path):
          os.mkdir(path)
        with open(os.path.join(path, str(i) + '.txt'), 'wb') as f:
          f.write(text)
      except:
        print('Could not save file: ' + str(i))

      if not i % 1000:
        print('Downloaded ' + str(i) + ' books out of ~60.000')

  except:
    print('The gutenberg package requires a metadata cache to be populated.')
    print('It looks like this is not done on your machine, so before ' +
          'downloading this needs to be run, and might take several hours.')
    cache = get_metadata_cache()
    try:
      cache.populate()
    except:
      #cache.delete()
      cache.populate()
