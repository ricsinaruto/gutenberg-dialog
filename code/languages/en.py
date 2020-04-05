import re
import unicodedata


def delimiters():
  def d1(delimiter, line):
    return line.count(delimiter)

  def d2(delimiter, line):
    return line.count(delimiter) * 2

  def d3(delimiter, line):
    if line[0] == delimiter:
      return 1
    return 0

  # Dictionary of delimiters and their respective counting functions.
  return {'"': d1, '“': d2, '‘': d2, '_': d3}


def process_file_(cfg, dialogs, paragraph_list, filename):
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

        chars_since_dialog = 0
      else:
        # Otherwise add the whole paragraph since there was no dialog
        chars_since_dialog += len(p)


# Extract the dialogs from one file.
def process_file(cfg, dialogs, paragraph_list, filename, delimiter):
  if delimiter == '_':
    process_file_(cfg, dialogs, paragraph_list, filename)
    return

  # We have to deal with single quatation marks.
  if delimiter == '‘':
    paragraph_list = [p.replace('’ ', '‘ ')for p in paragraph_list]
  # Unify the later processing.
  if delimiter == '“':
    paragraph_list = [p.replace('”', '“')for p in paragraph_list]

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
            if segment[0] == segment[0].lower():
              good_segment = False
              break
          if i % 2 == 1:
            utt += segment + ' '

        if good_segment:
          dialogs[-1].append(filename + ':  ' + ' '.join(utt.split()))

      # Add chars after last comma.
      if good_segment:
        chars_since_dialog = len(segments[-1]) - 3
      else:
        chars_since_dialog += len(p)
    else:
      # Otherwise add the whole paragraph since there was no dialog
      chars_since_dialog += len(p)


def clean_line(line):
  line = re.sub(' \' ', '\'', line)
  line = unicodedata.normalize('NFKD', line)

  # Keep some special tokens.
  line = re.sub('[^a-z .,-:?!"\'0-9]', '', line)
  line = re.sub('[.]', ' . ', line)
  line = re.sub('[?]', ' ? ', line)
  line = re.sub('[!]', ' ! ', line)
  line = re.sub('[-]', ' - ', line)
  line = re.sub('["]', ' " ', line)
  line = re.sub('[:]', ' : ', line)
  line = re.sub('[,]', ' , ', line)
  return line
