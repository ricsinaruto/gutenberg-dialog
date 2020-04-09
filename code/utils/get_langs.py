from gutenberg.query import get_metadata

lang_file = open('metadata.txt', 'w')

for i in range(1, 65000):
    try:
        lang = next(iter(get_metadata('language', i)))
    except StopIteration:
        print('Could not get language of: ' + str(i) + ' (skipping).')
        continue

    try:
        r = next(iter(get_metadata('rights', i)))
    except StopIteration:
        r = 'EMPTY'

    try:
        a = next(iter(get_metadata('author', i))).encode('utf-8')
    except StopIteration:
        a = '<EMPTY>'
    a = a.replace(':', '')

    try:
        title = next(iter(get_metadata('title', i))).encode('utf-8')
    except StopIteration:
        title = '<EMPTY>'
    title = title.replace(':', '')
    title = ' '.join(title.split())

    if 'Copyrighted.' in r or r == 'EMPTY' or r == 'None':
        print('File not saved because copyrighted: ' + str(i))
        lang_file.write('{}:{}:0:{}:{}\n'.format(str(i), lang, a, title))
    else:
        lang_file.write('{}:{}:1:{}:{}\n'.format(str(i), lang, a, title))

lang_file.close()
