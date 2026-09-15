from bs4 import BeautifulSoup
from pip._vendor import requests
import os
import shutil
import re
from bs4 import BeautifulSoup
import uuid
import toolkit
import os
import zlib

rnd_str = 'test' # uuid.uuid4().hex
folder_name= "download_" + rnd_str
main_full_path = os.path.join(toolkit.root_path, folder_name)
image_folder_path = os.path.join(main_full_path, 'images')

html_file_name = os.path.join(main_full_path, "page.html")
html_gzip_file_name = os.path.join(main_full_path, "page.html.gzip")
text_file_name = os.path.join(main_full_path, "text.txt")
text_gzip_file_name = os.path.join(main_full_path, "text.txt.gzip")

if os.path.exists(main_full_path):
    shutil.rmtree(main_full_path)
os.mkdir(main_full_path)
os.mkdir(image_folder_path)


site = 'https://www.parniatech.com/'
site = 'https://en.wikipedia.org/wiki/Universally_unique_identifier'
response = requests.get(site)




# html

with open(html_file_name, 'wb') as fd:
    for chunk in response.iter_content(chunk_size=128):
        fd.write(chunk)

with open(html_file_name, 'rb') as fd:
    payload = fd.read()

with open(html_gzip_file_name, 'wb') as fd:
    fd.write(zlib.compress(payload))



soup = BeautifulSoup(payload, 'html.parser')



# text only
soup_text = soup.get_text()
with open(text_file_name, 'wb') as fd:
    fd.write(soup_text.encode())


with open(text_file_name, 'rb') as fd:
    text_content = fd.read()


with open(text_gzip_file_name, 'wb') as fd:
    fd.write(zlib.compress(text_content))





print(f'target dir: {main_full_path}\n')






print("\nImages")

img_tags = soup.find_all('img')
urls = [img['src'] for img in img_tags]
for url in urls:
    serach_result = re.search(r'/([\w_-]+[.](jpg|gif|png|svg))$', url)
    if (serach_result is not None):
        print (url)
        with open(os.path.join(image_folder_path, serach_result.group(1))  , 'wb') as f:
        #with open(main_folder+filename.group(1), 'wb') as f:
            if 'http' not in url:
                # sometimes an image source can be relative
                # if it is provide the base url which also happens
                # to be the site variable atm.
                url = '{}{}'.format(site, url)
            response = requests.get(url)
            f.write(response.content)


