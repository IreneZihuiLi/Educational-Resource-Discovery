import logging
import mimetypes
from enum import Enum

from pipeline.parsers.pdf.pdf_parser import PdfParser
from pipeline.parsers.html.html_parser import HtmlParser
from pipeline.parsers.pptx.pptx_parser import PptxParser


class FileType(Enum):
    HTML = 0
    PDF = 1
    PPT = 2
    DOC = 3
    TXT = 4

def uri_filetype_demux(uri: str) -> (FileType, str):
    ftype = FileType.HTML
    guessed_type = mimetypes.guess_type(uri)[0]

    if guessed_type:
        extension_to_filetype = {
            'html': FileType.HTML,
            'pdf': FileType.PDF,
            'pot': FileType.PPT,
            'pptx': FileType.PPT,
            'txt': FileType.TXT
        }

        ext = mimetypes.guess_extension(guessed_type)
        if ext is not None:
            ftype = extension_to_filetype.get(ext[1:], FileType.HTML)
    else:
        guessed_type = 'html'

    return ftype, guessed_type


def build_parsers(name_uris: list, csv_dir: str = None, txt_dir: str = None, keyphrase: str = '') -> list:
    parsers = [None for _ in range(len(name_uris))]

    for i, (name, url, uri) in enumerate(name_uris):

        ftype, guessed_type = uri_filetype_demux(uri)
        logging.info(f'Deducing {uri} to be of type {guessed_type} which is file type {ftype}.')

        if ftype == FileType.PDF:
            parsers[i] = PdfParser(uri, url, name, csv_dir, txt_dir, keyphrase)
        elif ftype == FileType.PPT:
            parsers[i] = PptxParser(uri, url, name, csv_dir, txt_dir, keyphrase)
        else:
            parsers[i] = HtmlParser(uri, url, name, csv_dir, txt_dir, keyphrase)
        logging.info('Done Deducing')

    logging.info('Done building parsers.')

    return parsers
