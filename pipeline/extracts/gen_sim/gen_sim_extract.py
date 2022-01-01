#from gensim.summarization import keywords

from pipeline.extracts.key_phrase_extract import KeyPhraseExtract
from pipeline.parsers.resource_parser import ResourceParser


class GenSimExtract(KeyPhraseExtract):
    def __init__(self) -> None:
        super().__init__('pipeline/extracts/gen_sim/config.yaml')

    def extract_key_phrases(self, resource_parser: ResourceParser) -> list:
        #result = keywords(resource_parser.get_key_phrase_extraction_text(), self.ratio)
        #return result.split('\n')
        return list()
