# -*- coding: utf-8 -*-
"""process_sbcorpus.py
Process the transcript files of the Santa Barbara Corpus.

TODO

Created on Fri Sept 11 13:32:00 2015

@author: Eric
"""
import sys
import getopt
import logging
import time
import os
import re

from HTMLParser import HTMLParser

# Custom modules
import eec_utils
import gzip

__author__ = 'eec'

DEBUG = False
INFILENAME = 'c:/Users/Eric/Downloads/movies.txt.gz'
OUTFILENAME = 'output.txt'
MAXFILESIZE = 1000000

# Setup some defaults
INPUT_DIR = 'c:/Downloads/'
OUTPUT_DIR = 'c:/bin/creativity/corpus/movies/'
INPUT_EXT = '.txt'
OUTPUT_EXT = '.txt'


class MLStripper(HTMLParser):
    # Based on:
    # http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def main(argv):
    arg_dict = parseArgs(argv)
    extract_all_files(arg_dict['input_dir'],
                      arg_dict['input_ext'],
                      arg_dict['output_dir'],
                      arg_dict['output_ext'])


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

    logging.basicConfig(filename="log_process_sbcorpus.txt",
                        level=log_level,
                        filemode="w")
    logging.info('process_sbcorpus start: ' + time.strftime("%c"))

    return arg_dict

# LET'S GO!!!
if __name__ == "__main__":
    main(sys.argv[1:])
