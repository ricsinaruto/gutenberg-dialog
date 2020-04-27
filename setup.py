import os


if not os.path.exists('data'):
    os.mkdir('data')
if not os.path.exists('data/raw'):
    os.mkdir('data/raw')

print('Installing requirements...')
os.system('pip install --no-deps gutenberg')
os.system('pip install -r requirements.txt')
