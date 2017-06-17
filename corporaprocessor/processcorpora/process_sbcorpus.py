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

# Custom modules
import eec_utils

__author__ = 'eec'

DEBUG = False
INFILENAME = 'test.trn'
OUTFILENAME = 'output.txt'
MAXFILESIZE = 1000000

# Setup some defaults
INPUT_DIR = 'c:/bin/creativity/corpora/sbcorpus/'
OUTPUT_DIR = 'c:/bin/creativity/corpora/sbcorpus_out/'
INPUT_EXT = '.trn'
OUTPUT_EXT = '.txt'


def main(argv):
    arg_dict = parseArgs(argv)
    process_trn_files(arg_dict['input_dir'],
                      arg_dict['input_ext'],
                      arg_dict['output_dir'],
                      arg_dict['output_ext'])


def process_trn_files(input_dir, input_ext, output_dir, output_ext):
    logging.debug('Begin process_trn_files()')

    # file_list = eec_utils.list_all_files_in_dirs('input_dir')
    file_list = eec_utils.list_a_file_type(input_dir, input_ext)

    file_count = 0

    # Check if the directory exists. If not, make it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for input_filename in file_list:
        filename = os.path.basename(input_filename)
        base_filename = os.path.splitext(filename)[0]
        output_filename = output_dir + base_filename + '.txt'
        # print output_filename
        with open(input_filename, 'r') as trn_file, open(output_filename, 'w') as out_file:
            file_count += 1
            for line in trn_file:
                match = re.search(r'\t.*\t(.*)', line)
                if match:
                    speech = match.group(1)
                    # print 'full speech', speech
                    cleaned_speech = speech
                    cleaned_speech = re.sub(r'(\[\d*|\d*\]|<\w*|\w*>|\(.*\)|XXX|XX)', '', cleaned_speech)
                    cleaned_speech = re.sub(r'(\.|<|>|@|,|=|--|!|\?|~|%)', '', cleaned_speech)
                    # print cleaned_speech
                else:
                    # print 'no match'
                    pass
                out_file.write(cleaned_speech)
                out_file.write('\n')

    print "Finished writing {} files.".format(file_count)


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