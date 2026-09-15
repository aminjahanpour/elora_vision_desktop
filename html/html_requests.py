import requests


url = "https://requests.readthedocs.io/"

chunks_dump_file_name = 'chunks_dump.html'
urllib_file_name  = 'urllib.html'
res_normal = requests.get(url)


with open(chunks_dump_file_name, 'wb') as fd:
    for chunk in res_normal.iter_content(chunk_size=128):
        fd.write(chunk)



sdf=4



import urllib.request
urllib.request.urlretrieve(url, urllib_file_name)
