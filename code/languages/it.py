from languages import fr


def delimiters():
  return fr.delimiters()


def process_file(cfg, dialogs, paragraph_list, filename, delimiter):
  fr.process_file(cfg, dialogs, paragraph_list, filename, delimiter)


def clean_line(line):
  return fr.clean_line(line)
