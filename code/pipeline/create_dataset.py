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

        books = {}
        # Filter based on saved indices, and split into final dataset.
        for i in indices:
            d = dialogs[i]
            book = int(d[0].split('.txt: ')[0])
            books[book] = 0
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

        metadata = {}
        # Read metadata first for author and title.
        in_path = os.path.join('code', 'utils', 'metadata.txt')
        with open(in_path, encoding='utf-8') as f:
            for line in f:
                [index, lang, r, author, title] = line.split(':')
                metadata[index] = ' :: '.join([author, title.strip('\n')])

        path = os.path.join(path, 'author_and_title.txt')
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                meta_list = [metadata[str(i)] + ' :: ' + str(i) for i in books]
                f.write('\n'.join(sorted(meta_list)))
        else:
            print('author_and_title.txt already exists in ' + lang + ' folder')
            print('Please specify (choose a number) how to merge the ' +
                  'current list with the new list:\n' +
                  '  1. Keep current list\n' +
                  '  2. Overwrite with new list\n' +
                  '  3. Keep the union of the two lists\n' +
                  '  4. Keep the intersection of the two lists')
            choice = input()

            if choice == '2':
                with open(path, 'w', encoding='utf-8') as f:
                    meta_list = [
                        metadata[str(i)] + ' :: ' + str(i) for i in books]
                    f.write('\n'.join(sorted(meta_list)))
            if choice == '3':
                old_list = []
                with open(path, encoding='utf-8') as f:
                    for line in f:
                        old_list.append(line.strip('\n'))

                with open(path, 'w', encoding='utf-8') as f:
                    new_list = [
                        metadata[str(i)] + ' :: ' + str(i) for i in books]
                    new_list.extend(old_list)
                    f.write('\n'.join(sorted(set(new_list))))
            if choice == '4':
                old_list = set()
                with open(path, encoding='utf-8') as f:
                    for line in f:
                        old_list.add(line.strip('\n'))

                with open(path, 'w', encoding='utf-8') as f:
                    new_list = set(
                        [metadata[str(i)] + ' :: ' + str(i) for i in books])
                    meta_list = list(new_list.intersection(old_list))
                    f.write('\n'.join(sorted(meta_list)))
