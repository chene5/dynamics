# -*- coding: utf-8 -*-
"""utilslib.py
Utility functions.

Created on Sat Nov 28 09:57:00 2015

@author: Eric
"""
from datetime import datetime
from random import randint
from flask import make_response
from application import db
from models import User

CONDITION_FEEDBACK = 2
CONDITION_NO_FEEDBACK = 1
CONDITION_CONTROL = 0


def calc_flow_condition():
    condition = randint(CONDITION_CONTROL, CONDITION_FEEDBACK)
    return condition


def set_flow_condition(user_id, condition=None):
    user = User.query.filter_by(id=user_id).first()
    # print "condition:", user.condition
    if condition:
        user.condition = condition
    else:
        user.condition = calc_flow_condition()
    db.session.add(user)
    db.session.commit()
    return int(user.condition)


def get_flow_condition(user_id):
    user = User.query.filter_by(id=user_id).first()
    # print "condition:", user.condition
    return int(user.condition)


def get_set_flow_condition(user_id, condition=None):
    user = User.query.filter_by(id=user_id).first()
    # print "old condition: {}, for user {}".format(user.condition, user_id)
    if not user.condition:
        set_flow_condition(user_id, condition=condition)
        # print "new condition: {}, for user {}".format(user.condition,
        # user_id)
    return int(user.condition)


def make_anon_id():
    return 'anon_' + datetime.now().strftime("%Y-%m-%d_%H%M%S%f")


def make_partic_id(prefix=None):
    if prefix:
        partic_id = prefix + '_' + datetime.now().strftime("%Y-%m-%d_%H%M%S%f")
    else:
        partic_id = 'partic_q_' + datetime.now().strftime("%Y-%m-%d_%H%M%S%f")
    return partic_id


def list_to_csv_str(input_list):
    # print 'input_list:', input_list
    csv_str = ''
    for row in input_list:
        for item in row[:-1]:
            if not item:
                csv_str += '.,'
            if item == '\n':
                continue
            csv_str += str(item) + ','
        # Now append the last item of the line.
        if row[-1]:
            csv_str += (row[-1])
        else:
            csv_str += '.'
        csv_str += '\n'
    return csv_str


def make_csv(input_list):
    csv_str = list_to_csv_str(input_list)
    # print 'csv_str:', csv_str

    response = make_response(csv_str)

    curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = 'results_' + curr_time + '.csv'
    # print 'filename:', filename

    response.headers["Content-Disposition"] = "attachment; filename=" + \
        filename
    response.mimetype = 'text/csv'

    return response


def format_for_tsv(str_item):
    return str_item.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')


def list_to_tsv_str(input_list):
    # print 'input_list:', input_list
    tsv_str = ''
    for row in input_list:
        for item in row[:-1]:
            if not item:
                tsv_str += '.\t'
                continue
            if item == '\n':
                continue
            try:
                tsv_str += format_for_tsv(str(item)) + '\t'
            except UnicodeEncodeError:
                item = item.encode('ascii', 'ignore')
                tsv_str += format_for_tsv(str(item)) + '\t'
            except:
                raise
        # Now append the last item of the line.
        if row[-1]:
            try:
                tsv_str += format_for_tsv(str(row[-1]))
            except UnicodeEncodeError:
                item = item.encode('ascii', 'ignore')
                tsv_str += format_for_tsv(str(row[-1]))
            except:
                raise
        else:
            tsv_str += '.'
        tsv_str += '\n'
    return tsv_str


def make_tsv(input_list):
    tsv_str = list_to_tsv_str(input_list)
    # print 'tsv_str:', tsv_str

    response = make_response(tsv_str)

    curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = 'results_' + curr_time + '.txt'
    # print 'filename:', filename

    response.headers["Content-Disposition"] = "attachment; filename=" + \
        filename
    response.mimetype = 'text/tab-separated-values'

    return response


def list_to_str(input_list, separator=','):
    # print 'input_list:', input_list
    out_str = ''
    for row in input_list:
        for item in row[:-1]:
            if not item:
                out_str += '.' + separator
                continue
            if item == '\n':
                continue
            out_str += str(item) + separator
        # Now append the last item of the line.
        if row[-1]:
            out_str += str(row[-1])
        else:
            out_str += '.'
        out_str += '\n'
    return out_str
