import argparse

from utils.config import Config
from pipeline.pipeline import Pipeline


def main():
  config = Config()
  parser = argparse.ArgumentParser(
    description='Code for building the Gutenberg Dialog Dataset')
  parser.add_argument('-dg', '--dialog_gap', default=config.dialog_gap,
                      help='Min. number of characters between two dialogs ' +
                      '(default: %(default)s)',
                      metavar='', type=int)
  parser.add_argument('-ml', '--max_length', default=config.max_length,
                      help='Max. number of words in 1 utterance ' +
                      '(default: %(default)s)',
                      metavar='', type=int)
  parser.add_argument('-b', '--max_books', default=config.max_books,
                      help='Limit the number of books in final dataset ' +
                      '(default: %(default)s)',
                      metavar='', type=int)
  parser.add_argument('-md', '--min_delimiters', default=config.min_delimiters,
                      help='Min. delimiters / 10.000 words needed in a book ' +
                      '(default: %(default)s)',
                      metavar='', type=int)
  parser.add_argument('-kl', '--kl_threshold',
                      default=config.kl_threshold,
                      help='KL divergence threshold for filtering old books ' +
                      '(default: %(default)s)',
                      metavar='', type=int)
  parser.add_argument('-st', '--size_threshold',
                      default=config.size_threshold,
                      help='Books with less words won\'t be filtered with KL' +
                      '(default: %(default)s)',
                      metavar='', type=int)
  parser.add_argument('-a', '--auto', default=config.auto,
                      help='Run in auto mode instead of pipeline step-by-step',
                      action='store_true')
  parser.add_argument('-c', '--clean_dialogs', default=config.clean_dialogs,
                      help='Whether to run pre-processing on dialogs',
                      action='store_false')
  parser.add_argument('-v', '--vocab_threshold',
                      default=config.vocab_threshold,
                      help='Ratio of max <unk> tokens allowed in a dialog ' +
                      '(default: %(default)s)',
                      metavar='', type=int)

  parser.parse_args(namespace=config)
  print(config.auto)

  p = Pipeline(config)
  p.run()


if __name__ == "__main__":
  main()
