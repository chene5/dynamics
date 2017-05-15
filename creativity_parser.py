# -*- coding: utf-8 -*-
"""creativity_parser.py

Created on Sun Feb 14 10:30:23 2016

@author: Eric Chen
"""


if __name__ == '__main__':
    # Parse any command line arguments.
    words_list = []
    p_ids = []
    with open('data.txt', 'r') as in_f:
        in_f.next()
        for line in in_f:
            line = line.strip()
            line_info = line.split('\t')
            word_str = line_info[1]
            word_str = word_str.replace('"', '')
            word_str = word_str.replace('[', '')
            word_str = word_str.replace(']', '')
            words = word_str.split(',')
            words_list.append(words)
            p_ids.append(line_info[0])

    with open('words.csv', 'w') as out_f:
        out_f.write('p_id')
        out_f.write(',')
        out_f.write('seed_word')
        for i in range(1, 21):
            out_f.write(',')
            out_f.write('word_{}'.format(i))
        out_f.write('\n')
        for p_id, words in zip(p_ids, words_list):
            out_f.write(p_id)
            for word in words:
                out_f.write(',')
                out_f.write(word)
            out_f.write('\n')
