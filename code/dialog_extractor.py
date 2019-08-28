import os

from config import Config


delimiters = ['"', '“', '‘']
abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
num_utterances = [0]


# Extract the dialogs from one file.
def process_file(cfg, dialogs, paragraph_list, filename, delimiter='"'):
  # After how many characters should we interpret the utterance as new dialog.
  chars_since_dialog = cfg.dialog_space + 1
  for p in paragraph_list:
    # If the paragraph potentially contains dialog.
    if delimiter in p:
      # If max chars exceeded since last utterance, then start a new dialog.
      if chars_since_dialog > cfg.dialog_space:
        dialogs.append([])

      utt = ''
      # Augment the segment so the splitting will always be correct.
      segments = ('YXC' + p + 'YXC').split(delimiter)

      good_segment = True
      # Join into a single utterance since we are inside a paragraph.
      if len(segments) > 2 and len(segments) % 2 == 1:
        for i, segment in enumerate(segments):
          if i == 1 and len(segment):
            # Make sure that the first sentence is upper-case thus a true utterance.
            if segment[0] in abc:
              good_segment = False
              break
          if i % 2 == 1:
            utt += segment + ' '

        if good_segment:
          dialogs[-1].append(filename + ':  ' + ' '.join(utt.split()))
          num_utterances[0] += 1

      # Add chars after last comma.
      if good_segment:
        chars_since_dialog = len(segments[-1]) - 3
      else:
        chars_since_dialog += len(p)
    else:
      # Otherwise add the whole paragraph since there was no dialog
      chars_since_dialog += len(p)


def process_file_(cfg, dialogs, paragraph_list, filename):
  # After how many characters should we interpret the utterance as new dialog.
  chars_since_dialog = cfg.dialog_space + 1
  for p in paragraph_list:
    # If the paragraph potentially contains dialog.
    if len(p) > 1:
      if '_' == p[0]:
        # If max chars exceeded since last utterance, then start a new dialog.
        if chars_since_dialog > cfg.dialog_space:
          dialogs.append([])

        utt = ''
        # Augment the segment so the splitting will always be correct.
        segments = ('YXC' + p).split('_')

        # Join into a single utterance since we are inside a paragraph.
        if len(segments) > 2:
          utt = ' '.join(segments[2:])
          dialogs[-1].append(filename + ':  ' + ' '.join(utt.split()))
          num_utterances[0] += 1

        chars_since_dialog = 0
      else:
        # Otherwise add the whole paragraph since there was no dialog
        chars_since_dialog += len(p)


def main():
  cfg = Config()
  file_stats = {}
  dialogs = []

  # Go through all books.
  for filename in os.listdir(cfg.directory):
    # Limiting the size of the dataset.
    if num_utterances[0] > cfg.max_utterances:
      break

    paragraph_list = ['']
    delimiter = '_'
    num_words = 0
    count_underscores = 0
    with open(
      cfg.directory + filename, errors='ignore', encoding='utf-8') as f:
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
        process_file_(cfg, dialogs, paragraph_list, filename)
      else:
        process_file(cfg, dialogs, paragraph_list, filename, delimiter)
    else:
      pass
      #print(filename)

    # Check whether there are enough dialogs in this file.
    if (len(dialogs) - len(old_dialogs)) / num_words * 10000 < cfg.min_delimiters / 10:
      print(filename)
      dialogs = list(old_dialogs)

  lengths = []
  dialog_lengths = []
  sample = open('sample.txt', 'w', encoding='utf-8')
  # Save the dialogs
  with open('dialogs.txt', 'w', encoding='utf-8') as f:
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

  print('Average utterance length: ' + str(sum(lengths) / (len(lengths) + 1)))
  print(
    'Average dialog length: ' + str(sum(dialog_lengths) / (len(dialog_lengths) + 1)))

  # Save. statistics to file.
  with open('statistics.txt', 'w') as f:
    for key, value in file_stats.items():
      f.write(key + ';' + str(value[0]) + ';' + str(value[1]) + '\n')


if __name__ == "__main__":
  main()
