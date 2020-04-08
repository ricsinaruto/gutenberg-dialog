from gutenberg.query import get_metadata
from collections import Counter

authors = []
langs = []
rights = []
for i in range(1, 60200):
    try:
        a = get_metadata('author', i)
        authors.append(iter(a).next().encode('utf-8'))
    except StopIteration:
        authors.append('<EMPTY>')

    try:
        lang = get_metadata('language', i)
        langs.append(iter(lang).next().encode('utf-8'))
    except StopIteration:
        langs.append('<EMPTY>')

    try:
        r = get_metadata('rights', i)
        rights.append(iter(r).next().encode('utf-8'))
    except StopIteration:
        rights.append('<EMPTY>')

    if i % 1000 == 0:
        print(i)

with open('author_counts.txt', 'wb') as f:
    f.write('\n'.join([k + ':' + str(v) for k, v in Counter(authors).items()]))

with open('lang_counts.txt', 'wb') as f:
    f.write('\n'.join([k + ':' + str(v) for k, v in Counter(langs).items()]))

with open('right_counts.txt', 'wb') as f:
    f.write('\n'.join([k + ':' + str(v) for k, v in Counter(rights).items()]))
