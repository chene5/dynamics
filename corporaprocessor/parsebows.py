# -*- coding: utf-8 -*-
"""parsebows.py
Mini-module that processes the bag of words dataset. Located here:
https://archive.ics.uci.edu/ml/datasets/Bag+of+Words

The files are gzipped.

TODO:


Created on Tue Sep 22 16:07:51 2015

@author: Eric Chen
"""
import sys
import getopt
import logging
import time
import os
import re

# Custom modules
import gzip

__author__ = 'Eric Chen'

DEBUG = False

NUM_HEADER_LINES = 3

"""Windows locations
NYT_DICT_FILE = 'c:/bin/BoW/docword.nytimes.txt.gz'
NYT_VOCAB_FILE = 'c:/bin/BoW/vocab.nytimes.txt'

KOS_DICT_FILE = 'c:/bin/BoW/docword.kos.txt.gz'
KOS_VOCAB_FILE = 'c:/bin/BoW/vocab.kos.txt'

ENRON_DICT_FILE = 'c:/bin/BoW/docword.enron.txt.gz'
ENRON_VOCAB_FILE = 'c:/bin/BoW/vocab.enron.txt'
"""
NYT_DICT_FILE = 'docword.nytimes.txt.gz'
NYT_VOCAB_FILE = 'vocab.nytimes.voc'

KOS_DICT_FILE = 'docword.kos.txt.gz'
KOS_VOCAB_FILE = 'vocab.kos.voc'

ENRON_DICT_FILE = 'docword.enron.txt.gz'
ENRON_VOCAB_FILE = 'vocab.enron.voc'

INFILENAME = 'c:/Users/Eric/Downloads/movies.txt.gz'
OUTFILENAME = 'output.txt'
MAXFILESIZE = 1000000

# Setup some defaults
INPUT_DIR = './'
OUTPUT_DIR = 'c:/bin/creativity/corpus/movies/'
INPUT_EXT = '.txt'
OUTPUT_EXT = '.txt'


def main(argv):
    # arg_dict = parseArgs(argv)
    # process_nyt()
    process_kos('/Users/Eric/Documents/corpora/')
    # process_enron()


def parse_bows(corpus_dir=INPUT_DIR, log_file=None):
    if not corpus_dir.endswith('/'):
        corpus_dir += '/'

    bow_list = []
    # Parse (some of) the BOW corpora.
    bow_list += process_nyt(corpus_dir, log_file)
    bow_list += process_kos(corpus_dir, log_file)
    bow_list += process_enron(corpus_dir, log_file)
    return bow_list


def process_nyt(corpus_dir, log_file=None):
    if not corpus_dir.endswith('/'):
        corpus_dir += '/'

    bow_list = process_bow(corpus_dir+NYT_DICT_FILE,
                           corpus_dir+NYT_VOCAB_FILE)
    # Log these files.
    if log_file:
        log_file.write('parse_bows: '+corpus_dir+NYT_DICT_FILE)
        log_file.write("\n")

    print 'Length of nyt bow list:', len(bow_list)
    return bow_list


def process_kos(corpus_dir, log_file=None):
    if not corpus_dir.endswith('/'):
        corpus_dir += '/'

    bow_list = process_bow(corpus_dir+KOS_DICT_FILE,
                           corpus_dir+KOS_VOCAB_FILE)
    # Log these files.
    if log_file:
        log_file.write('parse_bows: '+corpus_dir+KOS_DICT_FILE)
        log_file.write("\n")

    print 'Length of kos bow list:', len(bow_list)
    return bow_list


def process_enron(corpus_dir, log_file=None):
    if not corpus_dir.endswith('/'):
        corpus_dir += '/'

    bow_list = process_bow(corpus_dir+ENRON_DICT_FILE,
                           corpus_dir+ENRON_VOCAB_FILE)
    # Log these files.
    if log_file:
        log_file.write('parse_bows: '+corpus_dir+ENRON_DICT_FILE)
        log_file.write("\n")

    print 'Length of enron bow list:', len(bow_list)
    return bow_list


def load_vocab_file(vocab_filename):
    vocab = {}
    index = 1

    with open(vocab_filename, 'r') as vocab_file:
        for line in vocab_file:
            vocab[index] = line.rstrip()
            index += 1

    # print 'Read {} words.'.format(index)

    return vocab


def process_bow(docword_filename, vocab_filename):
    """Process a bag of word bags."""
    print 'Processing {} and {}'.format(docword_filename, vocab_filename)

    vocab = load_vocab_file(vocab_filename)

    docword_file = gzip.GzipFile(docword_filename)

    bow_list = []

    for i in xrange(NUM_HEADER_LINES):
        docword_file.next()

    text = ''
    current_docid = 1
    for line in docword_file:
        info = line.split()
        new_docid = int(info[0])
        word = vocab[int(info[1])]
        count = int(info[2])

        """
        print "Document {}: '{}' appears {} times.".format(new_docid,
                                                         word,
                                                         count)
        """
        if new_docid != current_docid:
            # Save all the text we have, since we're done with this document.
            bow_list.append(text)
            # Record  the next document.
            current_docid = new_docid
            # Reset the text for the new document.
            text = ''

        if word.startswith('zzz_'):
            word = word.replace('zzz_', '')
            word = word.replace('_', ' ')
        # Record this word.
        # XXX: This is awkward, but gensim just takes text documents.
        # So now we recreate the bags of words.
        for i in range(0, count):
            text += word
            text += ' '

    # Append the last text.
    if text != '':
        bow_list.append(text)

    return bow_list


def extract_all_files(input_dir, input_ext, output_dir, output_ext):
    logging.debug('Begin process_files()')

    movies = gzip.GzipFile(INFILENAME)

    line_count = 0
    review_count = 0

    # Check if the directory exists. If not, make it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = output_dir + 'review_text' + output_ext
    with open(output_filename, 'w') as out_file:
        for line in movies:
            line_count += 1
            # print line
            match = re.search(r'review/text: ', line)
            if match:
                review = re.sub(r'review/text: ', '', line)
                # print 'line {}:'.format(line_count)
                review = strip_tags(review)
                # print review
                review_count += 1
                out_file.write(review)
                out_file.write("\n\n")

    print "Finished writing files."


def usage():
    print __doc__


def parseArgs(argv):
    """Parse any command line arguments."""
    global INFILENAME
    global OUTFILENAME
    global MAXFILESIZE
    global DEBUG

    # Set the default logging level to INFO
    log_level = logging.INFO

    # This is the dictionary of arguments.
    arg_dict = {'input_dir': INPUT_DIR,
                'input_ext': INPUT_EXT,
                'output_dir': OUTPUT_DIR,
                'output_ext': OUTPUT_EXT}

    try:
        opts, args = getopt.getopt(argv,
                                   "hdi:o:x:",
                                   ["help",
                                    "debug",
                                    "input=",
                                    "output=",
                                    "max="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            log_level = logging.DEBUG
            print 'log level is at DEBUG'
            DEBUG = True
        elif opt in ("-i", "--input"):
            INFILENAME = arg
        elif opt in ("-o", "--output"):
            OUTFILENAME = arg
        elif opt in ("-x", "--max"):
            MAXFILESIZE = int(arg)

    # If this file is running as main, do logging.
    if __name__ == "__main__":
        logging.basicConfig(filename="log_parsebows.txt",
                            level=log_level,
                            filemode="w")
    logging.info('nyt_bow start: ' + time.strftime("%c"))

    return arg_dict


# LET'S GO!!!
if __name__ == "__main__":
    main(sys.argv[1:])
