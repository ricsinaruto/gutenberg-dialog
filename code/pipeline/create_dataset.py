import os


def create(cfg):
    directory = cfg.directory
    for lang in cfg.languages:
        print('Creating dataset for ' + lang + ' language.')
        path = os.path.join(directory, lang)
        train = open(os.path.join(path, 'train.txt'), 'w', encoding='utf-8')
        dev = open(os.path.join(path, 'dev.txt'), 'w', encoding='utf-8')
        test = open(os.path.join(path, 'test.txt'), 'w', encoding='utf-8')

        if cfg.clean_dialogs:
            dialogs_text = open(
                os.path.join(path, 'dialogs_clean.txt'), encoding='utf-8')
        else:
            dialogs_text = open(
                os.path.join(path, 'dialogs.txt'), encoding='utf-8')

        with open(os.path.join(path, 'indices.txt'), encoding='utf-8') as f:
            indices = [int(line.strip('\n')) for line in f]

        # Read trian, dev, test indices
        with open(os.path.join('code', 'utils', 'dev_indices.txt')) as f:
            dev_indices = [int(line.strip('\n')) for line in f]
        with open(os.path.join('code', 'utils', 'test_indices.txt')) as f:
            test_indices = [int(line.strip('\n')) for line in f]

        dialogs = [[]]
        # Go through dialogs and filter them.
        for line in dialogs_text:
            if line == '\n':
                dialogs.append([])
            else:
                dialogs[-1].append(line.strip('\n'))

        # Filter based on saved indices, and split into final dataset.
        for i in indices:
            d = dialogs[i]
            book = int(d[0].split('.txt: ')[0])
            dialog = [utt.split('.txt: ')[1] for utt in d]

            if book in test_indices:
                test.write('\n'.join(dialog))
                test.write('\n\n')
            elif book in dev_indices:
                dev.write('\n'.join(dialog))
                dev.write('\n\n')
            else:
                train.write('\n'.join(dialog))
                train.write('\n\n')

        train.close()
        dev.close()
        test.close()
        dialogs_text.close()
