from gutenberg.query import get_metadata
from collections import Counter

authors = []
languages = []
rights = []
for i in range(1, 60200):
  try:
    a = get_metadata('author', i)
    authors.append(iter(a).next().encode('utf-8'))
  except StopIteration:
    authors.append('<EMPTY>')

  try:
    l = get_metadata('language', i)
    languages.append(iter(l).next().encode('utf-8'))
  except StopIteration:
    languages.append('<EMPTY>')

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
  f.write('\n'.join([k + ':' + str(v) for k, v in Counter(languages).items()]))

with open('right_counts.txt', 'wb') as f:
  f.write('\n'.join([k + ':' + str(v) for k, v in Counter(rights).items()]))
