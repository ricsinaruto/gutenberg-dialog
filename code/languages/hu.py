import re
import unicodedata
from languages.lang import LANG_base


class LANG(LANG_base):
    def delimiters(self):
        def d1(delimiter, line):
            if delimiter in line[:2]:
                return 1
            return 0

        return {'–': d1}

    def process_file(self, paragraph_list, delimiter):
        # After some amount of characters interpret utterance as new dialog.
        chars_since_dialog = self.cfg.dialog_gap + 1
        for p in paragraph_list:
            # If the paragraph potentially contains dialog.
            if len(p) > 1:
                if delimiter in p[:2]:
                    if p.count(delimiter) == 1:
                        # If max chars exceeded start new dialog.
                        if chars_since_dialog > self.cfg.dialog_gap:
                            self.dialogs.append([])

                        self.dialogs[-1].append(
                            ' '.join(p[len(delimiter):].split()))

                        chars_since_dialog = 0
                    elif self.dialogs:
                        if not self.dialogs[-1]:
                            self.dialogs.append([])
                    else:
                        self.dialogs.append([])
                else:
                    # Add the whole paragraph since there were no dialog.
                    chars_since_dialog += len(p)

    def clean_line(self, line):
        line = re.sub(' \' ', '\'', line)
        line = unicodedata.normalize('NFKD', line)
        return line
