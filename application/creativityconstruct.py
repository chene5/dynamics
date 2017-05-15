# -*- coding: utf-8 -*-
"""creativityconstruct.py
Defines the CreativityConstruct class.

TODO

Created on Mon Jun 29 13:31:22 2015

@author: Eric
"""
from os.path import isfile
from zipfile import ZipFile
# import logging

from gensim import corpora, models, similarities
# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords

# Custom modules
from thoughtconstruct import ThoughtConstruct

"""
logging.basicConfig(filename="log_CreativityConstruct.txt",
                    level=logging.DEBUG,
                    filemode="w")
"""


class CreativityConstruct(ThoughtConstruct):
    """This is the class for the creativity construct."""

    def __init__(self,
                 dict_name,
                 construct_path,
                 corpus_path=None,
                 corpus_file_extension=None,
                 num_topics=None,
                 lemmatize=False,
                 load_zip=False):
        self.name = dict_name
        self.construct_path = construct_path
        self.filename = self.construct_path + self.name
        self.corpus_path = corpus_path
        self.dictionary_filename = self.construct_path + self.name + '.dict'
        self.corpus_filename = self.construct_path + self.name + '.mm'
        self.index_filename = self.construct_path + self.name + '.index'
        self.lsi_filename = self.construct_path + self.name + '.lsi'

        self.load_zip = load_zip
        if self.load_zip:
            filename = self.construct_path + self.name
            if isfile(filename + '.zip'):
                self.filename = filename + '.zip'
            elif isfile(filename + '.ZIP'):
                self.filename = filename + '.ZIP'
            else:
                print 'Error! Zip file not found!'
                return None

        self.dictionary = None
        self.dictionary_len = 0
        self.corpus = None
        self.lsi = None
        self.index = None
        # XXX: debugging self.lemmatize = lemmatize
        self.lemmatize = False
        if lemmatize:
            # XXX: Not lemmatizing, for debugging
            # self.lemmatizer = WordNetLemmatizer()
            print "Not lemmatizing"
        else:
            self.lemmatizer = None
        self.num_topics = num_topics
        self.corrector = None
        # Check if we should load all info from disk.
        self.load_all()
        print "Loaded Thought Construct:", self.name

    def description(self):
        print("Construct", self.name, "located at ", self.construct_path)
        print("Dictionary filename is:", self.dictionary_filename)
        print("Corpus filename is:", self.corpus_filename)
        print("LSI model filename is:", self.lsi_filename)
        print("Index filename is:", self.index_filename)

    def print_dictionary(self):
        print self.dictionary

    def load_all(self):
        if self.load_zip:
            with ZipFile(self.filename, 'r') as zipf:
                dictf = zipf.open(self.name + '/' + self.name + '.dict')
                self.dictionary = corpora.Dictionary.load(dictf)
                corpf = zipf.open(self.name + '/' + self.name + '.mm')
                self.corpus = corpora.MmCorpus(corpf)
                lsif = zipf.open(self.name + '/' + self.name + '.lsi')
                self.lsi = models.LsiModel.load(lsif)
                indf = zipf.open(self.name + '/' + self.name + '.index')
                self.index = similarities.MatrixSimilarity.load(indf)
        else:
            self.dictionary = corpora.Dictionary.load(self.dictionary_filename)
            self.corpus = corpora.MmCorpus(self.corpus_filename)
            self.lsi = models.LsiModel.load(self.lsi_filename)
            self.index = similarities.MatrixSimilarity.load(
                self.index_filename)
        self.dictionary_len = len(self.dictionary)

    def interactive_query(self):
        word_1 = raw_input(
            '{}==> What is the first word? '.format(self.name)).lower()
        word_2 = raw_input(
            '{}==> What is the second word? '.format(self.name)).lower()
        result = self.query_pair_lsi(word_1, word_2)
        print 'The cosine similarity is', result

    def query_lsi(self, text):
        text = text.lower()
        # Decode to utf-8.
        text = text.decode('utf-8', 'replace')
        if self.lemmatizer:
            text = self.lemmatizer.lemmatize(text)
        if self.corrector:
            text = self.corrector.correct(text)
        vec_bow = self.dictionary.doc2bow(text.lower().split())
        vec_lsi = self.lsi[vec_bow]  # convert the query to LSI space
        return vec_lsi

    def query_index(self, text):
        return self.index[self.query_lsi(text)]
