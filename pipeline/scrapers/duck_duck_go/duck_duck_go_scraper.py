import logging
from bs4 import BeautifulSoup
from selenium import webdriver

from pipeline.scrapers.search_engine_scraper import SearchEngineScraper
from pipeline.scrapers.scraper_helpers import wait_for_page_load

class DuckDuckGoScraper(SearchEngineScraper):
    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver, 'pipeline/scrapers/duck_duck_go/config.yaml')

    def load_next_page(self) -> bool:
        more_results_btn = self.driver.find_element_by_link_text('More Results')

        if more_results_btn is None:
            return False
        
        more_results_btn.click()
        return True

    def collect_links(self) -> list:
        soup = BeautifulSoup(self.driver.page_source, features='html.parser')
        links = list(map(lambda elem: elem.get('href'), soup.findAll('a', {'class': 'result__url js-result-extras-url'})))
        for link in links:
            logging.info('Found: ' + link)
        return links

    def query(self, query_str: str, num_results: int, kp_id: int, domain: str) -> None:
        links_list = list()
        attempts = 0

        while True:
            try:
                self.look_up(query_str)

                links_list = list()

                while True:
                    wait_for_page_load(self.driver)

                    all_links = self.collect_links()

                    links_list += self.clean_url_list(all_links[-min(self.results_per_page, len(all_links)):])

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
