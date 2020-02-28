import os

from pipeline.post_filter import post_filter


# globals
delimiters = ['"', '“', '‘']
abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
       'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


def hu(cfg, directory, lang='hu', delim='–'):
  def process_file(cfg, dialogs, paragraph_list, filename):
    num_utterances = 0
    # After how many characters should we interpret utterance as new dialog.
    chars_since_dialog = cfg.dialog_gap + 1
    for p in paragraph_list:
      # If the paragraph potentially contains dialog.
      if len(p) > 1:
        if delim in p[:2]:
          if p.count(delim) == 1:
            # If max chars exceeded since last utt, then start new dialog.
            if chars_since_dialog > cfg.dialog_gap:
              dialogs.append([])

            if delim == '--':
              dialogs[-1].append(filename + ':  ' + ' '.join(p[2:].split()))
            else:
              dialogs[-1].append(filename + ':  ' + ' '.join(p[1:].split()))
            num_utterances += 1

            chars_since_dialog = 0
          elif dialogs:
            if not dialogs[-1]:
              dialogs.append([])
          else:
            dialogs.append([])
        else:
          # Otherwise add the whole paragraph since there was no dialog
          chars_since_dialog += len(p)

    return num_utterances

  file_stats = {}
  dialogs = []
  num_utterances = 0

  delimiter_filter = open(os.path.join(directory, lang, 'delim.txt'), 'w')

  # Go through all books.
  for i, filename in enumerate(
      os.listdir(os.path.join(directory, lang, 'books'))):
    # Limiting the size of the dataset.
    if i > cfg.max_books:
      break

    path = os.path.join(directory, lang, 'books', filename)
    paragraph_list = ['']
    num_words = 0
    count_hyphens = 0
    with open(path, errors='ignore', encoding='utf-8') as f:
      for i, line in enumerate(f):
        num_words += len(line.split())

        if delim in line[:2]:
          count_hyphens += 1

        # Paragraphs are separated by new line.
        # Usually one paragraph contains a single speaker.
        if line == '\n':
          paragraph_list.append('')
        else:
          paragraph_list[-1] += line.strip('\n') + ' '

    # Store the dialogs before processing.
    old_dialogs = list(dialogs)
    # Need a min. number of delimiters for further processing.
    if count_hyphens / num_words * 10000 > cfg.min_delimiters:
      file_stats[filename] = [num_words, 0]
      num_utterances += process_file(cfg, dialogs, paragraph_list, filename)

      # Check whether there are enough dialogs in this file.
      if (len(dialogs) - len(old_dialogs)) / num_words * 10000 < \
        cfg.min_delimiters / 10:
        dialogs = list(old_dialogs)
        delimiter_filter.write(filename + '\n')

    else:
      delimiter_filter.write(filename + '\n')

  return dialogs, file_stats


def en(cfg, directory, lang='en'):
  # Extract the dialogs from one file.
  def process_file(cfg, dialogs, paragraph_list, filename, delimiter='"'):
    num_utterances = 0
    # After how many characters should we interpret utterance as new dialog.
    chars_since_dialog = cfg.dialog_gap + 1
    for p in paragraph_list:
      # If the paragraph potentially contains dialog.
      if delimiter in p:
        # If max chars exceeded since last utterance, then start a new dialog.
        if chars_since_dialog > cfg.dialog_gap:
          dialogs.append([])

        utt = ''
        # Augment the segment so the splitting will always be correct.
        segments = ('YXC' + p + 'YXC').split(delimiter)

        good_segment = True
        # Join into a single utterance since we are inside a paragraph.
        if len(segments) > 2 and len(segments) % 2 == 1:
          for i, segment in enumerate(segments):
            if i == 1 and len(segment):
              # Make sure the first sentence is upper-case: true utterance.
              if segment[0] in abc:
                good_segment = False
                break
            if i % 2 == 1:
              utt += segment + ' '

          if good_segment:
            dialogs[-1].append(filename + ':  ' + ' '.join(utt.split()))
            num_utterances += 1

        # Add chars after last comma.
        if good_segment:
          chars_since_dialog = len(segments[-1]) - 3
        else:
          chars_since_dialog += len(p)
      else:
        # Otherwise add the whole paragraph since there was no dialog
        chars_since_dialog += len(p)

    return num_utterances

  def process_file_(cfg, dialogs, paragraph_list, filename):
    num_utterances = 0
    # After how many characters should we interpret utterance as new dialog.
    chars_since_dialog = cfg.dialog_gap + 1
    for p in paragraph_list:
      # If the paragraph potentially contains dialog.
      if len(p) > 1:
        if '_' == p[0]:
          # If max chars exceeded since last utterance, then start new dialog.
          if chars_since_dialog > cfg.dialog_gap:
            dialogs.append([])

          utt = ''
          # Augment the segment so the splitting will always be correct.
          segments = ('YXC' + p).split('_')

          # Join into a single utterance since we are inside a paragraph.
          if len(segments) > 2:
            utt = ' '.join(segments[2:])
            dialogs[-1].append(filename + ':  ' + ' '.join(utt.split()))
            num_utterances += 1

          chars_since_dialog = 0
        else:
          # Otherwise add the whole paragraph since there was no dialog
          chars_since_dialog += len(p)

    return num_utterances

  # Main function start.
  file_stats = {}
  dialogs = []
  num_utterances = 0

  delimiter_filter = open(os.path.join(directory, lang, 'delim.txt'), 'w')

  # Go through all books.
  for i, filename in enumerate(
      os.listdir(os.path.join(directory, lang, 'books'))):
    # Limiting the size of the dataset.
    if i > cfg.max_books:
      break

    path = os.path.join(directory, lang, 'books', filename)
    paragraph_list = ['']
    delimiter = '_'
    num_words = 0
    count_underscores = 0
    with open(path, errors='ignore', encoding='utf-8') as f:
      for i, line in enumerate(f):
        num_words += len(line.split())

        if line[0] == '_':
          count_underscores += 1

        # Paragraphs are separated by new line.
        # Usually one paragraph contains a single speaker.
        if line == '\n':
          paragraph_list.append('')
        else:
          paragraph_list[-1] += line.strip('\n') + ' '

    # Find delimiter.
    text = ''.join(paragraph_list)

    # Try to find a delimiter with higher count than underscores.
    biggest = count_underscores
    for d in delimiters:
      if d == '“' or d == '‘':
        num_chars = text.count(d) * 2
      else:
        num_chars = text.count(d)
      if num_chars > biggest:
        biggest = num_chars
        delimiter = d

    # We have to deal with single quatation marks.
    if delimiter == '‘':
      paragraph_list = [p.replace('’ ', '‘ ')for p in paragraph_list]
    # Unify the later processing.
    if delimiter == '“':
      paragraph_list = [p.replace('”', '“')for p in paragraph_list]

    # Store the dialogs before processing.
    old_dialogs = list(dialogs)
    # Need a min. number of delimiters for further processing.
    if biggest / num_words * 10000 > cfg.min_delimiters:
      file_stats[filename] = [num_words, 0]
      # Special treatment.
      if delimiter == '_':
        num_utterances += process_file_(
          cfg, dialogs, paragraph_list, filename)
      else:
        num_utterances += process_file(
          cfg, dialogs, paragraph_list, filename, delimiter)

      # Check whether there are enough dialogs in this file.
      if (len(dialogs) - len(old_dialogs)) / num_words * 10000 < \
        cfg.min_delimiters / 10:
        dialogs = list(old_dialogs)
        delimiter_filter.write(filename + '\n')

    else:
      delimiter_filter.write(filename + '\n')

  delimiter_filter.close()
  return dialogs, file_stats


def fr(cfg, directory):
  return hu(cfg, directory, lang='fr', delim='--')


def it(cfg, directory):
  return hu(cfg, directory, lang='it', delim='--')


def extract(cfg, directory=os.path.join('data', 'filtered')):
  lang_func = {'en': en, 'hu': hu, 'fr': fr, 'it': it}
  for lang in cfg.languages:
    print('Extracting dialogs for ' + lang + ' language.')

    # Separate processing for languages.
    dialogs, file_stats = lang_func[lang](cfg, directory)

    # Common processing for all languages.
    lengths = []
    dialog_lengths = []
    path = os.path.join(directory, lang)
    sample = open(os.path.join(path, 'sample.txt'), 'w', encoding='utf-8')
    # Save the dialogs
    with open(os.path.join(path, 'dialogs.txt'), 'w', encoding='utf-8') as f:
      for ind, d in enumerate(dialogs):
        split_indices = []
        # Remove too long utterances and split dialogs accordingly.
        for i, u in enumerate(d):
          if len(u.split()) > cfg.max_length:
            split_indices.append(i)

        diags = [d[i + 1: j]
                 for i, j in zip([-1] + split_indices, split_indices + [None])]

        for d in diags:
          # Exclude single utterances.
          if len(d) > 1:
            f.write('\n'.join(d))
            f.write('\n')
            f.write('\n')

            if ind % 100 == 0:
              sample.write('\n'.join(d))
              sample.write('\n')
              sample.write('\n')

            file_stats[d[0].split(':')[0]][1] += len(d)
            dialog_lengths.append(len(d))
            lengths.extend([len(u.split()) for u in d])

    avg_dialog_length = sum(dialog_lengths) / (len(dialog_lengths) + 1)
    print('Avg utterance length: ' + str(sum(lengths) / (len(lengths) + 1)))
    print('Avg dialog length: ' + str(avg_dialog_length))

    # Save. statistics to file.
    with open(os.path.join(path, 'statistics.txt'), 'w') as f:
      for key, value in file_stats.items():
        f.write(key + ';' + str(value[0]) + ';' + str(value[1]) + '\n')

  # Continue with next step in pipeline.
  post_filter(cfg, directory)
