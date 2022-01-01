import argparse

from pipeline.download_manager import DownloadManager
from pipeline.misc.util import dump_args_to_csv
from pipeline.parsers.main import build_parsers
from pipeline.extracts.extract_helpers import get_key_phrase_extract, extract_key_phrases, dump_key_phrases_to_csv

DEFAULT_NUM_KEYWORDS = 5
DEFAULT_NUM_SEARCH_RESULTS = 5

def collect_seeding_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Seed a document for key phrases.', add_help=False)

    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')

    required.add_argument('-of', '--outfile', help='Path to CSV output file.', required=True)
    required.add_argument('-u','--uris', nargs='+', help='List of space-delimited file uris for document seeding (i.e. file paths and/or internet urls).')
    required.add_argument('-ex','--extract', help='Extraction strategy to use.', choices=['BertNer', 'GenSim', 'KeyBert', 'Rake', 'Rakun', 'Yake'])

    optional.add_argument('-mos','--macos', action='store_true', help='Specify if you are on MacOS. If unspecified, the webcrawler will run on Linux.')
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit.')

    args = parser.parse_args()
    
    return args


def main() -> int:
    args = collect_seeding_args()
    dump_args_to_csv(args)

    with DownloadManager() as dm:

        parsers = build_parsers(args.uris)
        extract = get_key_phrase_extract(args.extract)

        key_phrases = list()

        for parser in parsers:
            key_phrases.append(extract_key_phrases(parser, extract))

        dump_key_phrases_to_csv(args.uris, key_phrases, args.outfile)

    return 0


if __name__ == '__main__':
    exit(main())
