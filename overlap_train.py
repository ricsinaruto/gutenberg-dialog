train_set = set()
directory = 'Cornell/'
with open(directory + 'devSource.txt') as s:
  with open(directory + 'devTarget.txt') as t:
    for source, target in zip(s, t):
      train_set.add(' '.join(source.split()) + ' '.join(target.split()))

with open(directory + 'testSource.txt') as s:
  with open(directory + 'testTarget.txt') as t:
    for source, target in zip(s, t):
      train_set.add(' '.join(source.split()) + ' '.join(target.split()))

overlap = 0
sources = open(directory + 'curated_trainSource.txt', 'w')
targets = open(directory + 'curated_trainTarget.txt', 'w')
with open(directory + 'trainSource.txt') as s:
  with open(directory + 'trainTarget.txt') as t:
    for i, (source, target) in enumerate(zip(s, t)):
      if ' '.join(source.split()) + ' '.join(target.split()) in train_set:
        overlap += 1
      else:
        sources.write(source)
        targets.write(target)

sources.close()
targets.close()

print(overlap / i)
