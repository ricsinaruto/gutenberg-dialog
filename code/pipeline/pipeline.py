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
        if (self.config.download or
            self.config.pre_filter or
            self.config.run_all) and\
                self.config.directory == os.path.join('data', 'filtered'):
            self.config.directory = os.path.join('data', 'raw')

        if self.config.run_all:
            print('Running entire pipeline.')
            download(self.config)
            pre_filter(self.config)
            extract(self.config)
            post_filter(self.config)
            create(self.config)
        else:
            if self.config.download:
                download(self.config)
            if self.config.pre_filter:
                pre_filter(self.config)
            if self.config.extract:
                extract(self.config)
            if self.config.post_filter:
                post_filter(self.config)
            if self.config.create_dataset:
                create(self.config)

        if not (self.config.download or self.config.pre_filter or
                self.config.extract or self.config.post_filter or
                self.config.create_dataset):
            print('No steps selected, please see help (-h) to specify them.')
