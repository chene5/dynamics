# -*- coding: utf-8 -*-
"""process_corps_ii.py
Process the transcript files of the CORPS II corpus.

TODO

Created on Tue Oct 27 15:22:23 2015

@author: Eric
"""
import sys
import getopt
import logging
import time
import os

# Custom modules
from eec_utils_processor import list_a_file_type, file_to_bow

__author__ = 'eec'

DEBUG = False
INFILENAME = 'test.txt'
OUTFILENAME = 'output.txt'

# Setup some defaults
INPUT_DIR = 'c:/bin/CORPS_II/'
OUTPUT_DIR = 'c:/bin/corps_ii_out/'
INPUT_EXT = '.txt'
OUTPUT_EXT = '.txt'


def main(argv):
    arg_dict = parseArgs(argv)
    process_in_files(arg_dict['input_dir'],
                     arg_dict['input_ext'],
                     arg_dict['output_dir'],
                     arg_dict['output_ext'])


def process_in_files(input_dir, input_ext, output_dir, output_ext):
    logging.info('Begin process_in_files(): ' + input_dir)

    # file_list = eec_utils.list_all_files_in_dirs('input_dir')
    file_list = list_a_file_type(input_dir, input_ext)

    file_count = 0

    # Check if the directory exists. If not, make it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for input_filename in file_list:
        logging.info('Reading from: ' + input_filename)
        print('Reading from: ' + input_filename)
        filename = os.path.basename(input_filename)
        base_filename = os.path.splitext(filename)[0]
        # XXX: Append _out to the base filename
        output_filename = output_dir + base_filename + '_out' + output_ext
        # print output_filename
        bow = file_to_bow(input_filename,
                          raw=False,
                          exc_start='{', exc_end='}', no_http=True)
        with open(output_filename, 'w') as out_file:
            file_count += 1
            out_file.write(bow.encode('ascii', 'ignore'))
            out_file.write('\n')
            logging.info('Wrote to: ' + input_filename)

    print "Finished writing {} files.".format(file_count)
    logging.info("Finished writing {} files.".format(file_count))
    logging.info("process_in_files done at " + time.strftime("%c"))


def usage():
    print __doc__


def parseArgs(argv):
    """Parse any command line arguments."""
    global INFILENAME
    global OUTFILENAME
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
                                   "hdi:o:",
                                   ["help",
                                    "debug",
                                    "input=",
                                    "output="])
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

    logging.basicConfig(filename="log_process_corps_ii.txt",
                        level=log_level,
                        filemode="w")
    logging.info('process_corps_ii start: ' + time.strftime("%c"))

    return arg_dict

# LET'S GO!!!
if __name__ == "__main__":
    main(sys.argv[1:])
