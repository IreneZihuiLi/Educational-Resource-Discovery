from pipeline.parsers.resource_parser import ResourceParser

class TextParser(ResourceParser):
    def __init__(self, fname: str, outname: str, csv_dir: str, txt_dir: str, query: str = None):
        super().__init__(fname, outname, csv_dir, txt_dir, query)

        with open(self.fname, 'r') as f:
            self.text = f.read()        

    def get_title(self) -> str:
        return ''

    def get_authors(self) -> list:
        return list()

    def get_equations(self) -> list:
        return list()

    def get_important_phrases(self) -> dict:
        return dict()

    def get_figure_captions(self) -> dict:
        return dict()

    def get_body_paragraphs(self) -> list:
        return self.text.split('\n')

    def get_bib(self) -> list:
        return list()

    def get_refs(self) -> list:
        return list()
