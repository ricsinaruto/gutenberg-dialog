import os
import importlib
from collections import Counter

from utils import utils


def extract_(cfg, directory, lang):
    # Import relevant file.
    lang_module = importlib.import_module('languages.' + lang)
    lang_class = getattr(lang_module, lang.capitalize())(cfg)
    delimiters = lang_class.delimiters()

    file_stats = {}
    delimiter_filter = open(os.path.join(directory, lang, 'delim.txt'), 'w')

    # Get manually removed books.
    removed_books = utils.get_removed_books(os.path.join(directory, lang))
    path = os.path.join(directory, lang, 'books')
    # Go through all books.
    for i, fname in enumerate(os.listdir(path)):
        if fname not in removed_books:
            # Limiting the size of the dataset.
            if i > cfg.max_books:
                break

            paragraph_list = ['']
            delimiter_counts = Counter(delimiters.keys())
            path = os.path.join(directory, lang, 'books', fname)
            with open(path, errors='ignore', encoding='utf-8') as f:
                for line in f:
                    for delimiter, func in delimiters.items():
                        delimiter_counts[delimiter] += func(delimiter, line)

                    # Paragraphs are separated by new line.
                    # Usually one paragraph contains a single speaker.
                    if line == '\n':
                        paragraph_list.append('')
                    else:
                        paragraph_list[-1] += line.strip('\n') + ' '

            # Try to find a delimiter with higher count than underscores.
            delim, num_chars = delimiter_counts.most_common(1)[0]

            num_words = sum([len(p.split()) for p in paragraph_list])
            # Store the dialogs before processing.
            old_dialogs = list(lang_class.dialogs)
            # Need a min. number of delimiters for further processing.
            if num_chars / num_words * 10000 > cfg.min_delimiters:
                file_stats[fname] = [num_words, 0]
                lang_class.process_file(paragraph_list, delim)
                diff = len(lang_class.dialogs) - len(old_dialogs)

                # Add fname to utterances.
                for i, d in enumerate(lang_class.dialogs[-diff:]):
                    lang_class.dialogs[-diff + i] = [
                        fname + ':  ' + u for u in d]

                # Check whether there are enough dialogs in this file.
                if diff / num_words * 10000 < cfg.min_delimiters / 10:
                    lang_class.dialogs = list(old_dialogs)
                    delimiter_filter.write(fname + '\n')

            else:
                delimiter_filter.write(fname + '\n')

    delimiter_filter.close()
    return lang_class.dialogs, file_stats


def extract(cfg):
    directory = cfg.directory
    for lang in cfg.languages:
        print('Extracting dialogs for ' + lang + ' language.')

        # Separate processing for languages.
        dialogs, file_stats = extract_(cfg, directory, lang)

        # Common processing for all languages.
        lengths = []
        dialog_lengths = []
        path = os.path.join(directory, lang)
        sample = open(os.path.join(path, 'sample.txt'), 'w', encoding='utf-8')
        # Save the dialogs
        dialog_path = os.path.join(path, 'dialogs.txt')
        with open(dialog_path, 'w', encoding='utf-8') as f:
            for ind, d in enumerate(dialogs):
                split_ind = []
                # Remove too long utterances and split dialogs accordingly.
                for i, u in enumerate(d):
                    if len(u.split()) > cfg.max_length:
                        split_ind.append(i)

                split_ind = zip([-1] + split_ind, split_ind + [None])
                diags = [d[i + 1: j] for i, j in split_ind]

                for d in diags:
                    # Exclude single utterances.
                    if len(d) > 1:
                        f.write('\n'.join(d))
                        f.write('\n\n')

                        if ind % 100 == 0:
                            sample.write('\n'.join(d))
                            sample.write('\n\n')

                        file_stats[d[0].split(':')[0]][1] += len(d)
                        dialog_lengths.append(len(d))
                        lengths.extend([len(u.split()) for u in d])

        avg_dialog_length = sum(dialog_lengths) / (len(dialog_lengths) + 1)
        print(
            'Avg utterance length: ' + str(sum(lengths) / (len(lengths) + 1)))
        print('Avg dialog length: ' + str(avg_dialog_length))

        # Save. statistics to file.
        with open(os.path.join(path, 'statistics.txt'), 'w') as f:
            for key, value in file_stats.items():
                f.write(key + ';' + str(value[0]) + ';' + str(value[1]) + '\n')
