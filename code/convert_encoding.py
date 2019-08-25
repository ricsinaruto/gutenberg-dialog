import os

from config import Config

enc_table = {'ASCII': 'iso-8859-1',
             'UTF-8': 'utf8',
             'UTF‐8': 'utf8',
             'UTF8': 'utf8',
             'UF-8': 'utf8',
             'ISO-8859-1': 'iso-8859-1',
             'ISO-646-US (US-ASCII)': 'iso-8859-1',
             'iso-8859-1': 'iso-8859-1',
             'US-ASCII': 'iso-8859-1',
             'UTFâ€8': 'utf8',
             'ISO 8859-1': 'iso-8859-1',
             'ISO 8859-1 (Latin-1)': 'iso-8859-1',
             'ASCII, with a couple of ISO-8859-1 characters': 'iso-8859-1',
             'ASCII, with a few ISO-8859-1 characters': 'iso-8859-1',
             'ASCII, with some ISO-8859-1 characters': 'iso-8859-1',
             'ISO Latin-1': 'iso-8859-1',
             'ISO-Latin-1': 'iso-8859-1',
             'Latin1': 'iso-8859-1',
             'Latin-1': 'iso-8859-1',
             'Unicode UTF-8': 'utf8',
             'ISO-8859-2': 'iso-8859-2',
             'UTF-8.': 'utf8',
             'utf-8': 'utf8',
             'ISO8859_1': 'iso-8859-1',
             'ISO8859-1': 'iso-8859-1',
             'Latin 1': 'iso-8859-1',
             'iso-Latin-1': 'iso-8859-1',
             'UTR-8': 'utf8',
             'iso-latin-1': 'iso-8859-1',
             'windows-1252': 'windows-1252',
             'ISO-8859-15': 'iso-8859-1',
             'ISO-LATIN-1': 'iso-8859-1'}
cfg = Config()
filenames = {}

for filename in os.listdir(cfg.directory):
  # Skip directories.
  if os.path.isdir(cfg.directory + filename):
    continue

  # Don't go through the same book multiple times.
  check_name = (filename.strip('.txt') + '-a').split('-')[0]
  if filenames.get(check_name, 0) == 0:
    filenames[check_name] = 1
    encoding = ''

    # First find the encoding of the file.
    with open(cfg.directory + filename, errors='ignore') as f:
      for i, line in enumerate(f):
        # Check for encoding type.
        if 'Character set encoding:' in line:
          try:
            encoding = enc_table[line.split(':')[1].strip()]
            tru_encoding = line.split(':')[1].strip()
          except KeyError:
            print(line.split(':')[1].strip())

        # Quit if we found the encoding or too many lines.
        if encoding or i > cfg.max_first_lines:
          break

    # Convert the encoding of a file to utf-8.
    try:
      with open(cfg.directory + filename, 'rb') as f:
        data = f.read().decode(encoding).encode('utf-8')
      with open(cfg.out_dir + filename, 'wb') as f:
        f.write(data)
    except KeyError:
      print(encoding)
