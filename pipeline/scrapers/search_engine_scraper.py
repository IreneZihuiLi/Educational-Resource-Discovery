import abc
import yaml
import logging
import requests
from ordered_set import OrderedSet
import pandas as pd
from selenium import webdriver

from pipeline.scrapers.scraper_helpers import wait_for_page_load

class SearchEngineScraper(metaclass=abc.ABCMeta):
    MAX_ATTEMPTS = 3
    MAX_URL_LENGTH = 200
    URL_TIMEOUT = 2

    @abc.abstractmethod
    def load_next_page(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def collect_links(self, html: str) -> list:
        raise NotImplementedError

    def __init__(self, driver: webdriver.Chrome, yaml_path: str):
        self.driver = driver
        self.results_df = pd.DataFrame(columns=['Query', 'Rank', 'Link'])
        self.urls = dict()

        with open(yaml_path) as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)

            for attr_name, attr_value in cfg['params'].items():
                setattr(self, attr_name, attr_value)

    def __str__(self):
        return str(self.results_df)

    def clean_url_list(self, url_list: list) -> list:
        good_urls = list()

        for url in url_list:
            try:
                if requests.head(url, timeout=self.URL_TIMEOUT).status_code == 200:
                    good_urls.append(url)
            except:
                logging.info(f'{url} did not return a STATUS 200 within {self.URL_TIMEOUT} seconds, will skip it.')

        return good_urls

    def look_up(self, query_str: str) -> None:
        logging.info('Searching up ' + query_str)
        self.driver.get(self.domain)
        input_element = self.driver.find_element_by_name(self.search_bar_name)
        input_element.send_keys(query_str)
        input_element.submit()

    def get_ftype_from_query(self, query_str: str) -> str:
        ftype = 'html'
        tokens = query_str.split()
        for token in tokens:
            if token.startswith('filetype'):
                found = token.rfind('.')
                if found == -1:
                    found = token.rfind(':')
                ftype = token[found + 1:]
                break
        return ftype

    def append_to_csv(self, query_str: str, links_list: list) -> None:
        for i in range(len(links_list)):
            self.results_df = self.results_df.append({self.results_df.columns[0]: query_str,
                                                      self.results_df.columns[1]: str(i),
                                                      self.results_df.columns[2]: links_list[i]}, 
                                                      ignore_index=True)

    def save_search_results(self, query_str: str, kp_id: int, domain: str, links_list: list) -> None:
        self.urls[query_str] = [(f'{domain}.{kp_id}.{i}.{self.get_ftype_from_query(query_str)}', link)
                                for i, link in enumerate(links_list)]

    def query(self, query_str: str, num_results: int, kp_id: int, domain: str) -> None:
        links_list = list()
        attempts = 0

        while True:
            try:
                self.look_up(query_str)

                while True:
                    wait_for_page_load(self.driver)
                    links_list += self.clean_url_list(self.collect_links())
                    links_list = list(OrderedSet(links_list))

                    if len(links_list) >= num_results or not self.load_next_page():
                        break

                    logging.info('Loaded next page')

                links_list = list(filter(lambda link: len(link) <= self.MAX_URL_LENGTH, links_list))[:min(num_results, len(links_list))]

            except Exception as e:
                if attempts == self.MAX_ATTEMPTS:
                    break

                logging.error(str(e))

                attempts += 1
                continue

            break

        self.save_search_results(query_str, kp_id, domain, links_list)

    def get_resources(self) -> dict:
        return self.urls
