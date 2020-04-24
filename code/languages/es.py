import re
import unicodedata

from languages.it import It


class Es(It):
    def clean_line(self, line):
        line = re.sub(' \' ', '\'', line)
        line = unicodedata.normalize('NFKD', line)
        line = re.sub('[.]', ' . ', line)
        line = re.sub('[?]', ' ? ', line)
        line = re.sub('[!]', ' ! ', line)
        line = re.sub('[-]', ' - ', line)
        line = re.sub('["]', ' " ', line)
        line = re.sub('[:]', ' : ', line)
        line = re.sub('[,]', ' , ', line)

        line = re.sub('[¿]', ' ¿ ', line)
        line = re.sub('[¡]', ' ¡ ', line)

        return line
