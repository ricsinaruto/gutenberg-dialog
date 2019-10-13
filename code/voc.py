with open('vocab.txt', 'w', encoding='utf-8') as out:
  with open('vocab_big.txt', encoding='utf-8') as f:
    for i, line in enumerate(f):
      if i < 100000:
        out.write(line.split('<SEP>')[0] + '\n')
