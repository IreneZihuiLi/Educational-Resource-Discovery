from keybert import KeyBERT

from pipeline.extracts.key_phrase_extract import KeyPhraseExtract
from pipeline.parsers.resource_parser import ResourceParser


class KeyBertExtract(KeyPhraseExtract):
    def __init__(self) -> None:
        super().__init__('pipeline/extracts/key_bert/config.yaml')
        self.model = KeyBERT('distilbert-base-nli-mean-tokens')

    def extract_key_phrases(self, resource_parser: ResourceParser) -> list:
        results = self.model.extract_keywords(resource_parser.get_key_phrase_extraction_text(), 
                                              keyphrase_ngram_range=(self.ngram_range[0], self.ngram_range[1]),
                                              top_n=self.top_n,
                                              use_mmr=self.use_mmr,
                                              diversity=self.diversity,
                                              stop_words='english')

        return [phrase for phrase, _ in sorted(results, key=lambda item: item[1], reverse=True)[:self.num_keyphrases]]
