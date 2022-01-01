import re
import abc
import numpy as np
import pandas as pd
import os.path

from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from spellchecker import SpellChecker

def clean_text(text: str) -> str:
    text = re.sub(str(chr(160)) + '|'  + str(chr(9)), '', text)
    text = re.sub(r'( |\t) +', ' ', text)
    text = '\n'.join([line for line in text.split('\n') if re.search('[a-zA-Z]', line)])
    return text

class ResourceParser(metaclass=abc.ABCMeta):
    def __init__(self, fname: str, link: str, outname: str, csv_dir: str, txt_dir: str, query: str):
        self.fname = fname
        self.link = link
        self.csv_outname = os.path.join(csv_dir, outname + '.csv')
        self.txt_outname = os.path.join(txt_dir, outname + '.txt')
        self.init_failed = False
        self.query = query

    @abc.abstractmethod
    def get_title(self) -> str:
        return None

    @abc.abstractmethod
    def get_authors(self) -> list:
        return list()

    @abc.abstractmethod
    def get_equations(self) -> list:
        return list()

    @abc.abstractmethod
    def get_important_phrases(self) -> dict:
        return dict()

    @abc.abstractmethod
    def get_figure_captions(self) -> dict:
        return dict()

    @abc.abstractmethod
    def get_body_paragraphs(self) -> list:
        return list()

    @abc.abstractmethod
    def get_bib(self) -> list:
        return list()

    @abc.abstractmethod
    def get_refs(self) -> list:
        return list()

    def get_body_text(self) -> str:
        return '\n'.join([' '.join(paragraph.split()) for paragraph in self.get_body_paragraphs()])

    def get_fname(self) -> str:
        return self.fname

    def is_usable(self) -> bool:
        return not self.init_failed

    def get_annotation_info(self) -> (str, str, str):
        return (self.txt_outname[self.csv_outname.rfind('/') + 1:], self.query, self.link)

    def extract_link_features(self) -> (str, str, str, str):
        link = self.link[:]
        link = link[link.find('//') + 2:]

        sub_domain = link[:link.find('.')]
        link = link[link.find('.') + 1:]

        second_domain = link[:link.find('.')]
        link = link[link.find('.') + 1:]

        top_domain = link[:link.find('/')]

        num_url_subdirs = link.count('/')

        return sub_domain, second_domain, top_domain, num_url_subdirs

    def extract_vocab_features(self) -> (float, float, float):
        word_count = len(self.words)
        
        normalized_vocab = 0
        vocab_mean = 0
        vocab_stdev = 0

        if word_count > 0:
            word_histogram = Counter(self.words)
            normalized_vocab = round(len(word_histogram) / word_count, 3)
            vocab_mean = round(np.mean(list(word_histogram.values())), 3)
            vocab_stdev = round(np.std(list(word_histogram.values())), 3)

        return normalized_vocab, vocab_mean, vocab_stdev

    def extract_word_features(self) -> (float, float, float):
        word_count = len(self.words)
        
        word_len_mean = 0
        word_len_stdev = 0
        percent_typos = 0

        if word_count > 0:
            word_lengths = [len(word) for word in self.words]
            word_len_mean = round(np.mean(word_lengths), 3)
            word_len_stdev = round(np.std(word_lengths), 3)

            spell = SpellChecker()
            percent_typos = round(len(spell.unknown(self.words)) / word_count * 100, 3)

        return word_len_mean, word_len_stdev, percent_typos

    def extract_sentence_features(self) -> (int, float, float):
        sentences = sent_tokenize(self.free_text)

        num_sents = len(sentences)
        sent_mean = 0
        sent_stdev = 0

        sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]

        if num_sents > 0:
            sent_mean = round(np.mean(sentence_lengths), 3)
            sent_stdev = round(np.std(sentence_lengths), 3)
        
        return num_sents, sent_mean, sent_stdev

    def cache_free_text(self) -> None:
        self.figure_captions = self.get_figure_captions()
        self.body_text = self.get_body_text()
        self.important_phrases = self.get_important_phrases()
        self.title = clean_text(self.get_title()).replace(str(chr(10)), '')

    def combine_free_text(self) -> None:
        if not hasattr(self, 'free_text'):
            self.cache_free_text()

            self.free_text = self.title + '\n'

            for important_phrases in self.important_phrases.values():
                for important_phrase in important_phrases:
                    self.free_text += important_phrase + '\n'

            self.free_text += self.body_text + '\n'

            for caption in self.figure_captions.values():
                self.free_text += caption + '\n'

            self.free_text = clean_text(self.free_text)
            self.words = [word.lower() for word in word_tokenize(self.free_text)]
        
    def dump_to_txt(self) -> None:
        self.combine_free_text()

        with open(self.txt_outname, 'w') as f:    
            f.write(self.free_text)

    def dump_to_csv(self) -> None:
        self.combine_free_text()

        sub_domain, second_domain, top_domain, num_url_subdirs = self.extract_link_features()
        num_sents, sent_mean, sent_stdev = self.extract_sentence_features()
        word_mean, word_stdev, pct_typos = self.extract_word_features()
        normalized_vocab, vocab_mean, vocab_stdev = self.extract_vocab_features()

        df = pd.DataFrame([[self.title,
                            self.link,
                            len(self.get_authors()),
                            len(self.get_important_phrases()),
                            len(self.get_figure_captions()),
                            len(self.get_equations()),
                            len(self.get_body_paragraphs()),
                            num_sents,
                            sent_mean,
                            sent_stdev,
                            len(self.words),
                            word_mean,
                            word_stdev,
                            normalized_vocab,
                            vocab_mean,
                            vocab_stdev,
                            pct_typos,
                            len(self.get_refs()),
                            self.free_text.count('github.com'),
                            len(self.get_bib()),
                            sub_domain,
                            second_domain,
                            top_domain,
                            num_url_subdirs]],
                            columns=['Title',
                                     'Url',
                                     'NumAuthors',
                                     'NumHeadings',
                                     'NumFigures', 
                                     'NumEquations',
                                     'NumParagraphs',
                                     'NumSentences',
                                     'SentenceLenMean',
                                     'SentenceLenStdev',
                                     'NumWords',
                                     'WordLenMean',
                                     'WordLenStdev',
                                     'NormalizedUniqueVocab',
                                     'UniqueVocabMean',
                                     'UniqueVocabStdev',
                                     'PercentTypos',
                                     'NumLinks',
                                     'NumGithubLinks',
                                     'BibLength',
                                     'SubDomain',
                                     'SecondDomain',
                                     'TopDomain',
                                     'NumUrlSubdirs'])
       
        df.to_csv(self.csv_outname)
