import os
import requests
import zipfile
from clint.textui import progress


for filename in os.listdir('robot'):
  if 'offset' in filename:
    with open('robot/' + filename) as f:
      for line in f:
        if '.zip' in line:
          segments = line.split('"http')
          for segment in segments:
            if '.zip' in segment:
              link = 'http' + segment.split('.zip')[0] + '.zip'
              data_stream = requests.get(link, stream=True)
              path = ''.join(link.split('/'))

              with open(path, 'wb') as file:
                total_length = int(data_stream.headers.get('content-length'))
                for chunk in progress.bar(data_stream.iter_content(chunk_size=1024),
                                          expected_size=total_length / 1024 + 1):
                  if chunk:
                    file.write(chunk)
                    file.flush()

              # Extract file.
              zip_file = zipfile.ZipFile(path, 'r')
              zip_file.extractall('texts')
              zip_file.close()
