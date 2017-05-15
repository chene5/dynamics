# -*- coding: utf-8 -*-
"""processtweets.py
Process tweets stored in .json files.

@author: eec
"""
from datetime import datetime
import getopt
import json
import os
# import string
import sys

from flask import make_response

import thoughtslib
from eec_utils import list_type_in_dir

_in_filename = None


def process_one_file(in_filename):
    # print in_filename
    text_list = []
    tweeter_data = {'tweeter': '',
                    'tweet_count': 0,
                    'lsa_avg': 0.0,
                    'comparison_count': 0,
                    'NAs': 0}
    # Get the thought construct.
    thought_construct = thoughtslib.get_user_construct()

    # Get the name of the tweeter.
    tweeter = os.path.splitext(in_filename)[0].lower()
    tweeter = tweeter.lstrip('./')
    tweeter = tweeter.rstrip('_0')
    # print tweeter
    tweeter_data['tweeter'] = tweeter

    # Set up tweets string
    tweets = tweeter + ','

    # Tweets
    prev_tweet = None
    this_tweet = None
    lsa_total = 0.0
    comparison_count = 0
    na_count = 0
    tweet_count = 0
    sim = 0.0

    # Read tweet file.
    with open(in_filename, 'r') as in_f:
        for line in in_f:
            tweet = json.loads(line)
            if not tweet:
                continue
            tweet_count += 1

            # Convert to utf-8.
            # text = str(tweet['text'].encode('utf-8', 'ignore'))
            text = tweet['text'].encode('ascii', 'replace')
            # Replace ? with a space
            text = text.replace('?', ' ')
            # Clean out some of the punctuation
            # text = text.translate(None, string.punctuation)
            text = text.replace(',', '')
            text = text.replace('.', '')
            text = text.replace(':', '')
            text = text.replace('/', '')
            text = text.replace('@', '')
            text = text.replace('#', '')
            text = text.replace('&amp;', '')
            # print text

            this_tweet = text
            text_list.append(text)
            tweets += text + ','

            # Count the number of comparisons
            comparison_count += 1

            # Try to get the similarity between this tweet and the previous one
            try:
                sim = thought_construct.query_pair_lsi(prev_tweet, this_tweet)
            except AttributeError:
                # This should only happen if prev_tweet is None.
                # That's ok. It just means we just started.
                if prev_tweet:
                    raise
                else:
                    # print "prev_tweet is none"
                    sim = 0.0
                    comparison_count -= 1
            except:
                raise

            # print "sim", sim
            # print "lsa_total", lsa_total
            # Add this similarity to the running total.
            try:
                lsa_total += sim
            except TypeError:
                # This should only happen if sim is None
                # That's ok. It just means the tweet wasn't understood.
                if sim:
                    raise
                # print "Didn't understand this tweet:"
                # print this_tweet
                na_count += 1
                comparison_count -= 1
            except:
                raise

            # Get ready for the next loop
            prev_tweet = this_tweet
    try:
        lsa_avg = lsa_total / comparison_count
    except ZeroDivisionError:
        lsa_avg = '.'
    except:
        raise
    tweeter_data['lsa_avg'] = lsa_avg
    tweeter_data['comparison_count'] = comparison_count
    tweeter_data['na_count'] = na_count
    tweeter_data['tweet_count'] = tweet_count
    return tweeter_data


def process_this_dir():
    file_list = list_type_in_dir('.', '.json')
    tweet_lsa_dict = {}
    for filename in file_list:
        # Get the name of the tweeter.
        tweeter = os.path.splitext(filename)[0].lower()
        print tweeter
        tweeter = tweeter.lstrip('./')
        tweeter = tweeter.rstrip('_0')
        print tweeter
        tweeter_data = process_one_file(filename)
        tweet_lsa_dict[tweeter] = tweeter_data

    file_str = 'Tweeter,Flow,Comparisons,NAs,Tweets\n'
    for tweeter, tweeter_data in sorted(tweet_lsa_dict.iteritems()):
        file_str += tweeter_data['tweeter'] + ','
        file_str += str(tweeter_data['lsa_avg']) + ','
        file_str += str(tweeter_data['comparison_count']) + ','
        file_str += str(tweeter_data['na_count']) + ','
        file_str += str(tweeter_data['tweet_count']) + '\n'

    curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = 'tweets_' + curr_time + '.csv'

    response = make_response(file_str)
    response.headers["Content-Disposition"] = "attachment; filename=" + \
        filename
    response.mimetype = 'text/csv'

    # print output
    return response


def usage():
    print __doc__


def parse_args(argv):
    # Parse the command-line arguments
    global _in_filename

    args_dict = {"in_filename": _in_filename}

    try:
        opts, args = getopt.getopt(argv,
                                   "hf:i:",
                                   ["help",
                                    "file",
                                    "input"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            args_dict["in_filename"] = arg
            print("in_filename:", args_dict["in_filename"])
        elif opt in ("-i", "--iv"):
            args_dict["in_filename"] = arg
            print("in_filename:", args_dict["in_filename"])

    return args_dict


if __name__ == '__main__':
    args_dict = parse_args(sys.argv[1:])

    in_filename = args_dict["in_filename"]

    if in_filename:
        process_one_file(in_filename)
    else:
        process_this_dir()
