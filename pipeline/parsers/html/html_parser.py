import re
from bs4 import BeautifulSoup

from pipeline.parsers.resource_parser import ResourceParser


class HtmlParser(ResourceParser):

    def __init__(self, fname: str, link: str, outname: str, csv_dir: str, txt_dir: str, query: str = None):
        super().__init__(fname, link, outname, csv_dir, txt_dir, query)
        
        try:
            with open(self.fname, 'r') as f:
                self.soup = BeautifulSoup(f.read(), features='html.parser')
        except:
            self.init_failed = True

        self.strong_text = None
        self.strong_text_elements = None


    def get_title(self) -> str:
        if self.init_failed:
            return super().get_title()

        text = ''
        title = self.soup.find('title')
        if title:
            text = title.text
        return text


    def get_authors(self) -> list:
        if self.init_failed:
            return super().get_authors()

        def author_name_len_range(name: str) -> bool:
            return len(name) > 0 and len(name) < 30

        try:
            # meta heuristic
            authors = self.soup.findAll('meta', {'name': re.compile('.*[aA]uthor.*')})
            if len(authors) > 0:
                return [author.get('content').strip() for author in authors if author_name_len_range(author.get('content').strip())]

            # rel heuristic
            authors = self.soup.findAll(re.compile('.+'), {'rel', re.compile('.*[aA]uthor.*')})
            if len(authors) > 0:
                return [author.text.strip() for author in authors if author_name_len_range(author.text.strip())]

            # address heuristic
            authors = self.soup.findAll('address', {'class': re.compile('.*[aA]uthor.*')})
            if len(authors) > 0:
                return [author.text.strip() for author in authors if author_name_len_range(author.text.strip())]

            # general class names
            authors = self.soup.findAll(re.compile('.+'), {'class': re.compile('(.*[aA]uthor.*|.*[Bb]yline.*)')})
            return [author.text.strip() for author in authors if author_name_len_range(author.text.strip())]
        except:
            return list()


    def get_equations(self) -> list:
        if self.init_failed:
            return super().get_equations()

        eqn_list = list()
        html = str(self.soup)
        eqn_starts = [m.start() + m.group().find('}') for m in re.finditer(re.compile(r'\\begin{.+}'), html)]
        eqn_ends = [m.start() for m in re.finditer(re.compile(r'\\end{.+}'), html)]
        num_equations = min(len(eqn_starts), len(eqn_ends))

        start_idx = 0
        end_idx = 0

        while start_idx < num_equations:
            while start_idx < num_equations and eqn_starts[start_idx] >= eqn_starts[end_idx]:
                start_idx += 1
                end_idx += 1

            if start_idx == num_equations:
                break

            i = start_idx

            while i < num_equations and eqn_starts[i] < eqn_ends[end_idx]:
                i += 1

            end_idx = i - 1

            eqn_list.append(html[eqn_starts[start_idx]:eqn_ends[end_idx]].strip())
            
            end_idx = i
            start_idx = end_idx

        return eqn_list


    def get_important_phrases(self) -> dict:
        if self.init_failed:
            return super().get_important_phrases()
        
        important_phrases = dict()
        self.get_strong_text()

        important_phrases = self.strong_text

        return important_phrases


    def get_figure_captions(self) -> dict:
        if self.init_failed:
            return super().get_figure_captions()

        image_dict = dict()
        for img_no, image in enumerate(self.soup.findAll('img')):
            caption = image.get('alt', None)
            if caption is not None:
                image_dict[caption.strip()] = str(img_no)
            else:
                image_dict['unlabeled_img_' + str(img_no)] = str(img_no)

        return image_dict


    def get_body_paragraphs(self) -> list:
        if self.init_failed:
            return super().get_body_paragraphs()

        return [paragraph.text.strip() for paragraph in self.soup.findAll('p') if len(paragraph.text.strip()) > 0]


    def get_bib(self) -> list:
        if self.init_failed:
            return super().get_bib()

        bib_list = list()

        possible_bib_titles = ['references?', 'sources?', 'bibliography']
        if self.strong_text is None:
            self.get_strong_text()

        headers_elem = list()
        headers_text = list()

        for strong_type in self.strong_text.keys():
            headers_text += self.strong_text[strong_type]
            headers_elem += self.strong_text_elements[strong_type]

        for i, text_content in enumerate(headers_text):
            if any(re.match(pat, text_content, re.IGNORECASE) for pat in possible_bib_titles):
                bib = headers_elem[i].parent.find(re.compile('(ul|ol)'))
                if bib:
                    bib_elems = bib.findAll('li')
                    for bib_elem in bib_elems:
                        citation = bib_elem.find('cite')
                        if citation:
                            bib_list.append(citation.text.strip())
                        else:
                            try:
                                bib_list.append(bib_elem.text.strip())
                            except:
                                pass

        return bib_list


    def get_refs(self) -> list:
        if self.init_failed:
            return super().get_refs()

        refs = list()
        for hyperlink in self.soup.findAll('a', {'href': re.compile(r'.*')}):
            href = hyperlink.get('href')
            if href.startswith('http'):
                refs.append(href.strip())
            elif href.startswith('//'):
                refs.append(href[2:].strip())
        
        return refs


    def get_strong_text(self) -> None:
        self.strong_text = dict()
        self.strong_text_elements = dict()
        key_tags = ['h1', 'h2', 'h3', 'strong']
        for key_tag in key_tags:
            self.strong_text_elements[key_tag] = [elem for elem in self.soup.findAll(key_tag) if len(elem.text) > 0]
            self.strong_text[key_tag] = [elem.text.strip() for elem in self.strong_text_elements[key_tag] if len(elem.text.strip()) > 0]
