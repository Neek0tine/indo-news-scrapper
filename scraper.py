from newsplease import NewsPlease
from bs4 import BeautifulSoup
import requests as r
import pandas as pd
import re

"""
"authors": [],
"date_download": null,
"date_modify": null,
"date_publish": "2017-07-17 17:03:00",
"description": "Russia has called on Ukraine to stick to the Minsk peace process [news-please will extract the whole text but in this example file we needed to cut off here because of copyright laws].",
"filename": "https%3A%2F%2Fwww.rt.com%2Fnews%2F203203-ukraine-russia-troops-border%2F.json",
"image_url": "https://img.rt.com/files/news/31/9c/30/00/canada-russia-troops-buildup-.si.jpg",
"language": "en",
"localpath": null,
"source_domain": "www.rt.com",
"maintext": "Russia has called on Ukraine to stick to the Minsk peace process [news-please will extract the whole text but in this example file we needed to cut off here because of copyright laws].",
"title": "Moscow to Kiev: Stick to Minsk ceasefire, stop making false \u2018invasion\u2019 claims",
"title_page": null,
"title_rss": null,
"url": "https://www.rt.com/news/203203-ukraine-russia-troops-border/"
"""

def detik_query(q='capres', p=5):
    tresult = []
    for _p in range(1, p+1):
        # qresult = r.get(f"https://www.detik.com/search/searchall?query={q}&siteid=3&sortby=time&page={_p}")
        qresult = r.get(f"https://www.detik.com/search/searchall?query={q}&siteid=3&sortby=time&sorttime=3&fromdatex=28/11/2023&todatex=28/12/2023&page={_p}")
        qsoup = BeautifulSoup(qresult.content, "html.parser")
        for a in qsoup.find_all('a', href=True): 
            _a = a['href']
            # print(_a)
            match = re.findall(r"/d-\d+/", _a)
            if match != []:
                tresult.append(_a)
    return tresult, q


def detik_get_from_query():
    l = detik_query()
    df = pd.DataFrame(columns=['title','main', 'source', 'date', 'url'])
    for i, _u in enumerate(l[0]):
        _article = NewsPlease.from_url(_u)
        _title = _article.title
        _main = _article.maintext
        _url = _article.url
        _date = _article.date_publish
        _source = _article.source_domain
        print(f"Exported [{i+1}/{len(l[0])}]")
        df.loc[i] = ([_title] + [_main] + [_source] + [_date] + [_url])
    df.to_csv(f"keyword_{l[1]}.csv", index=False, sep=';')
    print(f"File saved 'keyword_{l[1]}.csv'")


def tribun_query(q='pemilu'):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.chrome.service import Service
    import time
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    # options.add_argument("--disable-crash-reporter");
    # options.add_argument("--disable-extensions");
    # options.add_argument("--disable-in-process-stack-traces");
    # options.add_argument("--disable-logging");
    # options.add_argument("--disable-dev-shm-usage");
    # options.add_argument("--log-level=3");
    # options.add_argument("--output=/dev/null");
    driver_path = 'driver\chromedriver.exe'
    driver = webdriver.Chrome(service=Service(driver_path))
    

    # Initialize the WebDriver
# ----------------------------------------- URL VARIABLES ------------------------------------------------------
    driver.get('https://www.detik.com/')
    search_bar = driver.find_element(By.NAME, 'query')
    search_query = q
    search_bar.send_keys(search_query)
    search_bar.send_keys(Keys.RETURN)
    qresult = driver.page_source

    qsoup = BeautifulSoup(qresult, "html.parser")
# ----------------------------------------- PAGINATION VARIABLES ------------------------------------------------------
    # tribun
    # mydivs = qsoup.find("div", {"class": "gsc-cursor"})
    # print(mydivs)
    # max_page = int(mydivs.getText(' ').split(' ')[-1])
    # pages = range(1, max_page)

    # print(pages)
    
    # detoik
    # data = qsoup.find_all('div', class_='pagingtext_center')
    # a_class = data[0].find_all('a')
    # url_ = a_class[0].get('href')
    # print(url_)

    pages = range(1, 10)

    tresult = []
    for _p in pages:
        _p = int(_p) + 1
        print(_p)
        try:

            for a in qsoup.find_all('a', href=True): 
                _a = a['href']
                # print(_a)
# ----------------------------------------- FILTER VARIABLES ------------------------------------------------------
                # match = re.findall(r"tribunnews.com/\d+/\d+/\d+", _a)
                match = re.findall(r"/d-\d+/", _a)
                # match = re.findall(r"/\d+/\d+/\d+/\d+", _a)
                if match != []:
                    tresult.append(_a)


            time.sleep(5)
# ----------------------------------------- PAGINATION VARIABLES ------------------------------------------------------
            # tribun
            # WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"[aria-label='Page {_p}']"))).click()

            # detik kompas     
            if '&sortby=time&page=' in driver.current_url:
                driver.get(str(driver.current_url).replace(f'&sortby=time&page={_p-1}', f'&sortby=time&page={_p}'))

            elif '&sortby=time&page=' not in driver.current_url:
                driver.get(str(driver.current_url) + f'&sortby=time&page={_p}')

            # print(driver.current_url)

        except: 
            pass

        
    
    tresult = list(dict.fromkeys(tresult))
    print(tresult)

    df = pd.DataFrame(columns=['title','main', 'source', 'date', 'url'])
    for i, _u in enumerate(tresult):
        _article = NewsPlease.from_url(_u)
        _title = _article.title
        _main = _article.maintext
        _url = _article.url
        _source = _article.source_domain
        _date = _article.date_publish
        _domain = str(_source.split('.')[1])
        print(f"Exported [{i+1}/{len(tresult)}]")
        df.loc[i] = ([_title] + [_main] + [_source] + [_date] + [_url])
        _filename = f"raw_scrapped/{_domain}_keyword_{q}_.csv"

    df.to_csv(_filename, index=False, sep='~')
    print(f"File saved as {_filename}")

    



keywords = ['cawapres', 'capres', 'pemilu', 'anies', 'ganjar', 'gibran', 'imin', 'mahfud', 'prabowo']
# keywords = ['cawapres', 'pemilu', 'capres']
for key in keywords:
    tribun_query(key)
# if __name__ == "__main__":
    # detik_get_from_query()
    # tribun_query()