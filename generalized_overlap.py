from collections import Counter


threshold = 0.1

train_set = []
with open('trainSource.txt') as s:
  with open('trainTarget.txt') as t:
    for source, target in zip(s, t):
      sCounter = Counter(source.split())
      tCounter = Counter(target.split())
      train_set.append((sCounter, tCounter, sum(list(sCounter.values())), sum(list(tCounter.values()))))

overlap = 0
sources = open('curated_testSource.txt', 'w')
targets = open('curated_testTarget.txt', 'w')
responses = open('curated_testResponses.txt', 'w')
with open('testSource.txt') as s:
  with open('testTarget.txt') as t:
    with open('test_set_35k.txt') as r:
      for i, (source, target, response) in enumerate(zip(s, t, r)):
        print(i)
        sCounter = Counter(source.split())
        tCounter = Counter(target.split())
        sSum = sum([v for v in sCounter.values()])
        tSum = sum([v for v in tCounter.values()])
        bad_example = False
        for example in train_set:
          source_dif = sum(list((example[0] - sCounter).values())) + sum(list((sCounter - example[0]).values()))
          target_dif = sum(list((example[1] - tCounter).values())) + sum(list((tCounter - example[1]).values()))
          total_s = example[2] + sSum
          total_t = example[3] + tSum

          if source_dif / total_s < 0.1 and target_dif / total_t < 0.1:
            print(source)
            print(example[0])
            print('\n')
            overlap += 1
            bad_example = True
            break
        if not bad_example:
          sources.write(source)
          targets.write(target)
          responses.write(response)

sources.close()
targets.close()
responses.close()

print(overlap / i)
