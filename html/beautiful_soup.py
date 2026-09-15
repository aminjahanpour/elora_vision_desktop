import requests
import re
from bs4 import BeautifulSoup



url = "https://requests.readthedocs.io/"


chunks_dump_file_name = 'chunks_dump.html'
urllib_file_name  = 'urllib.html'
res_normal = requests.get(url)


with open(chunks_dump_file_name, 'wb') as fd:
    for chunk in res_normal.iter_content(chunk_size=128):
        fd.write(chunk)

with open(chunks_dump_file_name, 'rb') as fd:
    payload = fd.read()


soup = BeautifulSoup(payload, 'html.parser')

text_only = soup.get_text()

print("\nImages")

img_tags = soup.find_all('img')
urls = [img['src'] for img in img_tags]
for url in urls:
    serach_result = re.search(r'/([\w_-]+[.](jpg|gif|png|svg))$', url)
    if (serach_result is not None):
        print (url)
        with open(os.path.join(folder_full_path, serach_result.group(1))  , 'wb') as f:
        #with open(main_folder+filename.group(1), 'wb') as f:
            if 'http' not in url:
                # sometimes an image source can be relative
                # if it is provide the base url which also happens
                # to be the site variable atm.
                url = '{}{}'.format(site, url)
            response = requests.get(url)
            f.write(response.content)




sdf = 3