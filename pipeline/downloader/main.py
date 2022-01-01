import os
import sys
import argparse
import logging
import shutil
from contextlib import contextmanager

from pipeline.downloader.multithreaded_downloader import download_batch_multithreaded
from pipeline.parsers.parser_helpers import build_parsers


def collect_downloader_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Downloader', add_help=False)

    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')

    required.add_argument('-csv','--csv-path', help='Path to csv file containing the list of urls for download.', type=str, required=True)
    required.add_argument('-dp','--data-path', help='Path to folder where the outputted free text will be written to.', type=str, required=True)

    optional.add_argument('-col','--col-no', help='0-indexed column number in the csv file which has the links, defaulted to column 0.', type=int, default=0)
    optional.add_argument('-j','--jobs', help='Number of threads for downloading, defaults to 0.', type=int, default=1)

    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit.')
    
    return parser.parse_args()

def extract_urls_from_csv(csv_path: str, col_no: int) -> list:
    try:
        with open(csv_path, 'r') as f:
            urls = list()
            is_col_titles = True
            for line in f:
                if not is_col_titles:
                    cols = line.split(',')
                    urls.append(cols[col_no].strip())
                is_col_titles = False
            
            return urls

    except IndexError:
        logging.error(f'Provided column index {col_no} indexes beyond the number of columns in the provided csv: {csv_path}.')
        exit(1)
    except:
        logging.error(f'Could not open csv path: {csv_path}.')
        exit(1)

@contextmanager
def download_cleanup(dl_path: str):
    try:
        os.mkdir(dl_path)
        yield
    finally:
        shutil.rmtree(dl_path)


def main() -> int:
    args = collect_downloader_args()

    dl_path = os.path.join(args.data_path, 'tmp')

    with download_cleanup(dl_path):
        urls = extract_urls_from_csv(args.csv_path, args.col_no)

        download_batch_multithreaded(urls, dl_path, args.jobs)

        

        parsers = build_parsers([(str(i), str(i), os.path.join(dl_path, fname)) for i, fname in enumerate(os.listdir(dl_path))],
                                csv_dir=args.data_path, txt_dir=args.data_path)

        for parser in parsers:
            if parser is not None and parser.is_usable():
                logging.info(f'Writing to {parser.get_fname()}.txt')
                parser.dump_to_txt()

    return 0

if __name__ == '__main__':
    exit(main())