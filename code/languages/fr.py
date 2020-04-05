from languages import hu


def delimiters():
  return {'--': hu.delimiters()['–']}


def process_file(cfg, dialogs, paragraph_list, filename, delimiter):
  hu.process_file(cfg, dialogs, paragraph_list, filename, delimiter)


def clean_line(line):
  return hu.clean_line(line)
