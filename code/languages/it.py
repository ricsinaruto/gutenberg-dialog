import re
import unicodedata

from languages.lang import Lang


class It(Lang):
    def delimiters(self):
        def d1(delimiter, line):
            return line.count(delimiter) * 2

        return {'--': d1}

    def process_file(self, paragraph_list, delimiter):
        dialogs = []
        count_doubles = 0
        # After some amount of characters interpret utterance as new dialog.
        chars_since_dialog = self.cfg.dialog_gap + 1
        for p in paragraph_list:
            # If the paragraph potentially contains dialog.
            if len(p) > 1:
                if delimiter in p[:2]:
                    text = ''
                    for i, segment in enumerate(p.split(delimiter)[1:]):
                        if not i % 2:
                            text += segment + ' '

                    # Extra filtering.
                    if p.count(delimiter) > 1:
                        count_doubles += 1

                    # If max chars exceeded start new dialog.
                    if chars_since_dialog > self.cfg.dialog_gap:
                        dialogs.append([])

                    dialogs[-1].append(' '.join(text.split()))
                    chars_since_dialog = 0
                else:
                    # Add the whole paragraph since there were no dialog.
                    chars_since_dialog += len(p)

        num_words = sum([len(p.split()) for p in paragraph_list])
        if count_doubles / num_words * 10000 > self.cfg.min_double_delim:
            self.dialogs.extend(dialogs)

    def clean_line(self, line):
        line = re.sub(' \' ', '\'', line)
        line = unicodedata.normalize('NFKD', line)
        line = re.sub('[.]', ' . ', line)
        line = re.sub('[?]', ' ? ', line)
        line = re.sub('[!]', ' ! ', line)
        line = re.sub('[-]', ' - ', line)
        line = re.sub('["]', ' " ', line)
        line = re.sub('[:]', ' : ', line)
        line = re.sub('[,]', ' , ', line)

        return line
