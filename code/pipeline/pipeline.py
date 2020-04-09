import os

from pipeline.download import download
from pipeline.pre_filter import pre_filter
from pipeline.dialog_extractor import extract
from pipeline.post_filter import post_filter
from pipeline.create_dataset import create


class Pipeline:
    def __init__(self, config):
        self.config = config

        # Convert language codes to list.
        if isinstance(self.config.languages, str):
            self.config.languages = self.config.languages.split(',')

    def run(self):
        # Pre-set directory.
        if (self.config.download or self.config.pre_filter) and\
                self.config.directory == os.path.join('data', 'filtered'):
            self.config.directory = os.path.join('data', 'raw')

        start = False
        if self.config.download:
            start = True
            download(self.config)
        if self.config.pre_filter:
            start = True
            pre_filter(self.config)
        if self.config.extract:
            start = True
            extract(self.config)
        if self.config.post_filter:
            start = True
            post_filter(self.config)
        if self.config.create_dataset:
            start = True
            create(self.config)

        if not start:
            if self.config.directory == os.path.join('data', 'filtered'):
                self.config.directory = os.path.join('data', 'raw')
            print('No steps selected, running entire pipeline.')
            download(self.config)
            pre_filter(self.config)
            extract(self.config)
            post_filter(self.config)
            create(self.config)
