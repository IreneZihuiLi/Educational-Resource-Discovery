import logging
import argparse
import re

from pipeline.downloader.download_manager import DownloadManager
from pipeline.misc.util import parse_key_phrase_file, dump_links_to_csv
from pipeline.parsers.parser_helpers import build_parsers
from pipeline.scrapers.scraper_helpers import build_scraper
from pipeline.extracts.extract_helpers import get_key_phrase_extract, extract_key_phrases


def parse_seed_documents(args: argparse.Namespace, download_manager: DownloadManager) -> list:
    logging.info('Downloading and Preparing Seed Documents')
    download_manager.download_batch(args.uris, force_download=False)
    parsers = build_parsers([('null_fname', uri, uri) for uri in args.uris])
    logging.info('\n\n')
    return parsers

def get_key_phrases(args: argparse.Namespace, parsers: list) -> list:
    logging.info('Extracting Keywords from Documents')

    if args.keyphrases_file is not None:
        parse_key_phrase_file(args)

    key_phrases = [args.keyphrases]

    logging.info('Explicit Keyphrases Provided')
    for key_phrase in key_phrases[0]:
        logging.info(key_phrase)

    if len(parsers) > 1:
        logging.info('Using extract: ' + args.extract)

        extract = get_key_phrase_extract(args.extract)
        
        for count, parser in zip(args.counts, parsers):
            key_phrases.append(extract_key_phrases(parser, extract, count))

        for i, keyphrase_list in enumerate(key_phrases[1:]):
            logging.info('Keyphrases Extracted From: ' + parsers[i - 1].get_fname())
            for key_phrase in keyphrase_list:
                logging.info(key_phrase)

    logging.info('\n\n')

    return key_phrases

def web_crawl(args: argparse.Namespace, key_phrases: list) -> dict:
    logging.info('Scraping the Web')
    scraper = build_scraper(args)

    kp_id = args.start_query

    for group_no, key_phrase_group in enumerate(key_phrases):
        for key_no, keyphrase in enumerate(key_phrase_group):
            logging.info('Scraping for keyphrase: ' + keyphrase)
            num_results = args.searchresults
            domain = 'none'
            if group_no == 0:
                num_results = args.keyphrase_counts[key_no]
                domain = args.keyphrase_domains[key_no]

            scraper.query(keyphrase, num_results, kp_id, domain)
            kp_id += 1

    scraper.driver.quit()

    resources = scraper.get_resources()

    logging.info('\n\nOverall Resources Scraped')

    for keyphrase, search_results in resources.items():
        logging.info('Keyphrase: ' + keyphrase)
        for search_result in search_results:
            logging.info('%16s: %32s' % search_result)

    logging.info('\n\n')

    return resources

def parse_resource_documents(args: argparse.Namespace, online_resources: dict, download_manager: DownloadManager) -> dict:
    logging.info('Downloading and Preparing Online Resources')
    parsers = dict()
    for keyphrase, online_resource_list in online_resources.items():
        logging.info('Keyphrase: ' + keyphrase)
        uris = download_manager.download_batch([link for _, link in online_resource_list], force_download=True)
        parsers[keyphrase] = build_parsers([(*online_resource_list[i], uris[i]) for i in range(len(uris)) if uris[i] is not None],
                                           args.csv_dir, args.txt_dir, keyphrase)

    logging.info('\n\n')

    return parsers

def output_parse_results(args: argparse.Namespace, parsers: dict) -> None:
    logging.info('Outputting Parsed Results')
    list_file_info = list()

    for keyphrase, parsers in parsers.items():
        logging.info('Keyphrase: ' + keyphrase)
        for parser in parsers:
            if parser is not None:
                if parser.is_usable():
                    logging.info(f'Writing to {parser.get_fname()}.{{csv, txt}}')

                    parser.dump_to_csv()
                    parser.dump_to_txt()

                    if args.list_file:
                        list_file_info.append(parser.get_annotation_info())
                else:
                    logging.info(f'Unusable parser for {parser.get_fname()}')

    if args.list_file:
        dump_links_to_csv(args.list_file, list_file_info)

    logging.info('\n\n')
