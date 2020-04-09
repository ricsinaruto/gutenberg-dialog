import argparse

from utils.config import Config
from pipeline.pipeline import Pipeline


def main():
    config = Config()
    parser = argparse.ArgumentParser(
        description='Code for building the Gutenberg Dialog Dataset')
    parser.add_argument('-dg', '--dialog_gap', default=config.dialog_gap,
                        help='Min. number of characters between two dialogs ' +
                        '(default: %(default)s)', metavar='', type=int)
    parser.add_argument('-ml', '--max_length', default=config.max_length,
                        help='Max. number of words in 1 utterance ' +
                        '(default: %(default)s)', metavar='', type=int)
    parser.add_argument('-mb', '--max_books', default=config.max_books,
                        help='Limit the number of books in final dataset ' +
                        '(default: %(default)s)', metavar='', type=int)
    parser.add_argument('-md', '--min_delimiters',
                        default=config.min_delimiters,
                        help='Min delimiters / 10000 words needed in a book ' +
                        '(default: %(default)s)', metavar='', type=int)
    parser.add_argument('-kl', '--kl_threshold', default=config.kl_threshold,
                        help='KL divergence threshold for filtering books ' +
                        '(default: %(default)s)', metavar='', type=int)
    parser.add_argument('-st', '--size_threshold',
                        default=config.size_threshold,
                        help='#words threshold for filtering with KL' +
                        '(default: %(default)s)', metavar='', type=int)
    parser.add_argument('-cd', '--clean_dialogs', default=config.clean_dialogs,
                        help='Whether to run pre-processing on dialogs',
                        action='store_true')
    parser.add_argument('-vt', '--vocab_threshold',
                        default=config.vocab_threshold,
                        help='Ratio of unknown words allowed in a dialog ' +
                        '(default: %(default)s)', metavar='', type=int)
    parser.add_argument('-l', '--languages', default=config.languages,
                        help='Comma separated language codes ' +
                        'for which to build datasets',
                        metavar='', type=str)
    parser.add_argument('-d', '--download', default=config.download,
                        help='Whether to run download step',
                        action='store_true')
    parser.add_argument('-f1', '--pre_filter', default=config.pre_filter,
                        help='Whether to run pre-filter step',
                        action='store_true')
    parser.add_argument('-e', '--extract', default=config.extract,
                        help='Whether to run extracting step',
                        action='store_true')
    parser.add_argument('-f2', '--post_filter', default=config.post_filter,
                        help='Whether to run post filter step',
                        action='store_true')
    parser.add_argument('-c', '--create_dataset',
                        default=config.create_dataset,
                        help='Whether to run create dataset step',
                        action='store_true')
    parser.add_argument('-dir', '--directory', default=config.directory,
                        help='Directory where the language folders are',
                        metavar='', type=str)

    parser.parse_args(namespace=config)
    p = Pipeline(config)
    p.run()


if __name__ == "__main__":
    main()
