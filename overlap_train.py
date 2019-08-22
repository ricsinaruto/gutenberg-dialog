train_set = set()
with open('devSource.txt') as s:
  with open('devTarget.txt') as t:
    for source, target in zip(s, t):
      train_set.add(' '.join(source.split()) + ' '.join(target.split()))

with open('testSource.txt') as s:
  with open('testTarget.txt') as t:
    for source, target in zip(s, t):
      train_set.add(' '.join(source.split()) + ' '.join(target.split()))

overlap = 0
sources = open('curated_trainSource.txt', 'w')
targets = open('curated_trainTarget.txt', 'w')
with open('trainSource.txt') as s:
  with open('trainTarget.txt') as t:
    for i, (source, target) in enumerate(zip(s, t)):
      if ' '.join(source.split()) + ' '.join(target.split()) in train_set:
        overlap += 1
      else:
        sources.write(source)
        targets.write(target)

sources.close()
targets.close()

print(overlap / i)
