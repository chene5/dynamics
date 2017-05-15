# -*- coding: utf-8 -*-
"""corpusupdater.py
Defines the class that updates the creativityconstruct.

TODO

Created on Fri Oct 14 15:39:23 2015

@author: Eric Chen
"""
import logging
from gensim import corpora, similarities  # , models
# import os
# import sys
# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords
# import smart_open
# from HTMLParser import HTMLParser
# import string

# Custom modules
from corpusprocessor import CorpusProcessor
# from creativityconstruct import CreativityConstruct
# import corrector
# import eec_utils
# import zippedtexts
# import parsebows

__author__ = 'Eric Chen'


class CorpusUpdater(CorpusProcessor):
    """This is the class for the corpus updater.
        If update is True, we're going to update an existing Construct,
            so we will reload it from disk.
    """

    def __init__(self):
        """Initialize the object. Takes the same arguments as the original."""
        print "Updating Creativity Construct:", self.name

    def interactive(self):
        while True:
            print '*** Options:'
            print '* query'
            print '* update'
            print '* exit'
            try:
                command = raw_input('==> What now [exit]? ').lower()
            except KeyboardInterrupt:
                print 'Goodbye!'
                # sys.exit()
                return

            if command == 'update':
                self.interactive_update()
                continue
            if command == 'query':
                self.interactive_query()
                continue
            if command == 'exit' or command == '':
                print 'Goodbye!'
                return

            print "I didn't understand your request."

    def interactive_update(self):
        update_name = raw_input('==> What is the name of the corpus to update from? ').lower()
        if update_name == '':
            print 'Ok, nevermind, then.'
            return
        update_path = 'c:/bin/creativity/corpus/' + update_name + '/'
        print 'Ok, updating from ', update_path
        update_ext = raw_input('==> What is the file extension of the corpus files [{}]? '.format(self.corpus_file_extension)).lower()
        if update_ext == '':
            update_ext = self.corpus_file_extension
        self.update_all(update_path, update_ext)
        print 'Done updating!'

    def update_corpus(self, texts):
        logging.debug("Updating corpus.")
        # It's the same process as creating a new one,
        # so just call the same function.
        self.add_corpus(texts)

    def update_lsi(self, corpus):
        """Online updating for the LSI model."""
        logging.debug("Updating LSI model.")
        self.lsi.add_documents(corpus)
        # XXX: Figure out a good way to determine filenames.
        # self.lsi.save(self.lsi_filename + '.1' + '.lsi')
        self.lsi.save(self.lsi_filename)

    def update_index(self, corpus):
        logging.debug("Updating index.")
        # XXX: gensim's add_documents method doesn't seem to work.
        # For now, just re-index everything.
        # Hopefully it won't take too long. :(
        # self.index.add_documents(corpus)
        self.index = similarities.Similarity(self.dict_path,
                                             self.lsi[corpus],
                                             num_features=self.num_topics)
        logging.debug('Saving updated index')
        self.index.save(self.index_filename)
        logging.debug('Saved updated index')

    def update_all(self, corpus_path, corpus_file_extension):
        """
        Update all the models.

        :param corpus_path: The path to the directory containing the files.
        :param corpus_file_extension: The file extension of the files.
        :return: Nothing
        """

        print "Updating models for:", self.name

        """
        documents = self.process_documents(corpus_path, corpus_file_extension)
        texts = self.get_texts_as_bow(documents)
        """
        texts = self.get_bows(corpus_path, corpus_file_extension)

        self.update_dictionary(texts)
        self.update_corpus(texts)
        # XXX: Using the whole, updated dictionary should work.
        # XXX: Or not:
        change_dictionary = corpora.Dictionary(texts)
        change_corpus = [change_dictionary.doc2bow(text) for text in texts]
        self.update_lsi(change_corpus)
        # Here we update the index with the corpus of new texts, but we can
        # index with any set of documents.
        self.update_index(change_corpus)

        """
        if spell_check is True:
            pass
        """
        logging.debug('Done updating models.')

    def update_from_file(self, file_name, file_extension):
        """Update the LSI model from a file."""
        # XXX Need to update the corpus and dictionary files.
        logging.debug("Updating from file {}.".format(file_name))
        corpus = self.create_corpus(file_name, file_extension)
        self.update_lsi(corpus)
        self.update_index()

# end of CorpusUpdater class
