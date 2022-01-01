import re

from bs4 import BeautifulSoup
from collections import defaultdict

HASH_LENGTH = 10

def get_num_alpha_characters(text: str) -> int:
    alpha_cnt = 0
    for c in text: alpha_cnt += int(c.isalpha())
    return alpha_cnt  


class HeuristicPdfParser():
    MIN_ALPHAS_IN_TITLE = 5
    MIN_BODY_LENGTH = 150

    IGNORE_TEXT_PATTERNS = [re.compile(pattern) for pattern in 
    [
        r'\(cid:[0-9]+\)'
    ]]

    def __init__(self, soup: BeautifulSoup, page_seperator: str):
        self.body_font_size = 0
        self.hash = page_seperator

        self.font_size_to_text = defaultdict(list)
        self.font_size_to_word_cnt = defaultdict(int)
        self.font_size_to_paragraph_cnt = defaultdict(int)
        self.pages = list()
        self.raw = ''

        self.soup = soup

        self.bucket_by_font_size()


    def is_title_candidate(self, text: str) -> bool:
        return self.MIN_ALPHAS_IN_TITLE <= get_num_alpha_characters(text)

    def get_title(self) -> str:
        sorted_font_sizes = sorted(list(self.font_size_to_text.keys()), reverse=True)
        found_title_start = False
        title = ''

        first_page = list(dict.fromkeys(self.pages[0]))

        for font_size in sorted_font_sizes:
            for text in first_page:
                if self.is_title_candidate(text):
                    if text in self.font_size_to_text[font_size]:
                        found_title_start = True
                        title += text.replace('\n', ' ')
                elif found_title_start:
                    return title.strip()

            if found_title_start:
                break

        return title.strip()

    def get_body_paragraphs(self) -> list:
        return self.raw.split('\n')

    def get_authors(self) -> list:
        return list()

    def get_equations(self) -> list:
        return list()

    def get_important_phrases(self) -> dict:
        return dict()

    def get_figure_captions(self) -> dict:
        return dict()

    def get_bib(self) -> list:
        return list()

    def get_refs(self) -> list:
        return list()

    def extract_font_size_from_style(self, style: str) -> int:
        start_idx = style.index('font-size:') + len('font-size:')
        end_idx = style.index('px', start_idx)
        return int(style[start_idx:end_idx].strip())

    def bucket_by_font_size(self) -> None:

        def clean_text(text: str) -> (str, int):
            if len(text.strip()) == 0:
                return '', 0

            text = text.replace('-\n', '').strip()
            num_newlines = text.count('\n')

            return text.strip(), num_newlines

        span_pattern = re.compile(r'(.*font-size:.*|{})'.format(self.hash))

        for text_span in self.soup.findAll('span', {'style': span_pattern}):
            if text_span.get('style') == self.hash:
                self.pages.append(list())
            else:
                text = text_span.text
                text, num_paragraphs = clean_text(text)

                self.raw += text
                text = text.replace('\n', ' ')

                if text and not any(re.match(pattern, text) for pattern in self.IGNORE_TEXT_PATTERNS):
                    font_size = self.extract_font_size_from_style(text_span.get('style'))
                    self.font_size_to_text[font_size].append(text)
                    self.font_size_to_word_cnt[font_size] += len(text.split())
                    self.font_size_to_paragraph_cnt[font_size] += num_paragraphs
                    self.pages[-1].append(text)
