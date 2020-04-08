for split in ['train', 'dev', 'test']:
    with open(split + 'dialogs_clean.txt', encoding='utf-8') as f:
        dialogs = [[]]
        for line in f:
            if line == '\n':
                dialogs.append([])

            else:
                dialogs[-1].append(line.strip('\n'))

    source = open(split + 'Source.txt', 'w', encoding='utf-8')
    target = open(split + 'Target.txt', 'w', encoding='utf-8')

    for d in dialogs:
        for i, u in enumerate(d[:-1]):
            source.write(' <eou> '.join(d[:i + 1]) + '\n')
            target.write(d[i + 1] + '\n')

    source.close()
    target.close()
