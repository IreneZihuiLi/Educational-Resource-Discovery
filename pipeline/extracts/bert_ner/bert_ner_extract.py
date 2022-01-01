from collections import defaultdict
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification

from pipeline.extracts.key_phrase_extract import KeyPhraseExtract
from pipeline.parsers.resource_parser import ResourceParser


class BertNerExtract(KeyPhraseExtract):
    def __init__(self) -> None:
        super().__init__('pipeline/extracts/bert_ner/config.yaml')
        tokenizer = AutoTokenizer.from_pretrained('dslim/bert-base-NER')
        model = AutoModelForTokenClassification.from_pretrained('dslim/bert-base-NER')
        self.nlp_pipeline = pipeline('ner', model=model, tokenizer=tokenizer)

    def extract_key_phrases(self, resource_parser: ResourceParser) -> list:
        ner_results = self.nlp_pipeline(resource_parser.get_key_phrase_extraction_text())
        keyword_list = list()
        keyword_score = list()

        for res in ner_results:
            if len(res) > 0:
                current = res[0]['index']
                current_word = [res[0]['word']]
                current_score = res[0]['score']
                for item in res[1:]:
                    if item['index'] == current + 1:
                        current_word.append(item['word'])
                        current = item['index']
                        current_score += item['score']
                    else:
                        keyword_list.append(current_word)
                        keyword_score.append(current_score)
                        current = item['index']
                        current_word = [item['word']]
                        current_score = item['score']

        clean = defaultdict(float)
        for group,score in zip(keyword_list, keyword_score):
            text = ' '.join([x for x in group])
            fine_text = text.replace(' ##', '')
            if len(fine_text) >= self.min_keyphrase_len:
                clean[fine_text] += score

        return [keyphrase for keyphrase, _ in sorted(clean.items(), key=lambda item: item[1], 
                reverse=True)[:self.num_keyphrases]]