import os


dialog_space = 1000
max_length = 100
filenames = []
dialogs = []


def process_ascii(paragraph_list, filename):
  # After how many characters should we interpret the utterance as a new dialog
  chars_since_dialog = dialog_space + 1
  for p in paragraph_list:
    # Utterance delimiters.
    if '"' in p:
      if chars_since_dialog > 500:
        dialogs.append([])

      utt = ''
      segments = ('a' + p + 'a').split('"')
      # Join into a single utterance since we are inside a paragraph.
      for i, segment in enumerate(segments):
        if i % 2 == 1:
          utt += segment + ' '

      dialogs[-1].append(filename + ':  ' + ' '.join(utt.split()))

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

      # Add chars after last comma.
      chars_since_dialog = len(segments[-1].split('â€ť')[-1])
    else:
      # Otherwise add the whole paragraph since no dialog
      chars_since_dialog += len(p)


process = {'ASCII': process_ascii,
           'UTF-8': process_utf,
           'ISO-8859-1': process_ascii,
           'ISO-646-US (US-ASCII)': process_ascii,
           'iso-8859-1': process_ascii,
           'US-ASCII': process_ascii,
           'UTFâ€8': process_utf,
           'ISO 8859-1': process_ascii,
           'ASCII, with a couple of ISO-8859-1 characters': process_ascii,
           'ISO Latin-1': process_ascii,
           'ISO-Latin-1': process_ascii}

for filename in os.listdir('texts'):
  if filename.split('-')[0] not in filenames:
    encoding = ''
    language = ''
    # Deal with separate file types.
    filenames.append(filename.split('-')[0])
    with open('texts/' + filename, errors='ignore') as f:
      # Paragraphs are separated by new line.
      # Usually one paragraph contains a single speaker.
      paragraph_list = ['']
      for i, line in enumerate(f):
        # Check for encoding type.
        if i < 200:
          if 'Character set encoding:' in line:
            encoding = line.split(':')[1].strip()

          # Only english language.
          if 'Language:' in line:
            print(line)
            if line.split(':')[1] != ' English\n':
              language = 'non-english'
              break

        # End of the book.
        if '*** END OF THIS PROJECT GUTENBERG' in line:
          break
        if line == '\n':
          paragraph_list.append('')
        else:
          paragraph_list[-1] += ' ' + line.strip('\n')

    if language != 'non-english' and encoding:
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
