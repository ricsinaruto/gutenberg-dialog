output = open('vocab.chatbot', 'w')

long_vocab = []
with open('vocab.chatbot.65536') as f:
  for line in f:
    long_vocab.append(line)

diff = []
with open('vocab.chatbot.16384') as f:
  for line in f:
    if line not in long_vocab:
      diff.append(line)

print(len(diff))
long_vocab = long_vocab[:len(long_vocab) - len(diff)]
long_vocab.extend(diff)
output.write(''.join(long_vocab))