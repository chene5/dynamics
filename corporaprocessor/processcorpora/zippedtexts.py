# -*- coding: utf-8 -*-
"""zippedtexts.py
Defines the class that can process zipped text files.

TODO

Created on Fri Sept 11 13:18:00 2015

@author: Eric
"""
__author__ = 'eec'

import os

from gensim.corpora.textcorpus import TextCorpus
import zipfile


class ZippedTexts(TextCorpus):
    """
    This class is for corpora files that are zipped.
    This class inherits from gensim's TextCorpus helper class.
    This supplies an iterator that iterates through the files in the zip file.

    """
    def __init__(self,
                 fname,
                 fext=None,
                 lemmatize=False,
                 dictionary=None,
                 filter_namespaces=('0',)):
        """
        Initialize the corpus. Unless a dictionary is provided, this scans the
        corpus once, to determine its vocabulary.

        If `pattern` package is installed, use fancier shallow parsing to get
        token lemmas. Otherwise, use simple regexp tokenization. You can
        override this automatic logic by forcing the `lemmatize` parameter
        explicitly.

        """
        self.fname = fname
        self.fext = fext
        self.filter_namespaces = filter_namespaces
        self.metadata = False
        self.lemmatize = lemmatize
        self.dictionary = dictionary

    def extract_file(self, filename, path=None):
        with zipfile.ZipFile(self.fname, "r") as zipped_file:
            if path:
                zipped_file.extract(filename, path)
            else:
                zipped_file.extract(filename)

    def extract_all_files(self, path):
        """
        Iterate over the collection, extracting all appropriate files.

        There may be further preprocessing of the words coming out of this
        function.

        """
        with zipfile.ZipFile(self.fname, "r") as zipped_file:
            for filename in zipped_file.namelist():
                # print "opening {}".format(filename)
                if self.fext:
                    _, ext = os.path.splitext(filename)
                    # print "ext: {}".format(ext)
                    if self.fext != ext:
                        # print "continuing"
                        continue
                    # print 'Opening:', filename
                if path:
                    zipped_file.extract(filename, path)
                else:
                    zipped_file.extract(filename)

    def get_text_names(self):
        """
        Iterate over the collection, yielding one document name at a time. A
        document is a sequence of words (strings) that can be fed into
        `Dictionary.doc2bow`.

        Each document is a separate file.

        There may be further preprocessing of the words coming out of this
        function.

        """
        with zipfile.ZipFile(self.fname, "r") as zipped_file:
            for filename in zipped_file.namelist():
                # print "opening {}".format(filename)
                if self.fext:
                    _, ext = os.path.splitext(filename)
                    # print "ext: {}".format(ext)
                    if self.fext != ext:
                        # print "continuing"
                        continue
                    # print 'Opening:', filename
                yield filename

    def get_texts(self):
        """
        Iterate over the collection, yielding one document at a time. A
        document is a sequence of words (strings) that can be fed into
        `Dictionary.doc2bow`.

        Each document is a separate file.

        There may be further preprocessing of the words coming out of this
        function.

        """
        with zipfile.ZipFile(self.fname, "r") as zipped_file:
            for filename in zipped_file.namelist():
                # print "opening {}".format(filename)
                if self.fext:
                    _, ext = os.path.splitext(filename)
                    # print "ext: {}".format(ext)
                    if self.fext != ext:
                        # print "continuing"
                        continue
                with zipped_file.open(filename, 'rU') as text:
                    yield text.read()

    def get_all_texts(self):
        """
        Read through the whole file and put them together in a list.

        """
        print "Get texts from {}".format(self.fname)
        # print "extension: {}".format(self.fext)
        doc_list = []
        for doc in self.get_texts():
            doc_list.append(doc)
        return doc_list
# endclass ZippedTexts
