# -*- coding: utf-8 -*-
"""dataprocessor.py - Processes data.

Created on Tue Nov 10 07:45:23 2015

Todo:
Fix future avg for final word.


@author: Eric Chen
"""
import sys
import getopt
import logging
import time
from array import array

from numpy import corrcoef

# Custom modules
from application.creativityconstruct import CreativityConstruct
import datareader
import datacomputer
import datawriter

__author__ = 'Eric Chen'

"""Defaults for Windows"""
_default_dict_path = 'c:/bin/constructs/'
_corpus_root = 'c:/bin/corpora/'
DEFAULT_CONSTRUCT = 'model_10-27-15_1648'
DEFAULT_PATH = 'c:/bin/constructs/{}/'.format(DEFAULT_CONSTRUCT)

"""Defaults for Mac
_default_dict_path = '/Users/eric/Documents/constructs/'
_corpus_root = '/Users/eric/Documents/'
"""

DRAMA_DATA = 'drama.csv'
FIELD_DATA = 'field.csv'


def main(argv):
    parse_args(argv)
    # boulder_vs_construct()
    """
    interactive_processing()
    """
    creativity_construct = CreativityConstruct(DEFAULT_CONSTRUCT,
                                               DEFAULT_PATH)
    boulder_vs_construct(creativity_construct)


def analyze_stream(creativity_construct, p_datastream, prefix='drama_'):
    """
    print "Analyze stream: Battling models... {}, {}".format(p_datastream,
                                                             prefix)
    """
    all_p_data = datareader.read_stream(p_datastream, prefix)
    all_c_data = compare_models(creativity_construct, all_p_data)
    output_data = datawriter.gen_output_data(all_p_data, all_c_data)
    # print "Done battling!"
    return output_data


def model_battle(creativity_construct,
                 p_data_file=DRAMA_DATA,
                 prefix='drama_'):
    print "Battling models... {}, {}".format(p_data_file, prefix)
    all_p_data, all_c_data = boulder_vs_construct(creativity_construct,
                                                  p_data_file=p_data_file,
                                                  prefix=prefix)
    output_data = datawriter.gen_output_data(all_p_data, all_c_data)
    print "Done battling!"
    return output_data


def compute_corrs(all_p_data, all_c_data):
    p_all_avgs = array('f')
    c_all_avgs = array('f')
    p_future_avgs = array('f')
    c_future_avgs = array('f')
    p_past_avgs = array('f')
    c_past_avgs = array('f')
    p_n_1_avgs = array('f')
    c_n_1_avgs = array('f')
    p_n_2_avgs = array('f')
    c_n_2_avgs = array('f')
    p_n_3_avgs = array('f')
    c_n_3_avgs = array('f')
    for p_id, p_data in all_p_data.iteritems():
        p_all_avgs.append(p_data['overall']['all'])
        p_future_avgs.append(p_data['overall']['future'])
        p_past_avgs.append(p_data['overall']['past'])
        p_n_1_avgs.append(p_data['overall']['n_1'])
        p_n_2_avgs.append(p_data['overall']['n_2'])
        p_n_3_avgs.append(p_data['overall']['n_3'])

        c_data = all_c_data[p_id]
        c_all_avgs.append(c_data['overall']['all'])
        c_future_avgs.append(c_data['overall']['future'])
        c_past_avgs.append(c_data['overall']['past'])
        c_n_1_avgs.append(c_data['overall']['n_1'])
        c_n_2_avgs.append(c_data['overall']['n_2'])
        c_n_3_avgs.append(c_data['overall']['n_3'])

    try:
        print 'all_avgs:', corrcoef(p_all_avgs, c_all_avgs)
    except:
        print "correlation calculation failed"
    print

    try:
        print 'future_avgs:', corrcoef(p_future_avgs, c_future_avgs)
    except:
        print "correlation calculation failed"
    print

    try:
        print 'past_avgs:', corrcoef(p_past_avgs, c_past_avgs)
    except:
        print "correlation calculation failed"
    print

    try:
        print 'n_1_avgs:', corrcoef(p_n_1_avgs, c_n_1_avgs)
    except:
        print "correlation calculation failed"
    print

    try:
        print 'n_2_avgs:', corrcoef(p_n_2_avgs, c_n_2_avgs)
    except:
        print "correlation calculation failed"
    print

    try:
        print 'n_3_avgs:', corrcoef(p_n_3_avgs, c_n_3_avgs)
    except:
        print "correlation calculation failed"
    print


def boulder_vs_construct_write(creativity_construct):
    all_p_data, creativity_data = boulder_vs_construct(creativity_construct)
    print "Writing data..."
    output_data = datawriter.write_all_data(all_p_data, creativity_data)
    print "Done writing!"
    return output_data


def boulder_vs_construct(creativity_construct,
                         p_data_file=DRAMA_DATA,
                         prefix='drama_'):
    all_p_data = datareader.read_data(p_data_file, prefix)
    creativity_data = compare_models(creativity_construct, all_p_data)
    return all_p_data, creativity_data


def compare_models(creativity_construct, all_p_data):
    all_word_lists = []
    print "Passing words to creativity construct..."
    creativity_data = {}
    for p_id, p_data in all_p_data.iteritems():
        words = p_data['words']
        creativity_data[p_id] = {'words': words}
        all_word_lists.append(words)
        """
        print "Query for {}:".format(p_id)
        print "Word list:"
        print words
        print
        """
        if words:
            result = creativity_construct.query_list(words)
            # result = query_list(creativity_construct, words)
            corr_data, overall_data = compute_all(result, words)
        else:
            """
            corr_data = None
            overall_data = None
            """
            continue
        creativity_data[p_id]['word_data'] = corr_data
        creativity_data[p_id]['overall'] = overall_data
        # print '  Did ', p_id,
    # print
    # print creativity_data
    return creativity_data


def get_p_data():
    # all_data = datareader.read_field_data()
    all_data = datareader.read_drama_data()
    # field_data = datareader.read_field_data()
    # all_data.update(field_data)
    return all_data


def get_total(in_list):
    total = 0.0
    count = 0
    for thing in in_list:
        if thing:
            total += thing
            count += 1
        else:
            continue
    if count == 0:
        return None
    else:
        return total


def get_abs_total(in_list):
    total = 0.0
    count = 0
    for thing in in_list:
        if thing:
            total += abs(thing)
            count += 1
        else:
            continue
    if count == 0:
        return None
    else:
        return total


def compute_all(result, word_list):
    corr_data = {}
    word_count = len(word_list)
    # print 'word count:', word_count
    word_idx = 0

    weighted_total = 0.0
    weighted_count = 0
    weighted_avg = 0.0

    n_1_total = 0.0
    n_1_count = word_count - 1
    n_2_total = 0.0
    n_2_count = word_count - 2
    n_3_total = 0.0
    n_3_count = word_count - 3

    # Number of unknown words
    n_a = 0

    for row in result:
        if word_count == 0:
            # print 'No Words here.'
            break
        count = 0
        total = 0.0
        # Start the row index counter for the similarities at -1
        # because we increment immediately, at the start of each loop.
        sim_idx = -1
        for sim in row:
            sim_idx += 1
            if sim:
                total += sim
            else:
                # In the future we may want to handle this specially.
                pass
            if sim_idx == word_idx:
                if sim is None:
                    # There wasn't a word here, so mark it as N/A
                    n_a += 1
                # The similarity of the word with itself. Don't count it.
                continue
            else:
                count += 1
        try:
            # all_avg = get_total(row[:word_idx] + row[(word_idx + 1):]) / \
            #    count
            all_row = row[:word_idx] + row[word_idx + 1:]
            all_avg = get_total(all_row) / len(all_row)
            """
            print "all row len {} for word {}: {}".format(
                len(all_row), word_idx, all_row)
            print "all_avg:", all_avg, "tot", get_total(all_row)
            """
        except ZeroDivisionError:
            all_avg = None
        except TypeError:
            all_avg = None
        except:
            raise

        # Calculate the average of the future.
        try:
            future_row = row[word_idx + 1:]
            # print "future_row for word_idx", word_idx, future_row
        except IndexError:
            future_row = None
        if future_row:
            try:
                future_avg = get_total(future_row) / len(future_row)
                weighted_total += get_abs_total(future_row)
                # future_avg = get_total(future_row) / (count - 1 - word_idx)
                # print "future row for word {}: {}".format(word_idx, future_row)
                # print "future_avg", future_avg
            except TypeError:
                future_avg = None
                # Don't increment weighted_total
            except:
                raise
            weighted_count += len(future_row)
        else:
            future_avg = None

        # Calculate the average of the past.
        past_row = row[:word_idx]
        # print "past_row for word_idx {}: {}".format(word_idx, past_row)
        if past_row:
            try:
                past_avg = get_total(past_row) / len(past_row)
                # past_avg = get_total(past_row) / word_idx
                """
                print "past row len {} for word {}: {}".format(
                    len(past_row), word_idx, past_row)
                print "past_avg:", past_avg, "tot", get_total(past_row)
                """
            except TypeError:
                past_avg = None
            except:
                raise
        else:
            past_avg = None

        # print
        # print "Word {}'s past average: {}".format(word_idx, past_avg)
        # print past_row
        corr_data[word_list[word_idx]] = {'all': all_avg,
                                          'future': future_avg,
                                          'past': past_avg}
        try:
            n_1_total += row[word_idx + 1]
        except IndexError:
            # Trying to look too far into the future.
            pass
        except TypeError:
            # Looked into a blank spot.
            pass
        try:
            n_2_total += row[word_idx + 2]
        except IndexError:
            # Trying to look too far into the future.
            pass
        except TypeError:
            # Looked into a blank spot.
            pass
        try:
            n_3_total += row[word_idx + 3]
        except IndexError:
            # Trying to look too far into the future.
            pass
        except TypeError:
            # Looked into a blank spot.
            pass
        word_idx += 1
        # End per-word loop
    if n_1_count < 1:
        n_1_avg = 0.0
    else:
        n_1_avg = n_1_total / n_1_count
    if n_2_count < 1:
        n_2_avg = 0.0
    else:
        n_2_avg = n_2_total / n_2_count
    if n_3_count < 1:
        n_3_avg = 0.0
    else:
        n_3_avg = n_3_total / n_3_count
    all_total_avg, future_total_avg, past_total_avg = \
        datacomputer.compute_all_future_past(corr_data)

    try:
        weighted_avg = weighted_total / weighted_count
    except ZeroDivisionError:
        weighted_avg = None

    overall_data = {'all': all_total_avg,
                    'future': future_total_avg,
                    'past': past_total_avg,
                    'weighted': weighted_avg,
                    'n_1': n_1_avg,
                    'n_2': n_2_avg,
                    'n_3': n_3_avg,
                    'n_a': n_a}
    # print corr_data
    return corr_data, overall_data


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
    """
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-2s: %(levelname)-2s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    """


# LET'S GO!!!
if __name__ == "__main__":
    main(sys.argv[1:])
