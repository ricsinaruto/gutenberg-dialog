import re
import unicodedata


def delimiters():
  def d1(delimiter, line):
    if delimiter in line[:2]:
      return 1
    return 0

  return {'–': d1}


def process_file(cfg, dialogs, paragraph_list, filename, delimiter):
  # After how many characters should we interpret utterance as new dialog.
  chars_since_dialog = cfg.dialog_gap + 1
  for p in paragraph_list:
    # If the paragraph potentially contains dialog.
    if len(p) > 1:
      if delimiter in p[:2]:
        if p.count(delimiter) == 1:
          # If max chars exceeded since last utt, then start new dialog.
          if chars_since_dialog > cfg.dialog_gap:
            dialogs.append([])

          dialogs[-1].append(filename + ':  ' + ' '.join(p[len(delimiter):].split()))

          chars_since_dialog = 0
        elif dialogs:
          if not dialogs[-1]:
            dialogs.append([])
        else:
          dialogs.append([])
      else:
        # Otherwise add the whole paragraph since there was no dialog
        chars_since_dialog += len(p)


def clean_line(line):
  line = re.sub(' \' ', '\'', line)
  line = unicodedata.normalize('NFKD', line)
  return line
