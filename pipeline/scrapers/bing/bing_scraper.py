import logging
from bs4 import BeautifulSoup
from selenium import webdriver

from pipeline.scrapers.search_engine_scraper import SearchEngineScraper

class BingScraper(SearchEngineScraper):
    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver, 'pipeline/scrapers/bing/config.yaml')


    def collect_links(self) -> list:
        self.soup = BeautifulSoup(self.driver.page_source, features='html.parser')
        links = list(map(lambda elem: elem.find('a').get('href'), self.soup.findAll('li', {'class': 'b_algo'})))
        for link in links:
            logging.info('Found: ' + link)
        return links


    def load_next_page(self) -> bool:
        more_results_btn = self.soup.find('a', {'class': 'sb_pagN sb_pagN_bp b_widePag sb_bp'})

        if more_results_btn is None:
            return False
        
        self.driver.get(self.domain + more_results_btn.get('href'))
        return True
