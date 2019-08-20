train_set = set()
with open('personachat/trainSource.txt') as s:
  with open('personachat/trainTarget.txt') as t:
    for source, target in zip(s, t):
      train_set.add(' '.join(source.split()) + ' '.join(target.split()))

overlap = 0
sources = open('personachat/curated_testSource.txt', 'w')
targets = open('personachat/curated_testTarget.txt', 'w')
responses = open('personachat/curated_testResponses.txt', 'w')
with open('personachat/testSource.txt') as s:
  with open('personachat/testTarget.txt') as t:
    with open('personachat/testTarget.txt') as r:
      for i, (source, target, response) in enumerate(zip(s, t, r)):
        if ' '.join(source.split()) + ' '.join(target.split()) in train_set:
          overlap += 1
        else:
          sources.write(source)
          targets.write(target)
          responses.write(response)

sources.close()
targets.close()
responses.close()

print(overlap / i)