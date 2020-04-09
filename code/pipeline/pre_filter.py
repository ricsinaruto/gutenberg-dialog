from collections import Counter
import os
import shutil
import math


def build_vocab(path, out_path):
    vocab = Counter()

    if not os.path.exists(out_path):
        os.mkdir(out_path)
        os.mkdir(os.path.join(out_path, 'books'))

    for i, fname in enumerate(os.listdir(path)):
        fname = os.path.join(path, fname)

        words = []
        with open(fname, errors='ignore', encoding='utf-8') as f:
            for line in f:
                words.extend(line.strip('\n').split())

        vocab.update(words)

    book_vocab_path = os.path.join(out_path, 'book_vocab.txt')
    with open(book_vocab_path, 'w', encoding='utf-8') as f:
        for word, count in vocab.most_common():
            f.write(word + '<SEP>' + str(count) + '\n')


def pre_filter(cfg):
    directory = cfg.directory

    metadata = {}
    # Read metadata first for author and title.
    path = os.path.join('code', 'utils', 'metadata.txt')
    with open(path, encoding='utf-8') as f:
        for line in f:
            [index, lang, r, author, title] = line.split(':')
            metadata[index] = ' :: '.join([author, title.strip('\n')])

    for lang in cfg.languages:
        print('Filtering old books based on vocab for ' + lang + ' language.')
        path = os.path.join(directory, lang)
        out_path = os.path.join(directory, '..', 'filtered', lang)

        if not os.path.exists(os.path.join(directory, '..', 'filtered')):
            os.mkdir(os.path.join(directory, '..', 'filtered'))

        if not os.path.exists(os.path.join(out_path, 'book_vocab.txt')):
            build_vocab(path, out_path)

        # Open a file to write filtered book numbers.
        filtered_books = open(os.path.join(out_path, 'filtered.txt'), 'w')

        vocab = Counter()
        book_vocab_path = os.path.join(out_path, 'book_vocab.txt')
        with open(book_vocab_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip('\n').split('<SEP>')
                vocab[line[0]] = int(line[1])

        total_words = sum([value for key, value in vocab.items()])
        total_distro = dict([(k, v / total_words) for k, v in vocab.items()])

        fnames = []
        # Go through single books and calculate KL-divergence from total vocab.
        for i, fname in enumerate(os.listdir(path)):
            if i > cfg.max_books:
                break

            words = []
            file_path = os.path.join(path, fname)
            with open(file_path, errors='ignore', encoding='utf-8') as f:
                for line in f:
                    words.extend(line.strip('\n').split())

            vocab = Counter(words)
            num_words = sum([value for key, value in vocab.items()])
            book_distro = dict([(k, v / num_words) for k, v in vocab.items()])

            kl_div = 0
            for key, value in book_distro.items():
                kl_div += value * math.log(value / total_distro[key])

            if not i % 1000:
                print('Filtered ' + str(i) + ' books.')

            # Let small books through because the distribution might be skewed.
            if kl_div < cfg.kl_threshold or num_words < cfg.size_threshold:
                shutil.copy(file_path, os.path.join(out_path, 'books', fname))
                fnames.append(fname.strip('.txt'))
            else:
                filtered_books.write(fname + '\n')

        path = os.path.join(out_path, 'author_and_title.txt')
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                meta_list = [metadata[name] + ' :: ' + name for name in fnames]
                f.write('\n'.join(sorted(meta_list)))

        filtered_books.close()

    # Prepare directory for next step.
    cfg.directory = os.path.join(directory, '..', 'filtered')
