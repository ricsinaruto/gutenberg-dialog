from gutenberg.acquire import load_etext, get_metadata_cache
from gutenberg.cleanup import strip_headers
from gutenberg.query import get_metadata
from gutenberg._domain_model.exceptions import UnknownDownloadUriException as download_ex
import os

from pipeline.pre_filter import pre_filter


def download_(cfg, directory=os.path.join('data', 'raw')):
  for i in range(1, cfg.max_books):
    # Get the language.
    try:
      lang = next(iter(get_metadata('language', i)))
    except StopIteration:
      print('Could not get language of: ' + str(i) + ' (skipping).')
      continue

    # Proceed only if we want this language.
    if lang in cfg.languages:
      # Get the book.
      try:
        text = strip_headers(load_etext(i)).strip().encode('utf-8')
      except download_ex:
        print('Could not download book: ' + str(i))
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
      print('Downloaded ' + str(i) + ' books')


def download(cfg, directory=os.path.join('data', 'raw')):
  print('Downloading Gutenberg data to: ' + directory)

  try:
    download_(cfg, directory)
  except:
    print('The gutenberg package requires a metadata cache to be populated.')
    print('It looks like this is not done on your machine, so before ' +
          'downloading this needs to be run, and might take several hours.')
    cache = get_metadata_cache()
    try:
      cache.populate()
    except:
      print('It looks like you already have a metadata cache, ' +
            'do you want to delete it? (y/n)')
      inp = input()
      if inp == 'y':
        cache.delete()
      cache.populate()

    download_(cfg, directory)

  # Continue with the next step in pipeline.
  pre_filter(cfg, directory)
