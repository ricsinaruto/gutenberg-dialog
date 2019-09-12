class Config:
  dialog_space = 150
  max_length = 100
  max_first_lines = 200
  max_utterances = 100000000
  min_delimiters = 150  # per 10.000 words
  old_vocab_threshold = 0.45
  old_size_threshold = 20000  # minimum number of words
  language = 'English'
  directory = 'en/'
  split = 'test'
  out_dir = 'no_old_en/'
  languages = ['english', 'french', 'german', 'finnish', 'dutch', 'italian',
               'spanish', 'portuguese', 'chinese', 'greek', 'hungarian',
               'swedish', 'esperanto', 'latin', 'danish', 'tagalog', 'catalan',
               'norwegian', 'japanese', 'polish']
