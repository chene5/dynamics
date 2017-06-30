# -*- coding: utf-8 -*-
"""thoughtconstruct.py
Defines the ThoughtConstruct class.

The parent class for all types of thought constructs.

Created on Wed Nov 04 08:46:23 2015

@author: Eric
"""
import logging
from heapq import heappush, heappushpop
from random import sample
from scipy.spatial.distance import cosine


class ThoughtConstruct:
    """This is the class for the thought construct."""

    def __init__(self,
                 dict_name,
                 dict_path,
                 num_topics=None,
                 lemmatize=False):
        self.name = dict_name
        self.dict_path = dict_path
        self.filename = self.dict_path + self.name
        self.dictionary_filename = self.dict_path + self.name
        self.lsi_filename = None
        self.dictionary = None
        self.dictionary_len = 0
        self.lsi = None
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
        print("Construct", self.name, "located at ", self.dict_path)
        print("Dictionary filename is:", self.dictionary_filename)
        print("LSI model filename is:", self.lsi_filename)

    def print_dictionary(self):
        print self.dictionary

    def load_all(self):
        self.dictionary = None
        self.dictionary_len = 0
        self.lsi = None

    def interactive_query(self):
        word_1 = raw_input(
            '{}==> What is the first word? '.format(self.name)).lower()
        word_2 = raw_input(
            '{}==> What is the second word? '.format(self.name)).lower()
        result = self.query_pair_lsi(word_1, word_2)
        print 'The cosine similarity is', result

    def query2bow(self, query):
        """Converts query word list into appropriate bag of words."""
        # This is the gensim version:
        # return self.dictionary.doc2bow(query.lower().split())
        pass

    def bow2lsi(self, bow):
        """Converts a bag of words into an LSI space vector."""
        # This is the gensim version:
        # return self.lsi[bow]  # convert the query to LSI space
        pass

    def query_lsi(self, text):
        """
        text = text.lower()
        if self.lemmatizer:
            text = self.lemmatizer.lemmatize(text)
        if self.corrector:
            text = self.corrector.correct(text)
        vec_bow = self.query2bow(text.lower().split())
        vec_lsi = self.bow2lsi(vec_bow)
        return vec_lsi
        """
        pass

    def query_single(self, text):
        vec_lsi = self.query_lsi(text)
        # XXX: At the moment this cosine_sim_origin() function is shaky.
        try:
            # XXX: Also calculate the distance from the 1 spot
            origin_distance = sim_origin(vec_lsi)
            # print 'Distance from the 1 spot is:', origin_distance
        except:
            origin_distance = None
        return origin_distance

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
            result = cosine_sim(vec_lsi1, vec_lsi2)
        except ValueError:
            # A ValueError: Probably one of the words wasn't in the dictionary.
            # logging.debug('Cosine similarity ValueError')
            return None
        except:
            # Other exceptions.
            # logging.exception('Cosine similarity unknown exception')
            logging.debug('Cosine similarity unknown exception')
            # XXX: Eventually need to figure out the possible exceptions.
            # raise
            return None
        return result

    def query_list(self, word_list):
        # print 'word list:', word_list
        results_matrix = [[self.query_pair_lsi(word1, word2)
                           for word1 in word_list] for word2 in word_list]
        # print(results_matrix)
        return results_matrix

    def query_single_to_list(self, word, word_list):
        # print 'word:', word
        # print 'word list:', word_list
        results_vector = [self.query_pair_lsi(word, curr_word)
                          for curr_word in word_list]
        # print(results_vector)
        return results_vector

    def query_pair_lsi_distance(self, text1, text2):
        # Compute the semantic space position of the first word.
        vec_lsi1 = self.query_lsi(text1)
        # Compute the semantic space position of the second word.
        vec_lsi2 = self.query_lsi(text2)
        try:
            # Compute the cosine distance
            result = cosine_distance(vec_lsi1, vec_lsi2)
        except ValueError:
            # A ValueError: Probably one of the words wasn't in the dictionary.
            # logging.debug('Cosine similarity ValueError')
            return None
        except:
            # Other exceptions.
            # logging.exception('Cosine similarity unknown exception')
            logging.debug('Cosine distance unknown exception')
            # XXX: Eventually need to figure out the possible exceptions.
            # raise
            return None
        return result

    def query_list_distance(self, word_list):
        # print 'word list:', word_list
        results_matrix = [[self.query_pair_lsi_distance(word1, word2)
                           for word1 in word_list] for word2 in word_list]
        # print(results_matrix)
        return results_matrix

    def get_closest(self, word, num=10, iterations=None):
        if word not in self.dictionary.values():
            return None
        closest_words = []
        # Start smaller than the smallest possible value.
        # Cosine similarity is between -1 and 1.
        curr_min_sim = -2.0
        count = 0
        i = 0
        for comparison in self.dictionary.values():
            # print 'comparing {} and {}'.format(word, comparison)
            try:
                similarity = self.query_pair_lsi(word, comparison)
                # Let's do one more than the number requested.
                # This is because the word will have the highest similarity
                # with itself. So the list will also contain the word itself,
                # which is not useful.
                # XXX: Might be sensible to pop the target word from the
                # result list.
                if count <= num:
                    heappush(closest_words, (similarity, comparison))
                    count += 1
                    # print 'current minimum on heap:', closest_words[0]
                    curr_min_sim = closest_words[0][0]
                    # print curr_min_sim
                else:
                    if similarity > curr_min_sim:
                        heappushpop(closest_words,
                                    (similarity, comparison))
                        # print 'current minimum on heap:', closest_words[0]
                        curr_min_sim = closest_words[0][0]
                        # print curr_min_sim
            except:
                print 'ERROR!'
                logging.exception('get_closest(): Comparisons failed.')
                pass

            # Check if we're just doing a limited number of iterations.
            if iterations:
                i += 1
                if i >= iterations:
                    break

        """
        biggest = max(closest_words)
        if biggest[1] != word:
            print '{} was more similar than itself.'.format(biggest[1])
            pass
        word_list = sorted(closest_words, reverse=True)[:num]
        """
        word_list = sorted(closest_words, reverse=True)
        return word_list

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
            random_words = sample(self.dictionary.values(), num)
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
        return sample(self.dictionary.values(), 1)[0]

    def compare_random(self, word=None):
        if not word:
            word = self.get_random_word()
        # Make sure we don't get stuck in an infinite loop.
        iterations = 0
        while True:
            random_word = self.get_random_word()
            similarity = self.query_pair_lsi(word, random_word)
            if similarity:
                return similarity, word, random_word
            # Bail if we've done more than 1000 iterations.
            iterations += 1
            if iterations >= 1000:
                return None, word, random_word


def cosine_sim(vec_lsi_1, vec_lsi_2):
    vector1 = []
    vector2 = []

    # Create vector 1.
    for coord in vec_lsi_1:
        # print coord[1]
        vector1.append(coord[1])

    # Create vector 2.
    for coord in vec_lsi_2:
        # print coord[1]
        vector2.append(coord[1])

    cosine_similarity = 1 - cosine(vector1, vector2)

    return cosine_similarity


def cosine_distance(vec_lsi_1, vec_lsi_2):
    vector1 = []
    vector2 = []

    # Create vector 1.
    for coord in vec_lsi_1:
        # print coord[1]
        vector1.append(coord[1])

    # Create vector 2.
    for coord in vec_lsi_2:
        # print coord[1]
        vector2.append(coord[1])

    flow = cosine(vector1, vector2)

    return flow


def sim_origin(vec_lsi_1):
    vector1 = []
    vector2 = []

    # Create vector 1.
    for coord in vec_lsi_1:
        vector1.append(1)

    # Create vector 2.
    for coord in vec_lsi_1:
        vector2.append(coord[1])

    cosine_similarity = 1 - cosine(vector1, vector2)
    # print 'version 2:', cosine_similarity

    return cosine_similarity
