import logging
from bs4 import BeautifulSoup, Tag
from selenium import webdriver

from pipeline.scrapers.search_engine_scraper import SearchEngineScraper

def clean_url(elem: Tag) -> str:
    return elem.find('a').get('href')

class YahooScraper(SearchEngineScraper):
    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver, 'pipeline/scrapers/yahoo/config.yaml')


    def collect_links(self) -> list:
        self.soup = BeautifulSoup(self.driver.page_source, features='html.parser')
        links = list(map(clean_url, self.soup.findAll('h3', {'class': 'title ov-h'})))
        for link in links:
            logging.info('Found: ' + link)

        return links


    def load_next_page(self) -> bool:
        more_results_btn = self.soup.find('div', {'class': 'compPagination'})

        if more_results_btn is None:
            return False

        more_results_btn = more_results_btn.find('a', {'class', 'next'})

        if more_results_btn is None:
            return False
        
        self.driver.get(more_results_btn.get('href'))
        return True
