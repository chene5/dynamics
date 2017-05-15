# -*- coding: utf-8 -*-
"""process_corpora.py
Process the corpora for the thought walking.

TO DO:
Lemmatize.
Setup stoplist.
Spell checking.
XXX

Created on Mon Jun 29 11:24:53 2015

@author: Eric Chen
"""
import os
import sys
import getopt
import logging
import time
import csv

import pprint

# Custom modules
from corporaprocessor.corpusprocessor import CorpusProcessor
from application.creativityconstruct import CreativityConstruct

__author__ = 'Eric Chen'

"""Defaults for Windows"""
_default_dict_path = 'c:/bin/creativity/constructs/'
_corpus_root = 'c:/bin/creativity/corpora/'

"""Defaults for Mac
_default_dict_path = '/Users/eric/Documents/constructs/'
_corpus_root = '/Users/eric/Documents/'
"""


def main(argv):
    parse_args(argv)
    interactive_processing()


def interactive_processing():
    logging.debug('Begin interactive_processing()')
    dict_path = _default_dict_path
    creativity_construct = None
    while True:
        print '*** What shall we do? ***'
        print '* [create] construct'
        print '* [open] a construct'
        print '* [query] construct'
        print '* [closest] words'
        print '* [list] query'
        print '* [read] list'
        print '* [check] constructs'
        print '* [change] directory'
        print '* [exit]'
        try:
            command = raw_input('==> What now [open]? ').lower()
        except KeyboardInterrupt:
            print 'Goodbye!'
            # sys.exit()
            return

        try:
            if command == 'check':
                check_dictionaries(dict_path)
            if command == 'change':
                dict_path = change_directory(dict_path)
            if command == 'open' or command == '':
                creativity_construct = open_construct(dict_path)
            if command == 'query':
                if not creativity_construct:
                    print "A creativity construct hasn't been loaded yet!"
                    continue
                query_construct(creativity_construct)
            if command == 'closest':
                if not creativity_construct:
                    print "A creativity construct hasn't been loaded yet!"
                    continue
                query_closest(creativity_construct)
            if command == 'list':
                if not creativity_construct:
                    print "A creativity construct hasn't been loaded yet!"
                    continue
                list_query(creativity_construct)
            if command == 'read':
                if not creativity_construct:
                    print "A creativity construct hasn't been loaded yet!"
                    continue
                read_list(creativity_construct, dict_path)
            if command == 'create':
                process_corpora()
        except KeyboardInterrupt:
            print 'OK, nevermind!'

        if command == 'exit':
            print 'Goodbye!'
            return
        print


def open_construct(dict_path):
    construct_dict = check_dictionaries(dict_path)
    message = '==> Which construct number would you like to load? '
    construct_input = raw_input(message).lower()
    if construct_input == '':
        print 'Oops no construct name'
        return None
    try:
        construct_name = construct_dict[int(construct_input)][0]
        construct_path = construct_dict[int(construct_input)][1]
    except KeyError:
        print "Oops that construct number doesn't exist"
        return None

    print 'Opening {} from {}'.format(construct_name, construct_path)
    """
    return None
    """
    creativity_construct = CreativityConstruct(construct_name,
                                               construct_path)
    creativity_construct.description()
    return creativity_construct


def check_dictionaries(dict_path):
    return check_files(dict_path, '.dict')


def check_files(pathname, extension):
    print 'Here are the files in {}'.format(pathname)

    model_num = 1
    model_dict = {}
    for (dirpath, dirnames, filenames) in os.walk(pathname):
        for filename in filenames:
            # filename = eec_utils.get_filename(filename)
            # filename = os.path.splitext(filename)[0]
            fname, ext = os.path.splitext(filename)
            if ext == extension:
                print '{} >>> {}'.format(model_num, fname)
                if dirpath.endswith('/'):
                    modelpath = dirpath
                else:
                    modelpath = dirpath + '/'
                model_dict[model_num] = [fname, modelpath]
                model_num += 1

    return model_dict


def check_dictionaries_in_dir(dict_path):
    print 'Here are the files in {}'.format(dict_path)

    model_num = 1
    model_list = {}
    file_list = os.listdir(dict_path)
    for filename in file_list:
        # filename = eec_utils.get_filename(filename)
        # filename = os.path.splitext(filename)[0]
        fname, ext = os.path.splitext(filename)
        if ext == '.dict':
            print '{} >>> {}'.format(model_num, fname)
            model_list[model_num] = fname
            model_num += 1

    return model_list


def query_construct(creativity_construct):
    while True:
        try:
            word_1 = raw_input('{} >>> What is the first word? '.format(
                creativity_construct.name)).lower()
        except KeyboardInterrupt:
            print 'Done with querying!'
            return
        try:
            word_2 = raw_input(
                '{} >>> What is the second word (optional)? '.format(
                    creativity_construct.name)).lower()
        except KeyboardInterrupt:
            print 'Done with querying!'
            return

        if word_2 != '':
            result = creativity_construct.query_pair_lsi(word_1, word_2)
            print 'The cosine similarity is', result
        else:
            result = creativity_construct.query_single(word_1)
            print 'Origin calculation =', result
            sampled_avg = creativity_construct.get_sampled_avg(word_1)
            print 'Sampled average is =', sampled_avg
            # result = creativity_construct.query_lsi(word_1)
            # result = creativity_construct.query_index(word_1)
            # print(list(enumerate(result)))


def query_closest(creativity_construct):
    while True:
        try:
            word = raw_input('{} >>> What is the word? '.format(
                creativity_construct.name)).lower()
        except KeyboardInterrupt:
            print 'Done with querying!'
            return

        closest = creativity_construct.get_closest(word)
        print "Closest words are:"
        print closest


def list_query(creativity_construct):
    word_list = []
    while True:
        try:
            word = raw_input(
                '{} >>> Add a word: '.format(creativity_construct.name)).lower()
            if word != '':
                word_list.append(word)
                continue
        except KeyboardInterrupt:
            print 'Done with list query!'
            return

        query_list(creativity_construct, word_list)
        word_list = []


def get_file_info(pathname, extension):
    file_dict = check_files(pathname, extension)
    name_input = raw_input('==> Which file would you like to load? ').lower()
    if name_input == '':
        print 'Oops no file name'
        return
    try:
        file_name = file_dict[int(name_input)][0]
        file_path = file_dict[int(name_input)][1]
    except KeyError:
        print "Oops that file doesn't exist"
        return
    # print 'Opening {} from {}'.format(file_name, file_path)

    """
    file_info = (file_name, file_path)
    return file_info
    """
    return file_name, file_path


def read_list(creativity_construct, path):
    file_name, file_path = get_file_info(path, '.txt')
    print 'Opening {} from {}'.format(file_name, file_path)

    with open(file_path + file_name + '.txt', 'r') as f:
        for line in f:
            word_list = line.split()
            query_list(creativity_construct, word_list)


def query_list(creativity_construct, word_list):
    pp = pprint.PrettyPrinter()
    result = creativity_construct.query_list(word_list)
    print 'The similarity matrix is:'
    pp.pprint(result)
    output_csv(word_list, result)
    return result


def output_csv(word_list, result):
    try:
        csv_file = csv.writer(open('test.csv', 'a'))
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        return

    full_word_list = [' '] + word_list
    csv_file.writerow(full_word_list)
    index = 0
    for row in result:
        fullrow = [word_list[index]]
        index += 1
        fullrow += row
        csv_file.writerow(fullrow)


def change_directory(dict_path):
    print
    print 'The current construct path is:', dict_path

    dict_path_input = raw_input(
        '==> Change construct path [{}]? '.format(dict_path)).lower()
    if dict_path_input != '':
        dict_path = dict_path_input
    return dict_path


def process_corpora():
    logging.debug('Begin process_corpora()')
    print "*** Process corpora ***"
    date_time = time.strftime("model_%m-%d-%y_%H%M")

    dict_name = raw_input(
        '==> What is the construct name [{}]? '.format(date_time)).lower()
    if dict_name == '':
        dict_name = date_time
    print 'Construct name: ', dict_name

    dict_path = _default_dict_path + dict_name + '/'
    dict_subpath = raw_input(
        '==> What is the construct path [{}]? '.format(dict_path)).lower()
    if dict_subpath != '':
        if not dict_subpath.endswith('/'):
            dict_subpath += '/'
        dict_path = _default_dict_path + dict_subpath
    print "Construct path: ", dict_path

    corpus_path = _corpus_root
    corpus_subpath = raw_input(
        '==> What is the corpus path [{}]? '.format(corpus_path)).lower()
    if corpus_subpath != '':
        # corpus_path = '2pac/'
        if not corpus_subpath.endswith('/'):
            corpus_subpath += '/'
        corpus_path = corpus_path + corpus_subpath
    print "Corpus path: ", corpus_path

    corpus_extension = raw_input(
        '==> What is the file extension [.txt]? ').lower()
    if corpus_extension == '':
        corpus_extension = '.txt'
    else:
        if not corpus_extension.startswith('.'):
            corpus_extension = '.' + corpus_extension

    print "Corpus extension: ", corpus_extension

    parse_spec_str = 'false'
    parse_spec_str = raw_input(
        '==> Parse specific [{}]? '.format(parse_spec_str)).lower()
    if parse_spec_str == 'true':
        parse_specific = True
        print "True: Parsing specific corpora"
    else:
        parse_specific = False
        print "False: Not parsing specific corpora"

    num_topics = 25
    num_input = raw_input(
        '==> How many topics [{}]? '.format(num_topics)).lower()
    if num_input != '':
        num_topics = int(num_input)
    print "Number of topics: ", num_topics

    # Check if the directory exists. If not, make it.
    if not os.path.exists(dict_path):
        os.makedirs(dict_path)

    corpus_processor = CorpusProcessor(dict_name,
                                       dict_path,
                                       corpus_path,
                                       corpus_file_extension=corpus_extension,
                                       specific_corpora=parse_specific,
                                       num_topics=num_topics)

    # Get the initial description of the Corpus Processor object.
    corpus_processor.description()

    # Work interactively
    corpus_processor.interactive()

    # Get the latest description of the Corpus Processor object.
    corpus_processor.description()


def first_test():
    print 'Do some stuff'
    pp = pprint.PrettyPrinter()

    # remove words that appear only once
    from collections import defaultdict
    texts = [['hi', "what's", 'up'], ['bye'], ['hi']]
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    pp.pprint(frequency)

    texts = [[token for token in text if frequency[token] > 1]
             for text in texts]

    pp.pprint(texts)
    # process_corpora()


def usage():
    print __doc__


# Parse through the command-line arguments
def parse_args(argv):
    # Set the default logging level to INFO
    log_level = logging.INFO
    global _default_dict_path
    global _corpus_root

    try:
        opts, args = getopt.getopt(argv,
                                   "hdc:t:",
                                   ["help",
                                    "debug",
                                    "corpus",
                                    "constructs"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            log_level = logging.DEBUG
        elif opt in ("-c", "--corpus"):
            if not arg.endswith('/'):
                arg += '/'
            _corpus_root = arg
            print("Default corpus directory:", _corpus_root)
        elif opt in ("-t", "--constructs"):
            if not arg.endswith('/'):
                arg += '/'
            _default_dict_path = arg
            print("Default constructs directory:", _default_dict_path)

    logging.basicConfig(filename="log_process_corpora.txt",
                        level=log_level,
                        filemode="w")
    logging.info('process_corpora start: ' + time.strftime("%c"))
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-2s: %(levelname)-2s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


# LET'S GO!!!
if __name__ == "__main__":
    main(sys.argv[1:])
