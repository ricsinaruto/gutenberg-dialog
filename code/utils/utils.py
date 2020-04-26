import os


def get_removed_books(path):
    fnames = []
    path = os.path.join(path, 'banned_books.txt')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                if ('::') in line:
                    fnames.append(line.split(' :: ')[2].strip('\n') + '.txt')
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('Remove this text and paste lines from ' +
                    'author_and_title.txt corresponding to books which ' +
                    'you want to remove.')

    return fnames
