# -*- coding: utf-8 -*-
"""datacomputer.py - Computes data.

Created on Thu Nov 19 19:38:23 2015


@author: Eric Chen
"""


def compute_all_future_past(corr_data):
    all_total = 0.0
    all_count = 0
    future_total = 0.0
    future_count = 0
    past_total = 0.0
    past_count = 0
    # word_count = len(corr_data)
    for word_data in corr_data.itervalues():
        if word_data['all']:
            all_total += word_data['all']
            all_count += 1
        if word_data['future']:
            future_total += word_data['future']
            future_count += 1
        if word_data['past']:
            past_total += word_data['past']
            past_count += 1

    try:
        all_total_avg = all_total / all_count
    except ZeroDivisionError:
        all_total_avg = 0
    try:
        future_total_avg = future_total / future_count
    except ZeroDivisionError:
        future_total_avg = 0
    try:
        past_total_avg = past_total / past_count
    except ZeroDivisionError:
        past_total_avg = 0

    return all_total_avg, future_total_avg, past_total_avg
