from gutenberg.query import get_metadata

lang_file = open('langs.txt', 'w')

for i in range(1, 65000):
    try:
        lang = next(iter(get_metadata('language', i)))
    except StopIteration:
        print('Could not get language of: ' + str(i) + ' (skipping).')
        continue

    # Get the rights
    try:
        r = next(iter(get_metadata('rights', i)))
    except:
        r = 'EMPTY'

    if 'Copyrighted.' in r or r == 'EMPTY' or r == 'None':
        print('File not saved because copyrighted: ' + str(i))
        lang_file.write(str(i) + ':' + lang + ':0' '\n')
    else:
        lang_file.write(str(i) + ':' + lang + ':1' '\n')

lang_file.close()
