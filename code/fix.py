

with open('dialogs_clean_fixed.txt', 'w', encoding='utf-8') as out:
  with open('dialogs_clean.txt', encoding='utf-8') as f:
    count = 0
    for line in f:
      if line != '\n':
        out.write(line)
      else:
        if count == 0:
          out.write(line)
          count += 1
        else:
          count = 0
