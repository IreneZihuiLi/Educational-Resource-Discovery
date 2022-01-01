import re
import nltk
from tika import parser
from bs4 import BeautifulSoup
from collections import defaultdict

from pipeline.parsers.resource_parser import ResourceParser


class PptxParser(ResourceParser):
    NULL_AUTHOR_NAME = 'Microsoft Office User'
    MIN_WORDS_IN_PARA = 4

    def __init__(self, fname: str, link: str, outname: str, csv_dir: str, txt_dir: str, query: str = None):
        super().__init__(fname, link, outname, csv_dir, txt_dir, query)

        try:
            parsed = parser.from_file(self.fname, xmlContent=True)
            self.soup = BeautifulSoup(parsed['content'], features='html.parser')
            self.slides = self.soup.findAll('div', {'class': 'slide-content'})
            self.metadata = parsed["metadata"]
        except:
            self.init_failed = True

    def is_body_point(self, text: str) -> bool:
        return self.MIN_WORDS_IN_PARA <= len(text.split())

    def get_paragraphs_from_slide(self, slide_no: int) -> list:
        return [p.text for p in self.slides[slide_no].findAll('p') if p.text]

    def get_headers(self) -> list:
        headers = list()
        for slide in self.slides[1:]:
            header = slide.find('p')
            if header is not None and header.text:
                headers.append(header.text)

        return headers

    def get_title(self) -> str:
        if self.init_failed:
            return super().get_title()

        texts = self.slides[0].findAll('p')
        for text in texts:
            if text.text.strip():
                return ' '.join(text.text.split())
        
        title = self.soup.find('title')
        if title is not None:
            return ' '.join(title.text.split())

        return ''

    def get_authors(self) -> list:
        if self.init_failed:
            return super().get_authors()

        author_names = list()

        names = self.get_paragraphs_from_slide(0)

        for text in names[1:]:
            for sent in nltk.sent_tokenize(text):
                for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                    try:
                        if chunk.label() == 'PERSON':
                            author_names.append(' '.join(c[0] for c in chunk.leaves()))
                    except:
                        pass

        name = self.soup.find('meta', {'name': 'Author'})
        if name is not None:
            name = name.get('content')
            if name != self.NULL_AUTHOR_NAME:
                author_names.append(name)

        name = self.soup.find('meta', {'name': 'Last-Author'})
        if name is not None:
            name = name.get('content')
            if name != self.NULL_AUTHOR_NAME:
                author_names.append(name)

        return list(set(author_names))

    def get_equations(self) -> list:
        return super().get_equations()

    def get_important_phrases(self) -> dict:
        if self.init_failed:
            return super().get_important_phrases()

        important_phrases = defaultdict(list)
        important_phrases['h1'] = [header for header in self.get_headers() if header]

        return dict(important_phrases)

    def get_figure_captions(self) -> dict:
        if self.init_failed:
            return super().get_figure_captions()

        images = {'image' + str(i): elem.get('id', 'null caption') for i, elem in enumerate(self.soup.findAll('div', {'class': 'embedded'}))}
        tables = {'table' + str(i): 'null table caption' for i in range(len(self.soup.findAll('table')))}
        return {**images, **tables}

    def get_body_paragraphs(self) -> list:
        if self.init_failed:
            return super().get_body_paragraphs()

        paragraphs = list()
        for i in range(1, len(self.slides)):
            ps = self.get_paragraphs_from_slide(i)[1:]
            for p in ps:
                if self.is_body_point(p):
                    paragraphs.append(' '.join(p.split()))

        return paragraphs

    def get_bib(self) -> list:
        if self.init_failed:
            return super().get_bib()

        bib_list = list()
        possible_bib_titles = ['references?', 'sources?', 'bibliography']
        subtitles = self.get_headers()
        found_sources = False

        for i, subtitle in enumerate(subtitles):
            if found_sources and len(subtitle) == 0:
                bib_list += self.get_paragraphs_from_slide(i + 1)[1:]
            elif any(re.match(pat, subtitle.strip(), re.IGNORECASE) for pat in possible_bib_titles):
                found_sources = True
                bib_list = self.get_paragraphs_from_slide(i + 1)[1:]
                
        return bib_list

    def get_refs(self) -> list:
        if self.init_failed:
            return super().get_refs()

        links = list()
        for slide_no in range(len(self.slides)):
            paragraphs = self.get_paragraphs_from_slide(slide_no)
            for paragraph in paragraphs:
                tokens = paragraph.split()
                for token in tokens:
                    if re.match(r'https?://.+', token):
                        links.append(token)

        return links
