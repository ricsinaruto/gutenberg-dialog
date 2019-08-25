import re


# Clean a line with some re rules.
def clean_line(line):
  '''
  Params:
    :line: Line to be processed and returned.
  '''

  # 2 functions for more complex replacing.
  def replace(matchobj):
    return re.sub("'", " '", str(matchobj.group(0)))

  def replace_null(matchobj):
    return re.sub("'", '', str(matchobj.group(0)))

  # Keep some special tokens.
  line = re.sub("[^a-z .?!'0-9]", '', line)
  line = re.sub('[.]', ' . ', line)
  line = re.sub('[?]', ' ? ', line)
  line = re.sub('[!]', ' ! ', line)

  # Take care of apostrophes.
  line = re.sub("[ ]'[ ]", ' ', line)
  line = re.sub(" '[a-z]", replace_null, line)
  line = re.sub("n't", " n't", line)
  line = re.sub("[^ n]'[^ t]", replace, line)

  return line


source = open('sources.txt', 'w')
target = open('targets.txt', 'w')

dialogs = [[]]
with open('dialogs.txt') as f:
  for line in f:
    if line == '\n':
      dialogs.append([])
    else:
      line = line.split('.txt:  ')[1]
      dialogs[-1].append(clean_line(line.lower()) + '\n')

for d in dialogs:
  for i, u in enumerate(d[:-1]):
    source.write(u)
    target.write(d[i + 1])

source.close()
target.close()
