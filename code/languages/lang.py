class Lang:
    def __init__(self, cfg):
        self.cfg = cfg
        self.dialogs = []

    def delimiters():
        raise NotImplementedError

    def process_line(self, paragraph_list, delimiter):
        raise NotImplementedError

    def clean_line(self, line):
        raise NotImplementedError
