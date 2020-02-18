#from pipeline.download import download
from pipeline.pre_filter import pre_filter
from pipeline.dialog_extractor import extract
from pipeline.post_filter import post_filter
from pipeline.create_dataset import create


class Pipeline:
  def __init__(self, config):
    self.config = config
    self.auto = config.auto

  def directory(self):
    print('Please provide the directory where the separate language ' +
          'folders are or press enter to use default location ' +
          '(from the repo\'s root).')
    return input()

  def run(self):
    if self.auto:
      print('You have selected the auto mode, the program will ' +
            'automatically run through the steps and build the dataset.')
      #download(self.config)
    else:
      print('You have selected the pipeline mode, the program will now step ' +
            'you through building the dataset.')
      print('Have you downloaded the data? (y/n)')
      inp = input()
      if inp == 'n':
        pass
        #download(self.config)
      else:
        print('Is the pre-filtering of old books done? (y/n)')
        inp = input()
        if inp == 'n':
          directory = self.directory()
          if len(directory) > 1:
            pre_filter(self.config, directory)
          else:
            pre_filter(self.config)
        else:
          print('Are dialogs extracted from books? (y/n)')
          inp = input()
          if inp == 'n':
            directory = self.directory()
            if len(directory) > 1:
              extract(self.config, directory)
            else:
              extract(self.config)
          else:
            print('Is post-filtering on the dialogs done? (y/n)')
            inp = input()
            if inp == 'n':
              directory = self.directory()
              if len(directory) > 1:
                post_filter(self.config, directory)
              else:
                post_filter(self.config)
            else:
              directory = self.directory()
              if len(directory) > 1:
                create(self.config, directory)
              else:
                create(self.config)
