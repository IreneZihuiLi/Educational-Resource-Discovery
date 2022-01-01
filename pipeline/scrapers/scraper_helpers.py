import os
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


def init_web_driver(headless: bool, op_sys: str, download_dir: str = None) -> webdriver.Chrome:

    def populate_options(options):
        if headless:
            options.add_argument('--headless')
        
        if download_dir is not None:
            options.add_argument('--no-sandbox')
            options.add_experimental_option('prefs', {
                'download.default_directory': os.path.abspath(download_dir),
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing_for_trusted_sources_enabled': False,
                'safebrowsing.enabled': False
            })

    driver_dir = 'pipeline/scrapers/drivers'
    driver = None

    driver_dir = os.path.join(driver_dir, op_sys)

    options = ChromeOptions()
    populate_options(options)

    driver = webdriver.Chrome(os.path.join(driver_dir, 'chromedriver'), options=options)

    return driver


def wait_for_page_load(driver: webdriver.Chrome):
    while driver.execute_script('return document.readyState') != 'complete':
        pass


from pipeline.scrapers.search_engine_scraper import SearchEngineScraper
from pipeline.scrapers.duck_duck_go.duck_duck_go_scraper import DuckDuckGoScraper
from pipeline.scrapers.bing.bing_scraper import BingScraper
from pipeline.scrapers.yahoo.yahoo_scraper import YahooScraper

def build_scraper(args: argparse.Namespace) -> SearchEngineScraper:
    driver = init_web_driver(not args.visual, args.operating_system)

    scraper = None

    if args.searchengine == 'DuckDuckGo':
        scraper = DuckDuckGoScraper(driver)
    elif args.searchengine == 'Bing':
        scraper = BingScraper(driver)
    else:
        scraper = YahooScraper(driver)

    return scraper
