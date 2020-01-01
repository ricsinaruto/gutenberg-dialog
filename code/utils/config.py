# These can also be set as arguments via the command line.
class Config:
  dialog_gap = 150
  max_length = 100  # max number of words in 1 utterance
  max_books = 1000  # limit size of the dataset
  min_delimiters = 150  # per 10.000 words
  kl_threshold = 2
  size_threshold = 20000  # minimum number of words in a book for filtering
  vocab_threshold = 0.2
  auto = False  # if True, run pipeline with questions
  clean_dialogs = True # if True, run preprocessing on dialogs
  languages = ['en', 'de']
