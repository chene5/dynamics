# -*- coding: utf-8 -*-
"""mlstripper.py
Class to strip markup language (e.g., html) from strings.


Created on Wed Sep 23 15:48:55 2015

@author: Eric Chen
"""
from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    """
        Markup Language Stripper.
        This class strips out html tags (e.g., <p>, <b>) from strings.
        Works in conjunction with the strip_tags() function, below.
        Based on:
            http://stackoverflow.com/questions/753052/
            strip-html-from-strings-in-python
    """
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ' '.join(self.fed)


def strip_tags(html):
    """Strip html tags, using the MLStripper class."""
    s = MLStripper()
    s.feed(html)
    return s.get_data()
