import argparse

from pipeline.misc.util import dump_args_to_csv
from pipeline.parsers.parser_helpers import build_parsers


def collect_parsing_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description='Extracts features from different types of documents. Supported types are : html, ppt, pptx, doc, docx, pdf and txt.', add_help=False)
    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')

    required.add_argument('-u','--uris', nargs='+', help='List of space-delimited file uris for document seeding (i.e. file paths and/or internet urls).', required=True)
    required.add_argument('-of', '--outfile', help='Path to CSV output file.', required=True)
    
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit.')

    args = parser.parse_args()
    args.uris = list(set(args.uris))

    return args


def main() -> int:
    args = collect_parsing_args()

    dump_args_to_csv(args)

    parsers = build_parsers(args.uris)

    for parser in parsers:
        parser.dump_to_csv(args.outfile)

    return 0


if __name__ == '__main__':
    exit(main())
