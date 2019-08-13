from collections import Counter


vocab = Counter()
with open('sources.txt') as f:
	for line in f:
		for word in line.split():
			if word in vocab:
				vocab[word]+=1
			else:
				vocab[word]=1

with open('vocab.txt', 'w') as f:
	f.write('\n'.join([k[0] for k in vocab.most_common(65536 - 3)]))