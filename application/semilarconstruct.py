# -*- coding: utf-8 -*-
"""semilarconstruct.py
Defines the SemilarConstruct class.

The class for thought constructs based on Semilar models.
http://deeptutor2.memphis.edu/Semilar-Web/public/lsa-models-lrec2014.html
Stefanescu, D., Banjade, R., and Rus, V. (2014). Latent Semantic
    Analysis Models on Wikipedia and TASA. The 9th Language
    Resources and Evaluation Conference (LREC 2014), 26-31 May,
    Reykjavik, Iceland.

Inherits from ThoughtConstruct class.

Created on Wed Nov 04 08:46:23 2015

@author: Eric
"""
import logging
from zipfile import ZipFile
from random import sample
from os.path import isfile
from array import array

from scipy.spatial.distance import cosine

# Custom modules
from thoughtconstruct import ThoughtConstruct
from eec_utils import clean_word


class SemilarConstruct(ThoughtConstruct):
    """This is the class for thought constructs based on Semilar models."""

    def __init__(self,
                 construct_name,
                 construct_path,
                 dict_filename='voc',
                 lsi_filename='lsaModel',
                 load_zip=False,
                 num_topics=None,
                 lemmatize=False,
                 s3_key_voc=None,
                 s3_key_lsa=None):
        self.name = construct_name
        print "Constructing Semilar Thought Construct:", self.name
        self.construct_path = construct_path
        """
        if not self.construct_path.endswith('/'):
            self.construct_path += '/'
        """
        self.s3_key_voc = s3_key_voc
        self.s3_key_lsa = s3_key_lsa
        self.load_zip = load_zip
        if self.s3_key_voc or self.s3_key_lsa:
            if not (self.s3_key_voc and self.s3_key_lsa):
                return None
            print 'Retrieving from S3'
        else:
            if self.load_zip:
                filename = self.construct_path + self.name
                if isfile(filename + '.zip'):
                    self.filename = filename + '.zip'
                elif isfile(filename + '.ZIP'):
                    self.filename = filename + '.ZIP'
                else:
                    print 'Error! Zip file not found!'
                    return None
            else:
                self.filename = self.construct_path + self.name
        self.dictionary_filename = dict_filename
        self.lsi_filename = lsi_filename
        self.dictionary = {}
        self.dictionary_len = 0
        self.lsi = {}
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
        print("LSI model filename is:", self.lsi_filename)

    def print_dictionary(self):
        print self.dictionary

    def load_all(self):
        if self.s3_key_voc:
            with open(self.s3_key_voc.key, 'w+') as dictf, \
                    open(self.s3_key_lsa.key, 'w+') as lsif:
                self.s3_key_voc.get_contents_to_file(dictf)
                self.s3_key_lsa.get_contents_to_file(lsif)
                dictf.seek(0)
                lsif.seek(0)
                print 'Retrieved. Now processing data.'
                self.process_semilar_files(dictf, lsif)
            """
            voc_str = self.s3_key_voc.read()
            voc_lines = voc_str.splitlines()

            lsa_str = self.s3_key_lsa.read()
            lsa_lines = lsa_str.splitlines()
            print 'Retrieved. Now processing data.'
            self.process_semilar_files(voc_lines, lsa_lines)
            """
            return

        if self.load_zip:
            with ZipFile(self.filename, 'r') as zipf:
                dictf = zipf.open(self.name + '/' + self.dictionary_filename)
                lsif = zipf.open(self.name + '/' + self.lsi_filename)
                self.process_semilar_files(dictf, lsif)
        else:
            with open(self.construct_path + self.dictionary_filename, 'r') \
                as dictf, \
                    open(self.construct_path + self.lsi_filename, 'r') as lsif:
                self.process_semilar_files(dictf, lsif)

    def process_semilar_files(self, dictf, lsif):
        for word, vec_string in zip(dictf, lsif):
            word = word.strip()
            vec_string = vec_string.strip()
            word = clean_word(word)
            self.lsi[word] = self.trans_vec_string(vec_string)
            # This dictionary will just be keyed by the word itself.
            # self.dictionary[word] = word
        self.dictionary_len = len(self.lsi)

    def trans_vec_string(self, vec_string):
        float_vec = array('f')
        for coord in vec_string.split():
            float_vec.append(float(coord))
        return float_vec

    def query2bow(self, query):
        """Converts query word list into appropriate bag of words.
        For Semilar, no processing is necessary.
        """
        return query

    def word2lsi(self, word):
        """Converts a bag of words into an LSI space vector."""
        # XXX: Currently, just run analyses for the first word.
        try:
            lsi_vec = self.lsi[word]
        except KeyError:
            # Word isn't in the dictionary
            logging.debug('Cosine similarity ValueError')
            return None
        except IndexError:
            # XXX: Something's wrong with the bow
            logging.debug('IndexError: {}'.format(word))
            # print 'IndexError: {}'.format(bow)
            return None
        return lsi_vec

    def bow2lsi(self, bow):
        """Converts a bag of words into an LSI space vector."""
        unknown_count = 0
        word_count = len(bow)
        avg_vec = None
        for word in bow:
            this_vec = self.word2lsi(word)
            try:
                avg_vec = [x + y for x, y in zip(avg_vec, this_vec)]
            except TypeError:
                # This happens at the beginning, when avg_vec = None
                if not avg_vec:
                    avg_vec = this_vec

                if not this_vec:
                    unknown_count += 1
            except:
                raise

        word_count -= unknown_count
        try:
            avg_vec = [x/word_count for x in avg_vec]
        except TypeError:
            avg_vec = None
        except:
            raise
        return avg_vec

    def query_lsi(self, text):
        """Calculate lsi vector."""
        """
        if self.lemmatizer:
            text = self.lemmatizer.lemmatize(text)
        if self.corrector:
            text = self.corrector.correct(text)
        """
        # text = text.lower()
        bow = self.query2bow(text.lower().split())
        vec_lsi = self.bow2lsi(bow)
        return vec_lsi

    def query_single(self, text):
        # XXX: Not currently implemented here.
        return None

    def query_pair_lsi(self, text1, text2):
        # Compute the semantic space position of the first word.
        vec_lsi1 = self.query_lsi(text1)
        # print text1, "semantic space vector:", vec_lsi1
        # Compute the semantic space position of the second word.
        vec_lsi2 = self.query_lsi(text2)
        # print text2, "semantic space vector:", vec_lsi2
        try:
            """
            # Compute the Euclidean distance between the two words' positions
            # in the semantic space.
            result = euclidean_distance.euclidean_distance_vec_lsi(vec_lsi1,
                                                                   vec_lsi2)
            """

            # Compute the cosine similarity
            result = 1 - cosine(vec_lsi1, vec_lsi2)
        except ValueError:
            # A ValueError: Probably one of the words wasn't in the dictionary.
            logging.debug('Cosine similarity ValueError')
            return None
        except:
            # Other exceptions.
            # logging.exception('Cosine similarity unknown exception')
            logging.debug('Cosine similarity unknown exception')
            # XXX: Eventually need to figure out the possible exceptions.
            # raise
            return None
        return result

    def query_pair_lsi_distance(self, text1, text2):
        # Compute the semantic space position of the first word.
        vec_lsi1 = self.query_lsi(text1)
        # print text1, "semantic space vector:", vec_lsi1
        # Compute the semantic space position of the second word.
        vec_lsi2 = self.query_lsi(text2)
        # print text2, "semantic space vector:", vec_lsi2
        try:
            # Compute the cosine distance
            result = cosine(vec_lsi1, vec_lsi2) / 2
        except ValueError:
            # A ValueError: Probably one of the words wasn't in the dictionary.
            logging.debug('Cosine similarity ValueError')
            return None
        except:
            # Other exceptions.
            # logging.exception('Cosine similarity unknown exception')
            logging.debug('Cosine similarity unknown exception')
            # XXX: Eventually need to figure out the possible exceptions.
            # raise
            return None
        return result

    def get_sampled_avg(self, word, num=400):
        if num >= self.dictionary_len:
            return None
        vec_lsi = self.query_lsi(word)
        if not vec_lsi:
            logging.debug('get_sampled_avg(): No vector. Word not found')
            return None
        # Make sure we don't get the word that we're querying about.
        # Make sure we don't get stuck in an infinite loop.
        iterations = 0
        while True:
            random_words = sample(self.lsi, num)
            if word not in random_words:
                break
            # Bail if we've done more than 1000 iterations.
            iterations += 1
            if iterations >= 1000:
                return None
        # print random_words
        total = 0.0
        count = 0
        for random_word in random_words:
            similarity = self.query_pair_lsi(word, random_word)
            if not similarity:
                # print 'No similarity calculated:', random_word
                continue
            total += similarity
            count += 1
        # print 'count', count
        # print 'total', total
        if count == 0:
            return None
        return total/count

    def get_random_word(self):
        """Return a random word from the dictionary."""
        return sample(self.lsi, 1)[0]
