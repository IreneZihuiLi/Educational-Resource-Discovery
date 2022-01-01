from mrakun import RakunDetector
from nltk.corpus import stopwords

from pipeline.extracts.key_phrase_extract import KeyPhraseExtract
from pipeline.parsers.resource_parser import ResourceParser


class RakunExtract(KeyPhraseExtract):
    def __init__(self) -> None:
        super().__init__('pipeline/extracts/rakun/config.yaml')

        hyperparameters = {'distance_threshold': self.distance_threshold,
                           'distance_method': self.distance_method,
                           'num_keywords': self.num_keywords,
                           'pair_diff_length': self.pair_diff_length,
                           'bigram_count_threshold': self.bigram_count_threshold,
                           'max_similar': self.max_similar,
                           'max_occurrence': self.max_occurrence,
                           'num_keywords': self.num_keyphrases,
                           'num_tokens': self.num_tokens,
                           'stopwords': stopwords.words('english')}

        self.rakun = RakunDetector(hyperparameters)

    def extract_key_phrases(self, resource_parser: ResourceParser) -> list:
        keyphrases = self.rakun.find_keywords(resource_parser.get_key_phrase_extraction_text(), input_type = 'text')
        return [keyphrase for keyphrase, _ in keyphrases]
