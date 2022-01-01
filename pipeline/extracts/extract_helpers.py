import pandas as pd

from pipeline.parsers.resource_parser import ResourceParser

from pipeline.extracts.key_phrase_extract import KeyPhraseExtract
from pipeline.extracts.bert_ner.bert_ner_extract import BertNerExtract
from pipeline.extracts.gen_sim.gen_sim_extract import GenSimExtract
from pipeline.extracts.key_bert.key_bert_extract import KeyBertExtract
from pipeline.extracts.rake.rake_extract import RakeExtract
from pipeline.extracts.rakun.rakun_extract import RakunExtract
from pipeline.extracts.yake.yake_extract import YakeExtract

def get_key_phrase_extract(extract_name: str) -> KeyPhraseExtract:
    extract = None

    if extract_name == 'BertNer':
        extract = BertNerExtract()
    elif extract_name == 'GenSim':
        extract = GenSimExtract()
    elif extract_name == 'KeyBert':
        extract = KeyBertExtract()
    elif extract_name == 'Rake':
        extract = RakeExtract()
    elif extract_name == 'Rakun':
        extract = RakunExtract()
    elif extract_name == 'Yake':
        extract = YakeExtract()

    return extract


def extract_key_phrases(resource_parser: ResourceParser, extract: KeyPhraseExtract, count: int = None) -> list:
    key_phrases = list()

    key_phrases.append(resource_parser.get_title())

    key_phrases += extract.extract_key_phrases(resource_parser)

    return key_phrases


def dump_key_phrases_to_csv(uris: list, key_phrases: list, out_file: str) -> None:
    df = pd.DataFrame(columns=['Source', 'Rank', 'Key Phrase'])

    for uri, key_phrase_list in zip(uris, key_phrases):
        for i, key_phrase in enumerate(key_phrase_list):
            df = df.append({df.columns[0]: uri,
                            df.columns[1]: str(i),
                            df.columns[2]: key_phrase}, 
                            ignore_index=True)
    
    df.to_csv(out_file, index=False, mode='a')
