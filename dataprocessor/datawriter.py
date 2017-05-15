# -*- coding: utf-8 -*-
"""datawriter.py - Writes data.

Created on Wed Nov 11 08:32:23 2015

XXX TODO:
Write *avg variables.

@author: Eric Chen
"""
import os
import sys
import getopt
import logging
import time

# Custom modules
# from application.creativityconstruct import CreativityConstruct
# import datareader

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


def main(argv):
    parse_args(argv)


def write_all_data(all_p_data, all_c_data):
    counter = 0
    filename = 'all_output_' + str(counter) + '.csv'
    while os.path.isfile(filename):
        counter += 1
        filename = 'all_output_' + str(counter) + '.csv'
        if counter >= 20:
            # Time to give up.
            print 'Overwriting file', filename
            break
    output_data = None
    print 'Writing output to', filename
    with open(filename, 'w') as f:
        output_data = gen_output_data(all_p_data, all_c_data)
        for curr_line in output_data:
            f.write(curr_line)
    return output_data


def gen_data_header():
    # Generate header
    header = 'p_id,'
    for i in range(1, 21):
        header += 'creativity_all_' + str(i) + ','
        header += 'creativity_future_' + str(i) + ','
        header += 'creativity_past_' + str(i) + ','
    # Per-word averages
    header += 'creativity_all_avg,'
    header += 'creativity_future_avg,'
    header += 'creativity_past_avg,'
    # Per-participant averages
    header += 'creativity_n_1,'
    header += 'creativity_n_2,'
    header += 'creativity_n_3,'
    for i in range(1, 21):
        header += 'boulder_all_' + str(i) + ','
        header += 'boulder_future_' + str(i) + ','
        header += 'boulder_past_' + str(i) + ','
    # Per-word averages
    header += 'boulder_all_avg,'
    header += 'boulder_future_avg,'
    header += 'boulder_past_avg,'
    # Per-participant averages
    header += 'boulder_n_1,'
    header += 'boulder_n_2,'
    # No comma at the end!!!
    header += 'boulder_n_3'
    header += '\n'

    return header


def gen_model_str(model_data, sorted_p_ids, write_p_id):
    model_str_dict = {}
    for p_id in sorted_p_ids:
        c_data = model_data[p_id]
        """
        print 'c_data'
        print c_data
        print
        """
        try:
            c_corr_data = c_data['word_data']
        except KeyError:
            # This participant doesn't have any word data.
            continue
        # print "p words:", p_data['words']
        # print "c words:", c_data['words']
        if write_p_id:
            curr_line = p_id + ','
        else:
            curr_line = ''
        # f.write(p_id + ',')
        for word in c_data['words']:
            c_word_data = c_corr_data[word]
            try:
                curr_line += str(round(c_word_data['all'], 3)) + ','
            except TypeError:
                curr_line += '.,'
            try:
                curr_line += str(round(c_word_data['future'], 3)) + ','
            except TypeError:
                curr_line += '.,'
            try:
                curr_line += str(round(c_word_data['past'], 3)) + ','
                """
                print p_id
                print word
                print "str(round(c_word_data['past'], 3))"
                print str(round(c_word_data['past'], 3))
                """
            except TypeError:
                curr_line += '.,'
        curr_line += str(round(c_data['overall']['all'], 3)) + ','
        curr_line += str(round(c_data['overall']['future'], 3)) + ','
        curr_line += str(round(c_data['overall']['past'], 3)) + ','
        curr_line += str(round(c_data['overall']['n_1'], 3)) + ','
        curr_line += str(round(c_data['overall']['n_2'], 3)) + ','
        # No comma at the end!!!
        curr_line += str(round(c_data['overall']['n_3'], 3))

        model_str_dict[p_id] = curr_line
    return model_str_dict


def gen_output_data(all_p_data, all_c_data):
    output_data = []

    header = gen_data_header()
    output_data.append(header)

    # Generate participant data cells.
    sorted_p_ids = sorted(all_c_data)
    # print sorted_p_ids
    c_strs = gen_model_str(all_c_data, sorted_p_ids, write_p_id=True)
    p_strs = gen_model_str(all_p_data, sorted_p_ids, write_p_id=False)
    for p_id in sorted_p_ids:
        curr_line = c_strs[p_id]
        curr_line += ','
        curr_line += p_strs[p_id]
        curr_line += '\n'
        output_data.append(curr_line)

    return output_data


def gen_output_data_old(all_p_data, all_c_data):
    output_data = []

    # Generate header
    header = 'p_id,'
    for i in range(1, 21):
        header += 'boulder_all_' + str(i) + ','
        header += 'boulder_future_' + str(i) + ','
        header += 'boulder_past_' + str(i) + ','
    # Per-word averages
    header += 'boulder_all_avg,'
    header += 'boulder_future_avg,'
    header += 'boulder_past_avg,'
    # Per-participant averages
    header += 'boulder_n_1,'
    header += 'boulder_n_2,'
    header += 'boulder_n_3,'
    for i in range(1, 21):
        header += 'creativity_all_' + str(i) + ','
        header += 'creativity_future_' + str(i) + ','
        header += 'creativity_past_' + str(i) + ','
    # Per-word averages
    header += 'creativity_all_avg,'
    header += 'creativity_future_avg,'
    header += 'creativity_past_avg,'
    # Per-participant averages
    header += 'creativity_n_1,'
    header += 'creativity_n_2,'
    header += 'creativity_n_3,'
    header += '\n'
    output_data.append(header)

    # Generate participant data cells.
    sorted_p_ids = sorted(all_c_data)
    for p_id in sorted_p_ids:
        c_data = all_c_data[p_id]
        p_data = all_p_data[p_id]
        """
        print 'p_data'
        print p_data
        print
        print 'c_data'
        print c_data
        print
        """
        try:
            p_corr_data = p_data['word_data']
            c_corr_data = c_data['word_data']
        except KeyError:
            # This participant doesn't have any word data.
            continue
        # print "p words:", p_data['words']
        # print "c words:", c_data['words']
        curr_line = p_id + ','
        # f.write(p_id + ',')
        for word in p_data['words']:
            p_word_data = p_corr_data[word]
            try:
                curr_line += str(round(p_word_data['all'], 3)) + ','
            except TypeError:
                curr_line += '.,'
            try:
                curr_line += str(round(p_word_data['future'], 3)) + ','
            except TypeError:
                curr_line += '.,'
            try:
                curr_line += str(round(p_word_data['past'], 3)) + ','
            except TypeError:
                curr_line += '.,'
        curr_line += str(round(p_data['overall']['all'], 3)) + ','
        curr_line += str(round(p_data['overall']['future'], 3)) + ','
        curr_line += str(round(p_data['overall']['past'], 3)) + ','
        curr_line += str(round(p_data['overall']['n_1'], 3)) + ','
        curr_line += str(round(p_data['overall']['n_2'], 3)) + ','
        curr_line += str(round(p_data['overall']['n_3'], 3)) + ','

        for word in p_data['words']:
            c_word_data = c_corr_data[word]
            try:
                curr_line += str(round(c_word_data['all'], 3)) + ','
            except TypeError:
                curr_line += '.,'
            try:
                curr_line += str(round(c_word_data['future'], 3)) + ','
            except TypeError:
                curr_line += '.,'
            try:
                curr_line += str(round(c_word_data['past'], 3)) + ','
                """
                print p_id
                print word
                print "str(round(c_word_data['past'], 3))"
                print str(round(c_word_data['past'], 3))
                """
            except TypeError:
                curr_line += '.,'
        curr_line += str(round(c_data['overall']['all'], 3)) + ','
        curr_line += str(round(c_data['overall']['future'], 3)) + ','
        curr_line += str(round(c_data['overall']['past'], 3)) + ','
        curr_line += str(round(c_data['overall']['n_1'], 3)) + ','
        curr_line += str(round(c_data['overall']['n_2'], 3)) + ','
        curr_line += str(round(c_data['overall']['n_3'], 3)) + ','
        curr_line += '\n'
        output_data.append(curr_line)

    return output_data


def output_csv(word_list, result):
    with open('test.csv', 'w') as csvf:
        full_word_list = ','
        for word in word_list:
            full_word_list += word + ','
        csvf.write(full_word_list)
        csvf.write('\n')
        index = 0
        # print result
        # print type(result)
        for row in result:
            fullrow = word_list[index] + ','
            index += 1
            for word in row:
                # print row
                # print type(row)
                if word:
                    fullrow += str(round(word, 3)) + ','
                else:
                    fullrow += '.' + ','
            csvf.write(fullrow)
            csvf.write('\n')


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
