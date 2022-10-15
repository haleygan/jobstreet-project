from unittest import result
from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import pandas as pd
import time
import math
import json
import re

driver = Chrome()
time.sleep(2)
url = 'https://www.jobstreet.com.my/en/job-search/job-vacancy.php?createdAt=1d&sort=createdAt'


def get_page_number():
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_quantity = soup.find("span", {"class": "sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _1d0g9qk4 _18qlyvc8"}).text
    quantity_per_page = int(job_quantity.split()[0].split('-')[1])
    # total_quantity = int(job_quantity.split()[-2].replace(',',''))
    total_quantity = 30
    pages = math.ceil(total_quantity / quantity_per_page)
    return pages


def job_page_scraper(job_url):

    driver.get(job_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    scripts = soup.find_all("script")
    for script in scripts:
        if script.contents:
            txt = script.contents[0].strip()
            if 'window.REDUX_STATE = ' in txt:
                jsonStr = script.contents[0].strip()
                jsonStr = jsonStr.split('window.REDUX_STATE = ')[1].strip()
                jsonStr = jsonStr.rstrip(jsonStr[-1])
                jsonObj = json.loads(jsonStr)

    job = jsonObj['details']
    job_id = job['id']
    posted_at = job['header']['postedAt']

    return [job_id, posted_at, job]


def page_crawler():
    pages = get_page_number()
    job_urls = []

    for n in range(pages):
        print(f'Loading page {n+1}...')
        page_url = f'https://www.jobstreet.com.my/en/job-search/job-vacancy.php?createdAt=1d&pg={n+1}&sort=createdAt'
        driver.get(page_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.find_all('h1',{'class':'sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc3 _18qlyvca'})
        for card in cards:
            card_link = card.find('a')['href'].strip().split('?', 1)[0]
            job_url = 'https://www.jobstreet.com.my' + card_link
            job_urls.append(job_url)
    
    jobs = []

    for job_url in job_urls:
        jobs.append(job_page_scraper(job_url))
        
    result_df = pd.DataFrame(jobs, columns = ['job_id', 'posted_at', 'job_json'])
    return result_df


def main():
    dfs = []
    new_rows = page_crawler()
    dfs.append(new_rows)

    pd.concat(dfs).to_csv("job_postings_results.csv")


if __name__ == '__main__':
	main()

