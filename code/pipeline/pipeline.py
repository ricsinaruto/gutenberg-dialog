from pipeline.download import download
from pipeline.filter import pre_filter
from pipeline.dialog_extractor import extract


class Pipeline:
  def __init__(self, config):
    self.config = config
    self.auto = config.auto

  def run(self):
    if self.auto:
      print('You have selected the auto mode, the program will ' +
            'automatically run through the steps and build the dataset.')
      download(self.config)
      pre_filter(self.config)
      extract(self.config)
    else:
      print('You have selected the pipeline mode, the program will now step ' +
            'you through building the dataset.')
      print('Have you downloaded the data? (y/n)')
      inp = input()
      if inp == 'n':
        download(self.config)
        pre_filter(self.config)
        extract(self.config)
      else:
        print('Is the pre-filtering of old books done? (y/n)')
        inp = input()
        if inp == 'n':
          print('Please provide the directory where the separate language ' +
                'folders are or press enter to use default location ' +
                '(from the repo\'s root).')
          directory = input()
          if len(directory) > 1:
            pre_filter(self.condig, directory)
          else:
            pre_filter(self.config)
          extract(self.config)
        else:
          print('Are dialogs extracted from books? (y/n)')
          inp = input()
          if inp == 'n':
            print('Please provide the directory where the separate language ' +
                  'folders are or press enter to use default location ' +
                  '(from the repo\'s root).')
            directory = input()
            if len(directory) > 1:
              extract(self.condig, directory)
            else:
              extract(self.config)
          