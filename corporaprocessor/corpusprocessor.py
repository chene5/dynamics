# -*- coding: utf-8 -*-
"""corpusprocessor.py
Defines the class that creates the LSI model.

TODO

Created on Fri Aug 28 13:21:00 2015

@author: Eric Chen
"""
import os
# import sys
import logging
from gensim import corpora, models, similarities
from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords
# import smart_open
import unicodedata
from HTMLParser import HTMLParser
import string

# Custom modules
from ..application.creativityconstruct import CreativityConstruct
import corrector
from ..application import eec_utils
# import zippedtexts
import parsebows

__author__ = 'Eric Chen'

# logger = logging.getLogger(__name__)
"""
logging.basicConfig(filename="log_CorpusProcessor.txt",
                    level=logging.DEBUG,
                    filemode="w")
"""
# List of stopwords.
# The first option is the default NLTK stopword list.
# STOPLIST = set(stopwords.words('english'))
# STOPLIST = set("for a of the and to in . , ! \" ( ) + - *".split())
# STOPLIST = set("for a an of the and to in".split())
# Don't remove any stopwords.
STOPLIST = set()

hparser = HTMLParser()


class CorpusProcessor(CreativityConstruct):
    """This is the class for the corpus processor.
        If update is True, we're going to update an existing Construct,
            so we will reload it from disk.
    """

    def __init__(self,
                 dict_name,
                 dict_path,
                 corpus_path=None,
                 corpus_file_extension=None,
                 specific_corpora=False,
                 update=False,
                 num_topics=None,
                 lemmatize=False):
        self.name = dict_name
        self.dict_path = dict_path
        self.filename = self.dict_path + self.name
        # Define these here.
        self.dictionary_filename = None
        self.corpus_filename = None
        self.index_filename = None
        self.lsi_filename = None
        self.log_filename = None
        self.specific_corpora = specific_corpora

        if corpus_path is None:
            self.corpus_path = self.dict_path
        else:
            self.corpus_path = corpus_path

        # XXX: Probably don't need the file extension as a class attribute.
        # XXX: Probably will eventually want the default to be all files.
        if corpus_file_extension is None:
            self.corpus_file_extension = '.txt'
        else:
            self.corpus_file_extension = corpus_file_extension

        # XXX: Figure out a good way to set number of features.
        if num_topics is None:
            self.num_topics = 5
        else:
            self.num_topics = num_topics

        # Set the basic filenames.
        self.set_filenames(self.dict_path, self.name)

        # Check if we are doing lemmatization.
        self.lemmatize = lemmatize
        if lemmatize:
            print 'Lemmatizing with WordNetLemmatizer'
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.lemmatizer = None
        self.corrector = None
        # Check if we should load all info from disk.
        if update is True:
            self.load_all()
            print "Loaded existing Thought Construct:", self.name
        else:
            # Double check if we should reload from disk.
            if self.check_reload():
                self.load_all()
                print "Loaded existing Thought Construct:", self.name
            else:
                self.create_all(self.corpus_path, self.corpus_file_extension)
                print "Created new Thought Construct:", self.name

    def set_filenames(self, path_name, dict_name):
        self.dictionary_filename = path_name + dict_name + '.dict'
        self.corpus_filename = path_name + dict_name + '.mm'
        self.index_filename = path_name + dict_name + '.index'
        self.lsi_filename = path_name + dict_name + '.lsi'
        self.log_filename = path_name + dict_name + '_corpora_log' + '.txt'

    def check_reload(self):
        """Double-check if the dictionary already exists on disk.
           Doing this double check because it can be really time-consuming
           to re-run everything.
           Returns True if we should reload from disk.
           Returns False if we should create a new Thought Construct.
        """
        if os.path.isfile(self.dictionary_filename):
            print "<CorpusProcessor> This dictionary exists."
            message = "==> Do you want to load it from disk ([yes]/no)? " + \
                "(If no it will be overwritten.) "
            command = raw_input(message).lower()
            if command == 'no':
                return False
            else:
                return True
        else:
            return False

    def description(self):
        print("Construct", self.name, "located at ", self.dict_path)
        print("Dictionary filename is:", self.dictionary_filename)
        print("Corpus filename is:", self.corpus_filename)
        print("LSI model filename is:", self.lsi_filename)
        print("Index filename is:", self.index_filename)

    def print_dictionary(self):
        print self.dictionary

    def interactive(self):
        while True:
            print '*** Options:'
            print '* query'
            print '* exit'
            try:
                command = raw_input('==> What now [exit]? ').lower()
            except KeyboardInterrupt:
                print 'Goodbye!'
                # sys.exit()
                return

            if command == 'query':
                self.interactive_query()
                continue
            if command == 'exit' or command == '':
                print 'Goodbye!'
                return

            print "I didn't understand your request."

    def add_dictionary(self, texts):
        logging.debug("Adding dictionary.")
        self.dictionary = corpora.Dictionary(texts)
        self.dictionary_len = len(self.dictionary)
        # Now store the dictionary to disk.
        self.dictionary.save(self.dictionary_filename)

    def add_corpus(self, texts):
        logging.debug("Adding corpus.")
        self.corpus = [self.dictionary.doc2bow(text) for text in texts]
        # Now store the corpus to disk.
        corpora.MmCorpus.serialize(self.corpus_filename, self.corpus)

    def add_lsi(self):
        logging.debug("Adding LSI model.")
        self.lsi = models.LsiModel(self.corpus,
                                   id2word=self.dictionary,
                                   num_topics=self.num_topics)
        self.lsi.save(self.lsi_filename)

    def add_index(self):
        """
        Transform corpus to LSI space and index it.

        :return: Nothing
        """
        logging.debug("Adding index.")
        """One possible way to get the number of topics.
        max_ids = utils.get_max_id(self.corpus)
        print 'max_ids is', max_ids
        if self.num_topics > max_ids + 1:
            num_topics = max_ids + 1
        else:
            num_topics = self.num_topics
        """
        self.index = similarities.Similarity(self.dict_path + self.name,
                                             self.lsi[self.corpus],
                                             num_features=self.num_topics)
        self.index.save(self.index_filename)

    def add_corrector(self, texts):
        """Spell checker and suggestion giver.
        XXX Save this to disk."""
        self.corrector = corrector.Corrector(texts)

    def load_all(self):
        self.dictionary = corpora.Dictionary.load(self.dictionary_filename)
        self.dictionary_len = len(self.dictionary)
        self.corpus = corpora.MmCorpus(self.corpus_filename)
        self.lsi = models.LsiModel.load(self.lsi_filename)
        self.index = similarities.MatrixSimilarity.load(self.index_filename)

    def create_all(self, corpus_path, corpus_file_extension):
        print "Creating new Thought Construct:", self.name

        """
        documents = self.process_documents(corpus_path, corpus_file_extension)
        texts = self.get_texts_as_bow(documents)
        """
        if self.specific_corpora:
            texts = self.parse_specific(corpus_path, corpus_file_extension)
            texts += self.get_bows(corpus_path, corpus_file_extension)
        else:
            texts = self.get_bows(corpus_path, corpus_file_extension)

        self.add_dictionary(texts)
        self.add_corpus(texts)
        self.add_lsi()
        self.add_index()
        with open(self.log_filename, 'a') as log_file:
            log_file.write('Dictionary contains {} words.'.format(
                self.dictionary_len))
            log_file.write("\n")

        """
        if spell_check is True:
            print "Adding spell checker."
            tokens = ''
            for text in texts:
                for token in texts:
                    tokens += str(token)
            thought_construct.add_corrector(tokens)
        """

    def parse_specific(self, corpus_path, corpus_file_extension):
        """
        Parse specific (hard-coded) corpora. Each corpus will be parsed in
        a different way, corresponding to its particular format.

        :param corpus_path: Path to the corpora.
        :param corpus_file_extension: File extension of corpora files.
        :return: bag of words array.
        """
        texts = []
        # texts = self.get_bows(corpus_path, corpus_file_extension)

        # Now process the corpora from the Bag of Words dataset.
        with open(self.log_filename, 'a') as log_file:
            # XXX: Need to figure out a way to log the specific files that
            # are processed.
            # texts += parsebows.parse_bows(corpus_path)
            bow_list = parsebows.parse_bows(corpus_path, log_file)
            for bow_text in bow_list:
                texts += [self.parse_document(bow_text)]
            """
            # Process bag of words from New York Times dataset.
            texts += parsebows.process_nyt(corpus_path, log_file)
            # Process bag of words from Enron emails dataset.
            texts += parsebows.process_enron(corpus_path, log_file)
            # Process bag of words from Daily Kos blog dataset.
            texts += parsebows.process_kos(corpus_path, log_file)
            """

            # Final count
            log_file.write('Prcoessed {} texts.'.format(str(len(texts))))
            log_file.write("\n")

        return texts

    def get_bows(self, corpus_path, extension):
        """
        Read in all the documents in this directory and all its
        subdirectories. Only read files with the given extension. This is
        because corpora often come bundled with various metadata files.

        This function can divide up the text in each file into paragraphs. This
        function approximates that by dividing the text up when two newline
        characters occur one after the other.

        Warning: This function builds up a massive list, so it can be memory
        intensive.
        """
        logging.debug('Get BOWs')
        doc_list = eec_utils.list_a_file_type(corpus_path, extension)
        texts = []
        text_count = 0
        doc_count = 0
        # print 'BOWs by paragraph'

        # Log each filename processed.
        with open(self.log_filename, 'a') as log_file:
            for docname in doc_list:
                with open(docname, 'rU') as doc_file:
                    """
                    document = eec_utils.read_a_doc(doc_file)
                    new_texts = self.get_texts_from_doc(document)
                    """
                    # print 'Getting BOWs by paragraph:'
                    # new_texts = self.get_texts_from_doc(doc_file)
                    # print 'Process 1 text = 1 file.'
                    try:
                        new_texts = self.get_all_text_from_doc(doc_file)
                    except:
                        print "An error occurred with", docname
                        continue
                    texts += new_texts
                    text_count += len(new_texts)

                doc_count += 1
                if doc_count % 5000 == 0:
                    print '...', doc_count

                log_file.write(docname)
                log_file.write("\n")

            log_file.write('Processed {} texts from {} files.'.format(
                text_count, doc_count))
            log_file.write("\n")

        print 'Done reading'
        print 'Processed {} texts from {} files.'.format(text_count, doc_count)
        # remove words that appear only once
        from collections import defaultdict
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1

        texts = [[token for token in text if frequency[token] > 1]
                 for text in texts]

        """
        from pprint import pprint # pretty‐printer
        pprint(texts)
        """
        return texts

    def get_all_text_from_doc(self, document):
        """
        :param document: File handler object.
        :return: bow: An array of words (which are string objects).
        """
        bow = [self.parse_document(document.read())]

        return bow

    def parse_document(self, document):
        word_list = []
        for word in document.lower().split():
            # XXX: Word normalizing:
            # Turn word into a string.
            try:
                # word = word.decode('utf8').encode('ascii', 'ignore')
                word = word.decode('utf8').encode('ascii', 'replace')
            except:
                pass
            # Strip html stuff.
            try:
                word = hparser.unescape(word)
            except:
                print "hparser didn't like {} with type {}".format(word,
                                                                   type(word))
                raise
            # Turn word into utf-8, if necessary.
            try:
                word = word.decode('utf8')
            except:
                # word probably was already utf-8
                pass
            word = unicodedata.normalize('NFKD', word)
            # Turn word back into a string.
            try:
                word = word.encode('utf8')
            except:
                # word probably was already utf-8
                pass
            """Cleaning notes:
            Using if not word.isdigit() instead of if word.isalpha().
            That's because isalpha() will be false if there's punctuation.
            XXX: Get rid of punctuation entirely? Currently only strips them
                from the ends.
            """
            word = word.replace("'s", "")
            # word = word.strip("',.!?()\"/\\")
            word = word.strip(string.punctuation)
            if word == '':
                continue
            if not word.isdigit() and \
                    word not in STOPLIST:
                if self.lemmatizer:
                    word = self.lemmatizer.lemmatize(word)
                word_list.append(word)
        return word_list

    def get_texts_as_bow(self, documents):
        texts = []
        for document in documents:
            word_list = self.parse_document(document)
            texts.append(word_list)
        # pprint(texts)

        # remove words that appear only once
        from collections import defaultdict
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1

        texts = [[token for token in text if frequency[token] > 1]
                 for text in texts]

        """
        from pprint import pprint # pretty‐printer
        pprint(texts)
        """
        return texts

# end of CorpusProcessor class
