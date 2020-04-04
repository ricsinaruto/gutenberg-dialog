small_vocab = {}

with open('personachat.txt') as f:
  for line in f:
    small_vocab[line.strip('\n')] = 1

large_vocab = {}

with open('opensubtitles.txt') as f:
  for line in f:
    large_vocab[line.strip('\n')] = 1

diff_add = []
for word in small_vocab:
  if not large_vocab.get(word, 0):
    diff_add.append(word)

diff_discard = []
for word in large_vocab:
  if not small_vocab.get(word, 0):
    diff_discard.append(word)

vocab = list(large_vocab)
for word, new_word in zip(diff_discard[len(diff_discard) - len(diff_add):], diff_add):
  index = vocab.index(word)
  vocab[index] = new_word

with open('opensubtitles_personachat.txt', 'w') as f:
  for word in vocab:
    f.write(word + '\n')
