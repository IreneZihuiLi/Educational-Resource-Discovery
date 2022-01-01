import argparse

from pipeline.misc.util import dump_args_to_csv
from pipeline.scrapers.scraper_helpers import build_scraper

CSV_FLUSH_INTERVAL = 10
DEFAULT_NUM_SEARCH_RESULTS = 5


def collect_scraper_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Webcrawler for collecting search results on different search engines.', add_help=False)
    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')
    
    required.add_argument('-ql','--querylist', nargs='+', help='List of space-delimited queries.', required=True)
    required.add_argument('-se','--searchengine', help='Search engine to query.', choices=['DuckDuckGo', 'Bing', 'Yahoo'], required=True)
    required.add_argument('-of', '--outfile', help='Path to CSV output file.', required=True)

    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit.')
    optional.add_argument('-qc','--querycount', nargs='+', help='List of space-delimited queries. Default is ' + str(DEFAULT_NUM_SEARCH_RESULTS) + ' for each unspecified query.', default=list())
    optional.add_argument('-vi','--visual', action='store_true', help='Set to True if you want to see your queries live, in Google Chrome. Default is headless mode.')
    optional.add_argument('-mos','--macos', action='store_true', help='Specify if you are on MacOS. If unspecified, the webcrawler will run on Linux.')

    args = parser.parse_args()

    if len(args.querycount) < len(args.querylist):
        args.querycount += [DEFAULT_NUM_SEARCH_RESULTS for _ in range(len(args.querylist) - len(args.querycount))]

    return args


def main() -> int:
    args = collect_scraper_args()
    dump_args_to_csv(args)

    scraper = build_scraper(args)

    for i in range(len(args.querylist)):
        scraper.query(args.querylist[i], int(args.querycount[i]))

        if i % CSV_FLUSH_INTERVAL == CSV_FLUSH_INTERVAL - 1:
            scraper.outputToCsv()

    scraper.driver.quit()
    scraper.outputToCsv()

    return 0

if __name__ == '__main__':
    exit(main())
