import re
import unicodedata
from languages.lang import Lang

class De(Lang):

    delim_pairs = {
        '"': '"',
        '„': '“',
        '»': '«'
    }

    def delimiters(self):
        def d1(delimiter, line):
            return line.count(delimiter)

        def d2(delimiter, line):
            return line.count(delimiter) * 2

        def d3(delimiter, line):
            if line[0] == delimiter:
                return 1
            return 0

        # Dictionary of delimiters and their respective counting functions.
        return {'"': d1, '„': d2, '»': d2}

    def process_file(self, paragraph_list, delimiter):
        dialogs = []
        # After some amount of characters interpret utterance as new dialog.
        chars_since_dialog = self.cfg.dialog_gap + 1
        for p in paragraph_list:
            # If the paragraph potentially contains dialog.
            if len(p) > 1:
                if delimiter in p[:2]:
                    text = ''
                    for segment in p.split(delimiter)[1:]:
                        text += segment.split(De.delim_pairs[delimiter])[0]

                    # If max chars exceeded start new dialog.
                    if chars_since_dialog > self.cfg.dialog_gap:
                        dialogs.append([])

                    dialogs[-1].append(' '.join(text.split()))
                    chars_since_dialog = 0
                else:
                    # Add the whole paragraph since there were no dialog.
                    chars_since_dialog += len(p)

        self.dialogs.extend(dialogs)

    # Extract the dialogs from one file.
    def clean_line(self, line):
        line = re.sub(' \' ', '\'', line)
        line = unicodedata.normalize('NFKD', line)

        # Keep some special tokens.
        line = re.sub(r'([.?!-":,])', r' \1 ', line)
        return line
