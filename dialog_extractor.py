import os


dialog_space = 1000
max_length = 100
filenames = []
dialogs = []
num_utterances = [0]
max_utterances = 1000000


def process_ascii(paragraph_list, filename):
  # After how many characters should we interpret the utterance as a new dialog
  chars_since_dialog = dialog_space + 1
  for p in paragraph_list:
    # Utterance delimiters.
    if '"' in p:
      if chars_since_dialog > 500:
        dialogs.append([])

      utt = ''
      segments = ('YXC' + p + 'YXC').split('"')
      # Join into a single utterance since we are inside a paragraph.
      if len(segments) > 2 and len(segments) % 2 == 1:
        for i, segment in enumerate(segments):
          if i % 2 == 1:
            utt += segment + ' '

        dialogs[-1].append(filename + ':  ' + ' '.join(utt.split()))
        num_utterances[0] += 1

      # Add chars after last comma.
      chars_since_dialog = len(segments[-1])
    else:
      # Otherwise add the whole paragraph since no dialog
      chars_since_dialog += len(p)


def process_utf(paragraph_list, filename):
  # After how many characters should we interpret the utterance as a new dialog
  chars_since_dialog = dialog_space + 1
  for p in paragraph_list:
    # Utterance delimiters.
    if 'â€ś' in p and 'â€ť' in p:
      if chars_since_dialog > 500:
        dialogs.append([])

      utt = ''
      segments = p.split('â€ś')
      # Join into a single utterance since we are inside a paragraph.
      for segment in segments:
        utt += segment.split('â€ť')[0] + ' '

      dialogs[-1].append(filename + ':  ' + ' '.join(utt.split()))
      num_utterances[0] += 1

      # Add chars after last comma.
      chars_since_dialog = len(segments[-1].split('â€ť')[-1])
    else:
      # Otherwise add the whole paragraph since no dialog
      chars_since_dialog += len(p)


enc_table = {'ASCII': 'iso-8859-1',
           'UTF-8': 'utf8',
           'UTF‐8': 'utf8',
           'ISO-8859-1': 'iso-8859-1',
           'ISO-646-US (US-ASCII)': 'iso-8859-1',
           'iso-8859-1': 'iso-8859-1',
           'US-ASCII': 'iso-8859-1',
           'UTFâ€8': 'utf8',
           'ISO 8859-1': 'iso-8859-1',
           'ASCII, with a couple of ISO-8859-1 characters': 'iso-8859-1',
           'ISO Latin-1': 'iso-8859-1',
           'ISO-Latin-1': 'iso-8859-1'}

process = {'iso-8859-1': process_ascii,
           'utf8': process_utf}

for filename in os.listdir('texts'):
  if os.path.isdir('texts/' + filename):
    continue
  if os.path.getsize('texts/' + filename) > 10000000:
    continue
  # Limiting the size of the dataset.
  if num_utterances[0] > max_utterances:
    break
  if filename.split('-')[0] not in filenames:
    paragraph_list = ['']
    encoding = ''
    language = ''
    # Deal with separate file types.
    filenames.append(filename.split('-')[0])

    # First find the encoding and language of the file.
    with open('texts/' + filename, errors='ignore') as f:
      for i, line in enumerate(f):
        # Check for encoding type.
        if 'Character set encoding:' in line:
          try:
            encoding = enc_table[line.split(':')[1].strip()]
          except KeyError:
            break

        # Only english language.
        if 'Language:' in line:
          print(line)
          if line.split(':')[1] != ' English\n':
            language = 'non-english'
        if (language and encoding) or i > 500:
          break

    if language != 'non-english' and encoding:
      with open('texts/' + filename, errors='ignore') as f:
        # Paragraphs are separated by new line.
        # Usually one paragraph contains a single speaker.
        for line in f:
          # End of the book.
          if '*** END OF THIS PROJECT GUTENBERG' in line:
            break
          if line == '\n':
            paragraph_list.append('')
          else:
            paragraph_list[-1] += ' ' + line.strip('\n')

      process[encoding](paragraph_list, filename)

lengths = []
dialog_lengths = []
with open('dialogs.txt', 'w') as f:
  for d in dialogs:
    split_indices = []
    # Remove too long utterances and split dialogs accordingly.
    for i, u in enumerate(d):
      if len(u.split()) > max_length:
        split_indices.append(i)

    diags = [
      d[i + 1: j] for i, j in zip([-1] + split_indices, split_indices + [None])]

    for d in diags:
      # Exclude single utterances.
      if len(d) > 1:
        f.write('\n'.join(d))
        f.write('\n')
        f.write('\n')

        dialog_lengths.append(len(d))
        lengths.extend([len(u.split()) for u in d])

print('Average utterance length: ' + str(sum(lengths) / len(lengths)))
print(
  'Average dialog length: ' + str(sum(dialog_lengths) / len(dialog_lengths)))
