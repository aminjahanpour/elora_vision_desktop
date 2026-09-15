from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

site = 'https://requests.readthedocs.io'
dr = webdriver.Chrome()

dr.get(site)
try:
    element = WebDriverWait(dr, 20, 0.5).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "span1"))
    )
except:
    print("Wait a bit more")
    time.sleep(5)

text = dr.page_source
soup = BeautifulSoup(text,"lxml")
imgs = soup.find_all('img')
print(imgs)

dr.close()