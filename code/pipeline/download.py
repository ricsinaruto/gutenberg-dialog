from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg._domain_model.exceptions import UnknownDownloadUriException
import os


def download(cfg):
    print('Downloading Gutenberg data to: ' + cfg.directory)
    # Load language data for all books.
    path = os.path.join('code', 'utils', 'metadata.txt')
    with open(path, encoding='utf-8') as f:
        counter = 0
        for line in f:
            [index, lang, r, author, title] = line.split('\t')

            r = int(r)
            i = int(index)
            if counter < cfg.max_books and r == 1 and lang in cfg.languages:
                # Get the book.
                try:
                    text = strip_headers(load_etext(i)).strip().encode('utf-8')
                except UnknownDownloadUriException:
                    print('Could not download book: ' + str(i))
                    continue

                # Save the file to the correct directory.
                path = os.path.join(cfg.directory, lang)
                if not os.path.exists(path):
                    os.mkdir(path)
                with open(os.path.join(path, str(i) + '.txt'), 'wb') as f:
                    f.write(text)

                    counter += 1
                    if not counter % 1000:
                        print('Downloaded ' + str(counter) + ' books')
