# -*- coding: utf-8 -*-
"""datareader.py - Reads data.

Created on Tue Nov 10 07:47:23 2015

XXX:
Weird things happen if a participant repeats words.

@author: Eric Chen
"""
import sys
import getopt
import logging
import time

import datacomputer

__author__ = 'Eric Chen'

DRAMA_DATA = 'drama.csv'
FIELD_DATA = 'field.csv'


def main(argv):
    parse_args(argv)
    # p_data = read_data(DRAMA_DATA)
    read_field_data()

    print 'Done!'


def read_drama_data():
    return read_data(DRAMA_DATA, prefix='drama_')


def read_field_data():
    return read_data(FIELD_DATA, prefix='field_')


def read_data(filename, prefix=None):
    """Read raw data from RAs' manual analyses using the Boulder site.
    The file starts with a header at the very top.
    Then, for each participant, there's another header line,
    followed by the data.
    After the participant header, the cells of the first column are empty.

    :rtype: dict
    :param filename: The name of the csv file.
    :return: Dictionary of results, keyed by the participant SN#.
    """
    p_data = {}
    with open(filename) as f:
        # This first line is the header for the entire file.
        line = f.next()
        line = line.strip()
        # prev_line = line
        top_header = line.split(',')
        if not top_header:
            # Don't parse this for now.
            pass
        # Now read in per-participant data.
        while True:
            word_list = []
            all_words_data = {}
            # The first line for the participant is a header.
            try:
                line = f.next()
            except StopIteration:
                # We had previously read everything, so we're done.
                break
            line = line.strip()
            p_header = line.split(',')

            # The participant's ID # comes first.
            p_id = p_header[0]
            if not p_id:
                # This happens when the previous participant didn't answer.
                """
                print 'previous line:', prev_line
                print 'current line:', line
                print 'p header:', p_header
                print
                """
                continue
            if prefix:
                p_id = prefix + p_id
            # print 'SN #', p_id
            # The number of N/A's this p is at 28.
            try:
                p_nas = int(p_header[28])
            except ValueError:
                # This happens when an RA messes up the file.
                """
                print 'nas: previous line:', prev_line
                print 'nas: current line:', line
                print 'nas: p header:', p_header
                print
                """
                raise
            # print "NA's: #", p_nas
            # Check if this participant left everything blank.
            # XXX: Have to hard-code this.
            if p_nas == 20:
                """Don't record anything.
                p_data[p_id] = {'words': None,
                                'word_data': None,
                                'nas': None,
                                'overall': None}
                """
                continue
            # The next line after the header has both the data
            # for the first word and overall statistics.
            # prev_line = line
            try:
                line = f.next()
            except StopIteration:
                # We had previously read everything, so we're done.
                break
            line = line.strip()
            word, word_data, overall_data = parse_first_line(line.split(','))
            word_list.append(word)
            all_words_data[word] = word_data
            # Now read data for the rest of the words.
            for line in f:
                line = line.strip()
                word, word_data = parse_data_lines(line.split(','))
                if word == '':
                    """
                    print "loop's previous line:", prev_line
                    print "loop's current line:", line
                    print
                    """
                    # prev_line = line
                    break
                word_list.append(word)
                all_words_data[word] = word_data
                # prev_line = line
            # Compute per-word averages
            all_total_avg, future_total_avg, past_total_avg = \
                datacomputer.compute_all_future_past(all_words_data)
            overall_data['all'] = all_total_avg
            overall_data['future'] = future_total_avg
            overall_data['past'] = past_total_avg
            p_data[p_id] = {'words': word_list,
                            'word_data': all_words_data,
                            'nas': p_nas,
                            'overall': overall_data}
            # print 'p_data'
            # print p_data[p_id]
            # print
    print "Processed {} participants' data".format(len(p_data))
    return p_data


def read_stream(stream, prefix=None):
    """Read raw data from RAs' manual analyses using the Boulder site.
    The file starts with a header at the very top.
    Then, for each participant, there's another header line,
    followed by the data.
    After the participant header, the cells of the first column are empty.

    :rtype: dict
    :param filename: The name of the csv file.
    :return: Dictionary of results, keyed by the participant SN#.
    """
    f = stream.splitlines()
    p_data = {}
    # This first line is the header for the entire file.
    try:
        line = f.pop(0)
    except IndexError:
        print 'datareader.read_stream(): Empty file.'
        # XXX: Haven't decided how to handle all the potential errors.
        raise
    line = line.strip()
    # prev_line = line
    top_header = line.split(',')
    if not top_header:
        # Don't parse this for now.
        pass
    # Now read in per-participant data.
    while True:
        word_list = []
        all_words_data = {}
        # The first line for the participant is a header.
        try:
            line = f.pop(0)
        except IndexError:
            # We had previously read everything, so we're done.
            break
        line = line.strip()
        p_header = line.split(',')

        # The participant's ID # comes first.
        p_id = p_header[0]
        if not p_id:
            # This happens when the previous participant didn't answer.
            """
            print 'previous line:', prev_line
            print 'current line:', line
            print 'p header:', p_header
            print
            """
            continue
        if prefix:
            p_id = prefix + p_id
        # print 'SN #', p_id
        # The number of N/A's this p is at 28.
        try:
            p_nas = int(p_header[28])
        except ValueError:
            # This happens when an RA messes up the file.
            """
            print 'nas: previous line:', prev_line
            print 'nas: current line:', line
            print 'nas: p header:', p_header
            print
            """
            raise
        # print "NA's: #", p_nas
        # Check if this participant left everything blank.
        # XXX: Have to hard-code this.
        if p_nas == 20:
            p_data[p_id] = {'words': None,
                            'word_data': None,
                            'nas': None,
                            'overall': None}
            continue
        # The next line after the header has both the data
        # for the first word and overall statistics.
        # prev_line = line
        try:
            line = f.pop(0)
        except StopIteration:
            # We had previously read everything, so we're done.
            break
        line = line.strip()
        word, word_data, overall_data = parse_first_line(line.split(','))
        word_list.append(word)
        all_words_data[word] = word_data
        # Now read data for the rest of the words.
        for line in f:
            line = line.strip()
            word, word_data = parse_data_lines(line.split(','))
            if word == '':
                """
                print "loop's previous line:", prev_line
                print "loop's current line:", line
                print
                """
                # prev_line = line
                break
            word_list.append(word)
            all_words_data[word] = word_data
            # prev_line = line
        # Compute per-word averages
        all_total_avg, future_total_avg, past_total_avg = \
            datacomputer.compute_all_future_past(all_words_data)
        overall_data['all'] = all_total_avg
        overall_data['future'] = future_total_avg
        overall_data['past'] = past_total_avg
        p_data[p_id] = {'words': word_list,
                        'word_data': all_words_data,
                        'nas': p_nas,
                        'overall': overall_data}
        # print 'p_data'
        # print p_data[p_id]
        # print
    print "Processed {} participants' data".format(len(p_data))
    return p_data


def read_file(f, prefix=None):
    """Read raw data from RAs' manual analyses using the Boulder site.
    The file starts with a header at the very top.
    Then, for each participant, there's another header line,
    followed by the data.
    After the participant header, the cells of the first column are empty.

    :rtype: dict
    :param filename: The name of the csv file.
    :return: Dictionary of results, keyed by the participant SN#.
    """
    p_data = {}
    # This first line is the header for the entire file.
    line = f.next()
    line = line.strip()
    # prev_line = line
    top_header = line.split(',')
    if not top_header:
        # Don't parse this for now.
        pass
    # Now read in per-participant data.
    while True:
        word_list = []
        all_words_data = {}
        # The first line for the participant is a header.
        try:
            line = f.next()
        except StopIteration:
            # We had previously read everything, so we're done.
            break
        line = line.strip()
        p_header = line.split(',')

        # The participant's ID # comes first.
        p_id = p_header[0]
        if not p_id:
            # This happens when the previous participant didn't answer.
            """
            print 'previous line:', prev_line
            print 'current line:', line
            print 'p header:', p_header
            print
            """
            continue
        if prefix:
            p_id = prefix + p_id
        # print 'SN #', p_id
        # The number of N/A's this p is at 28.
        try:
            p_nas = int(p_header[28])
        except ValueError:
            # This happens when an RA messes up the file.
            """
            print 'nas: previous line:', prev_line
            print 'nas: current line:', line
            print 'nas: p header:', p_header
            print
            """
            raise
        # print "NA's: #", p_nas
        # Check if this participant left everything blank.
        # XXX: Have to hard-code this.
        if p_nas == 20:
            p_data[p_id] = {'words': None,
                            'word_data': None,
                            'nas': None,
                            'overall': None}
            continue
        # The next line after the header has both the data
        # for the first word and overall statistics.
        # prev_line = line
        try:
            line = f.next()
        except StopIteration:
            # We had previously read everything, so we're done.
            break
        line = line.strip()
        word, word_data, overall_data = parse_first_line(line.split(','))
        word_list.append(word)
        all_words_data[word] = word_data
        # Now read data for the rest of the words.
        for line in f:
            line = line.strip()
            word, word_data = parse_data_lines(line.split(','))
            if word == '':
                """
                print "loop's previous line:", prev_line
                print "loop's current line:", line
                print
                """
                # prev_line = line
                break
            word_list.append(word)
            all_words_data[word] = word_data
            # prev_line = line
        # Compute per-word averages
        all_total_avg, future_total_avg, past_total_avg = \
            datacomputer.compute_all_future_past(all_words_data)
        overall_data['all'] = all_total_avg
        overall_data['future'] = future_total_avg
        overall_data['past'] = past_total_avg
        p_data[p_id] = {'words': word_list,
                        'word_data': all_words_data,
                        'nas': p_nas,
                        'overall': overall_data}
        # print 'p_data'
        # print p_data[p_id]
        # print
    print "Processed {} participants' data".format(len(p_data))
    return p_data


def parse_first_line(line_list):
    # Most of this line is the same as the other lines.
    word, word_data = parse_data_lines(line_list)
    overall_data = {}
    try:
        overall_data['n_1'] = float(line_list[25])
    except ValueError:
        # Substitute None for unknown correlations.
        overall_data['n_1'] = None
    try:
        overall_data['n_2'] = float(line_list[26])
    except ValueError:
        # Substitute None for unknown correlations.
        overall_data['n_2'] = None
    try:
        overall_data['n_3'] = float(line_list[27])
    except ValueError:
        # Substitute None for unknown correlations.
        overall_data['n_3'] = None
    # print "N's", overall_data
    return word, word_data, overall_data


def parse_data_lines(line_list):
    word = line_list[1].lower()
    word = recode_word(word)
    # print 'word:', word
    word_data = {'corrs': []}
    for corr in line_list[2:22]:
        try:
            word_data['corrs'].append(float(corr))
        except ValueError:
            word_data['corrs'].append(None)
    # print 'word_data:', word_data['corrs']
    # print line_list
    try:
        word_data['all'] = float(line_list[22])
    except ValueError:
        # Substitute None for unknown correlations.
        word_data['all'] = None
    try:
        word_data['future'] = float(line_list[23])
    except ValueError:
        # Substitute None for unknown correlations.
        word_data['future'] = None
    try:
        word_data['past'] = float(line_list[24])
    except ValueError:
        # Substitute None for unknown correlations.
        word_data['past'] = None
    """
    print 'All, Future, Past:', \
        word_data['all'], \
        word_data['future'], \
        word_data['past']
    """
    return word, word_data


def recode_word(word):
    try:
        new_word = word.decode('utf8').encode('ascii', 'ignore')
    except UnicodeDecodeError:
        try:
            new_word = word.decode('latin1').encode('ascii', 'ignore')
        except UnicodeDecodeError:
            print "recode_word() doesn't know the encoding"
            raise
    return new_word


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

    logging.basicConfig(filename="log_dataprocessor.txt",
                        level=log_level,
                        filemode="w")
    logging.info('dataprocessor start: ' + time.strftime("%c"))
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
