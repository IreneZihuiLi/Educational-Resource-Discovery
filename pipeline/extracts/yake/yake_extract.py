import yake
from pipeline.extracts.key_phrase_extract import KeyPhraseExtract
from pipeline.parsers.resource_parser import ResourceParser

class YakeExtract(KeyPhraseExtract):
    def __init__(self) -> None:
        super().__init__('pipeline/extracts/yake/config.yaml')
        self.yake = yake.KeywordExtractor(lan='en',
                                          n=self.max_ngram_size,
                                          dedupLim=self.deduplication_thresold,
                                          dedupFunc=self.deduplication_algo,
                                          windowsSize=self.window_size,
                                          top=self.num_keyphrases,
                                          features=None)

    def extract_key_phrases(self, resource_parser: ResourceParser) -> list:
        keyphrases = self.yake.extract_keywords(resource_parser.get_key_phrase_extraction_text())
        return [keyphrase[0] for keyphrase in keyphrases]