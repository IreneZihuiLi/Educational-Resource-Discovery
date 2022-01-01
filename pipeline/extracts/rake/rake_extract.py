from rake_nltk import Rake

from pipeline.extracts.key_phrase_extract import KeyPhraseExtract
from pipeline.parsers.resource_parser import ResourceParser


class RakeExtract(KeyPhraseExtract):
    def __init__(self) -> None:
        super().__init__('pipeline/extracts/rake/config.yaml')
        self.rake = Rake()

    def extract_key_phrases(self, resource_parser: ResourceParser) -> list:
        self.rake.extract_keywords_from_text(resource_parser.get_key_phrase_extraction_text())
        return self.rake.get_ranked_phrases()[:self.num_keyphrases]
