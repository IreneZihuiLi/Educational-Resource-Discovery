import argparse
import logging

from pipeline.downloader.download_manager import DownloadManager
from pipeline.misc.util import log_args

from pipeline.stages import parse_seed_documents, get_key_phrases, web_crawl, parse_resource_documents, output_parse_results

DEFAULT_NUM_KEYWORDS = 5
DEFAULT_NUM_SEARCH_RESULTS = 5


def collect_pipeline_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Pipeline', add_help=False)

    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')

    required.add_argument('-u','--uris', nargs='+', help='List of space-delimited file uris for document seeding (i.e. file paths and/or internet urls).', default=list())
    required.add_argument('-se','--searchengine', help='Search engine to query.', choices=['DuckDuckGo', 'Bing', 'Yahoo'])
    required.add_argument('-csv', '--csv-dir', help='Folder to dump resultant csv feature summaries.', required=True)
    required.add_argument('-txt', '--txt-dir', help='Folder to dump resultant free text from the documents collected.', required=True)

    optional.add_argument('-lf','--list-file', help='Path to csv file where to write the list of urls collected from the search engine.', type=str)
    optional.add_argument('-sq','--start_query', help='Query start index within query list file.', type=int, default=0)
    optional.add_argument('-eq','--end-query', help='Query end index within query list file.', type=int, default=-1)
    optional.add_argument('-k','--keyphrases', nargs='+', help='Explicit list of space-delimited seeding keyphrases, each enclosed in quotes.', default=list())
    optional.add_argument('-kf','--keyphrases-file', help='Path to a file containing a list of newline-separated query strings.', type=str)
    optional.add_argument('-of', '--outfile', help='Path to output log file.')
    optional.add_argument('-ver','--verbose', action='store_true', help='Specify whether standard logging should occur (at an INFO level).')
    optional.add_argument('-ex','--extract', help='Extraction strategy to use.', choices=['BertNer', 'GenSim', 'KeyBert', 'Rake', 'Rakun', 'Yake'])
    optional.add_argument('-c','--counts', nargs='+', help=f"Space-delimited list consisting of the number of keywords to extract from each document, defaults to {DEFAULT_NUM_KEYWORDS} for each document.", default=list())
    optional.add_argument('-sr','--searchresults', help=f"Number of results to scrape for each keyword, defaulted to {DEFAULT_NUM_SEARCH_RESULTS}.", type=int, default=DEFAULT_NUM_SEARCH_RESULTS)
    optional.add_argument('-os','--operating-system', help='Specify the operating system you are on.', type=str, choices=['macos', 'linux', 'windows'], default='linux')
    optional.add_argument('-vi','--visual', action='store_true', help='Set to True if you want to see your queries live, in Google Chrome. Default is headless mode.')
    optional.add_argument('-d', '--domain', help='Specify the domain of the query range within the query file defaulting to \"*\".', type=str, default='.*')
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit.')

    args = parser.parse_args()

    if args.uris and not args.extract:
        parser.error('Gave seeding documents but did not specify a keyphrase extraction method.')

    if not args.keyphrases and not args.keyphrases_file:
        if not args.uris:
            parser.error('Must specify at least one key phrase or one seeding document to kick off the pipeline.')
        args.keyphrases = list()

    args.counts = [int(count) for count in args.counts]
    args.counts += [DEFAULT_NUM_KEYWORDS] * (max(0, len(args.uris) - len(args.counts)))
    
    return args


def set_up_logger(log_fname: str, verbosity: bool) -> None:
    log_level = logging.INFO

    if not verbosity:
        log_level = logging.ERROR

    if log_fname is None:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        logger = logging.getLogger()
        logger.handlers = list()

        fh = logging.FileHandler(log_fname)
        fh.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(formatter)

        logger.addHandler(fh)


def main() -> int:

    args = collect_pipeline_args()

    set_up_logger(args.outfile, args.verbose is not None)

    log_args(args)

    with DownloadManager() as dm:
        parsers = parse_seed_documents(args, dm)

        key_phrases = get_key_phrases(args, parsers)

        online_resources = web_crawl(args, key_phrases)

        parsers = parse_resource_documents(args, online_resources, dm)

        output_parse_results(args, parsers)

    logging.info('ALL DONE :).')

    return 0
    

if __name__ == '__main__':
    exit(main())
