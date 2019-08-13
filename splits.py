train = open('trainTargets.txt', 'w')
dev = open('devTarget.txt', 'w')


with open('trainTarget.txt') as f:
	for i, line in enumerate(f):
		if i < 670000:
			train.write(line)
		else:
			dev.write(line)
