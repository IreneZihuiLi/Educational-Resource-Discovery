import io
import logging
import requests
import sys
import numpy as np

from bs4 import BeautifulSoup
from random import choice
from string import ascii_uppercase

from pipeline.misc.util import SupressStdoutStderr
from pipeline.parsers.resource_parser import ResourceParser
from pipeline.parsers.pdf.paper_pdf_parser import PaperPdfParser
from pipeline.parsers.pdf.heuristic_pdf_parser import HeuristicPdfParser

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams


class PdfParser(ResourceParser):
    HASH_LENGTH = 10

    PAPER_SCORING_WEIGHTS = {
        'abstract': 5,
        'ref': 2,
        'bib': 3,
        'author': 1
    }

    PAPER_LEN_MIN = 300
    PAPER_SCORE_MIN = 5.0

    GROBID_SERVER = 'http://localhost'
    GROBID_PORT = '8070'

    def __init__(self, fname: str, link: str, outname: str, csv_dir: str, txt_dir: str, query: str = None):
        super().__init__(fname, link, outname, csv_dir, txt_dir, query)
        self.init_parser_impl()

    def get_title(self) -> str:
        if self.init_failed:
            return super().get_title()
        return self.parser_impl.get_title()

    def get_authors(self) -> list:
        if self.init_failed:
            return super().get_authors()
        return self.parser_impl.get_authors()

    def get_equations(self) -> list:
        if self.init_failed:
            return super().get_equations()
        return self.parser_impl.get_equations()

    def get_important_phrases(self) -> dict:
        if self.init_failed:
            return super().get_important_phrases()
        return self.parser_impl.get_important_phrases()

    def get_figure_captions(self) -> dict:
        if self.init_failed:
            return super().get_figure_captions()
        return self.parser_impl.get_figure_captions()

    def get_body_paragraphs(self) -> list:
        if self.init_failed:
            return super().get_body_paragraphs()
        return self.parser_impl.get_body_paragraphs()

    def get_bib(self) -> list:
        if self.init_failed:
            return super().get_bib()
        return self.parser_impl.get_bib()

    def get_refs(self) -> list:
        if self.init_failed:
            return super().get_refs()
        return self.parser_impl.get_refs()

    def is_paper(self) -> (bool, BeautifulSoup):
        url = '{}:{}/api/processFulltextDocument'.format(self.GROBID_SERVER, self.GROBID_PORT)
        files = {'input': (self.fname, open(self.fname, 'rb'), 'application/pdf', {'Expires': '0'})}
        the_data = {'consolidateHeader': '1'}
        headers = {'Accept': 'text/plain', 'Accept': 'application/xml'}

        response = requests.request(method='POST',
                                    url=url,
                                    headers=headers,
                                    files=files,
                                    data=the_data,
                                    timeout=5)

        soup = BeautifulSoup(response.text, features='html.parser')

        score = int(soup.find('abstract') is not None) * self.PAPER_SCORING_WEIGHTS['abstract'] + \
                len(soup.findAll('ref', {'type': 'bibr'})) * self.PAPER_SCORING_WEIGHTS['ref']

        author_list = soup.find('sourcedesc')
        if author_list:
            score += len(author_list.findAll('persname')) * self.PAPER_SCORING_WEIGHTS['author']

        bib_list = soup.find('listbibl')
        if bib_list:
            score += len(bib_list.findAll('biblstruct')) * self.PAPER_SCORING_WEIGHTS['bib']


        paragraph_lengths = [len(paragraph.text) for paragraph in soup.findAll('p')]
        num_chars = sum(paragraph_lengths)

        if num_chars < self.PAPER_LEN_MIN:
            num_chars = sys.maxsize

        return score / np.log(num_chars) >= self.PAPER_SCORE_MIN, soup

    def init_parser_impl(self) -> None:
        try:
            is_paper, soup = self.is_paper()

            if is_paper:
                self.parser_impl = PaperPdfParser(soup)
            else:
                hash = ''.join(choice(ascii_uppercase) for _ in range(self.HASH_LENGTH))
                page_seperator = '<span style=\"{}"><\span>'.format(hash)

                rsrcmgr = PDFResourceManager(caching=True)

                with io.StringIO() as outfp:
                    device = HTMLConverter(rsrcmgr, outfp, scale=1,
                                           layoutmode='loose', laparams=LAParams(),
                                           imagewriter=None, debug=0)

                    with open(self.fname, 'rb') as fp:
                        interpreter = PDFPageInterpreter(rsrcmgr, device)

                        logger = logging.getLogger()
                        logger.disabled = True

                        with SupressStdoutStderr():
                            for page in PDFPage.get_pages(fp, set(),
                                                        maxpages=0, password='',
                                                        caching=True, check_extractable=True):
                                outfp.write(page_seperator)
                                page.rotate = page.rotate % 360
                                interpreter.process_page(page)

                        logger.disabled = False

                        self.parser_impl = HeuristicPdfParser(BeautifulSoup(outfp.getvalue(), features='html.parser'), hash)                        
                        device.close()
        except Exception as e:
            self.init_failed = True
            logging.error('Cannot instantiate pdf parser: ' + str(e))
