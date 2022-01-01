from bs4 import BeautifulSoup
from collections import defaultdict

from pipeline.parsers.resource_parser import ResourceParser

class PaperPdfParser(ResourceParser):
    def __init__(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def get_title(self) -> str:
        return self.soup.find('filedesc').find('title').text

    def get_body_paragraphs(self) -> list:
        return [paragraph.text for paragraph in self.soup.findAll('p')]

    def get_authors(self) -> list:
        authors = list()

        def extract_organization(email: str) -> str:
            try:
                start = email.index('@') + 1
                end = email.index('.', start)
                return email[start:end]
            except:
                return None

        source_desc = self.soup.find('sourcedesc')

        if source_desc:
            for author in source_desc.findAll('author'):
                author_info = dict()

                forename = author.find('forename')
                if forename:
                    author_info['forename'] = forename.text

                surname = author.find('surname')
                if surname:
                    author_info['surname'] = surname.text
                
                email = author.find('email')
                if email:
                    email = extract_organization(email.text)
                    if email:
                        author_info['organization'] = email

                if author_info:
                    authors.append(author_info)

        return authors

    def get_equations(self) -> list:        
        return [formula.text for formula in self.soup.findAll('formula')]

    def get_important_phrases(self) -> dict:
        important_phrases = defaultdict(list)

        headings = self.soup.findAll('head')

        if headings:
            for heading in headings:
                level = heading.get('n')

                if level:
                    level = str(level.count('.'))
                else:
                    level = 'X'

                key = 'heading_' + level
                important_phrases[key].append(heading.text)

        footnotes = self.soup.findAll('note')

        if footnotes:
            for footnote in footnotes:
                if len(footnote.text) > 0:
                    important_phrases['footnote'].append(footnote.text)

        return dict(important_phrases)

    def get_figure_captions(self) -> dict:
        figure_dict = dict()
        figures = self.soup.findAll('figure')
        for figure in figures:
            figure_dict[figure['xml:id']] = figure.find('figdesc').text

        return figure_dict

    def get_bib(self) -> list:
        bib_list = list()
        bib = self.soup.find('listbibl')

        if bib:
            bib_entries = bib.findAll('biblstruct')

            for citation in bib_entries:
                citation_info = dict()

                paper_info = citation.find('analytic')
                if paper_info:
                    title = paper_info.find('title')
                    if title:
                        citation_info['title'] = title.text

                paper_info = citation.find('monogr')
                if paper_info:
                    journal_title = paper_info.find('title')
                    if journal_title:
                        citation_info['journal'] = journal_title.text

                author_forenames = citation.findAll('forename')
                author_surnames = citation.findAll('surname')
                num_authors = max(len(author_forenames), len(author_surnames))

                if num_authors > 0:
                    citation_info['authors'] = list()

                    for i in range(num_authors):
                        author_info = dict()
                        if i < len(author_forenames):
                            author_info['forename'] = author_forenames[i].text
                        if i < len(author_surnames):
                            author_info['surname'] = author_surnames[i].text

                        citation_info['authors'].append(author_info)

                date = citation.find('date')
                if date and 'when' in date:
                    citation_info['year'] = date['when'][:4]

                if citation_info:
                    bib_list.append(citation_info)
                
        return bib_list
                
    def get_refs(self) -> list:
        refs = self.soup.findAll('ref', {'type': 'bibr'})
        return [ref.text for ref in refs]
