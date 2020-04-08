from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg._domain_model.exceptions import UnknownDownloadUriException
import os

from pipeline.pre_filter import pre_filter


def download(cfg, directory=os.path.join('data', 'raw')):
    print('Downloading Gutenberg data to: ' + directory)
    # Load language data for all books.
    with open(os.path.join('code', 'utils', 'langs.txt')) as f:
        counter = 0
        for line in f:
            [index, lang, r] = line.split(':')

            i = int(index)
            if i < cfg.max_books and int(r) == 1 and lang in cfg.languages:
                # Get the book.
                try:
                    text = strip_headers(load_etext(i)).strip().encode('utf-8')
                except UnknownDownloadUriException:
                    print('Could not download book: ' + str(i))
                    continue

                # Save the file to the correct directory.
                path = os.path.join(directory, lang)
                if not os.path.exists(path):
                    os.mkdir(path)
                with open(os.path.join(path, str(i) + '.txt'), 'wb') as f:
                    f.write(text)
                    counter += 1

                    if not counter % 1000:
                        print('Downloaded ' + str(counter) + ' books')

    # Continue with the next step in pipeline.
    pre_filter(cfg, directory)
