import re
import os
import logging
import argparse
import pandas as pd


class SupressStdoutStderr():
    def __init__(self):
        self.null_fds =  [os.open(os.devnull,os.O_RDWR) for x in range(2)]
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        os.dup2(self.null_fds[0],1)
        os.dup2(self.null_fds[1],2)

    def __exit__(self, *_):
        os.dup2(self.save_fds[0],1)
        os.dup2(self.save_fds[1],2)
        for fd in self.null_fds + self.save_fds:
            os.close(fd)

# Currently unused
def dump_args_to_csv(args: argparse.Namespace) -> None:
    df = pd.DataFrame(columns=['Arg Name', 'Arg Value'])

    for arg_name, arg_value in vars(args).items():
        if arg_name != 'outfile':
            if type(arg_value) == list:
                for i, elem in enumerate(arg_value):
                    df = df.append({df.columns[0]: "{}[{}]".format(arg_name, str(i)),
                                    df.columns[1]: elem},
                                    ignore_index=True)
            else:
                df = df.append({df.columns[0]: arg_name,
                                df.columns[1]: arg_value},
                                ignore_index=True)

    df.to_csv(args.outfile, index=False)


def log_args(args: argparse.Namespace) -> None:
    logging.info('Command Line Arguments')
    for arg_name, arg_value in vars(args).items():
        if arg_name != 'outfile':
            logging.info('%16s: %16s' % (arg_name, arg_value))
    logging.info('\n\n')


def parse_key_phrase_file(args: argparse.Namespace) -> None:
    args.start_query = max(args.start_query, 0)

    if args.end_query == -1:
        args.end_query = int('inf')

    args.keyphrase_counts = list()
    args.keyphrase_domains = list()

    try:
        with open(args.keyphrases_file, 'r') as f:
            domain = 'none'
            idx = 0
            for line in f:
                if line.startswith('DOMAIN'):
                    (_, domain) = line.split()
                    idx = 0

                elif re.match(args.domain, domain):
                    if idx >= args.start_query and idx < args.end_query:
                        sep = line.rfind(',')
                        args.keyphrases.append(line[:sep].strip())
                        args.keyphrase_counts.append(int(line[sep + 1:].strip()))
                        args.keyphrase_domains.append(domain)

                    idx += 1

    except Exception as e:
        logging.error(f'Could not open keyphrase file: {args.keyphrases_file}')
        logging.error(str(e))


def dump_links_to_csv(path: str, links_info: list) -> None:
    has_col_titles = False

    try:
        with open(path, 'r') as f:
            titles = f.readline()
            if titles.startswith('Name,'):
                has_col_titles = True
    except:
        logging.info('Annotation file does not exist, creating a new one.')

    with open(path, 'a') as f:
        if not has_col_titles:
            f.write('Name,Query,URL\n')
        for fname, query_str, link in links_info:
            f.write(f'{fname},{query_str},{link}\n')
