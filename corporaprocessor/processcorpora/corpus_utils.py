# -*- coding: utf-8 -*-
"""corpus_utils.py
Utility functions for processing corpora.
Many of these were formerly methods of the CorpusProcessor class.

Created on Wed Sep 23 09:50:35 2015

@author: Eric Chen
"""
import os
import logging
import eec_utils
import smart_open
from gensim import corpora
import zippedtexts


def read_documents(self, corpus_path, extension):
    """
    Read in all the documents in this directory and all its
    subdirectories. Only read files with the given extension. This is
    because corpora often come bundled with various metadata files.

    Warning: This function builds up a massive list, so it can be memory
    intensive.
    """
    doc_list = eec_utils.list_a_file_type(corpus_path, extension)
    documents = []
    doc_count = 0
    print 'Reading documents:'
    for docname in doc_list:
        with smart_open.smart_open(docname, 'r') as doc_file:
            document = eec_utils.read_a_doc(doc_file)
            documents.append(document)
        doc_count += 1
        if doc_count % 100 == 0:
            print '...', doc_count
    return documents


def get_texts_from_doc_2lines(document):
    text_list = []
    text = ''
    got_newline_before = False

    for line in document:
        if line != "\n":
            # This is a line of text, so add it to the text and
            # then keep going.
            text += line
            got_newline_before = False
            continue
        else:
            # This is a newline. Check if we just got one before.
            if not got_newline_before:
                # We didn't see a newline before.
                # Add it, remember seeing the newline, and
                # keep going.
                text += line
                got_newline_before = True
                continue
            else:
                # This is the second newline in a row that we've
                # seen. Add it to the text and then we'll go on to
                # append it to the document list.
                text += line

        # Got to the end of a paragraph. Append it to documents.
        bow = parse_document(text)
        text_list.append(bow)
        text = ''
        got_newline_before = False

    if text != '':
        # Just in case there's anything left, Append the rest of the text.
        bow = parse_document(text)
        text_list.append(bow)

    return text_list


def read_documents_by_paragraph(self, corpus_path, extension):
    """
    Read in all the documents in this directory and all its
    subdirectories. Only read files with the given extension. This is
    because corpora often come bundled with various metadata files.

    This function divides up the text in each file into paragraphs. This
    function approximates that by dividing the text up when two newline
    characters occur one after the other.

    Warning: This function builds up a massive list, so it can be memory
    intensive.
    """
    doc_list = eec_utils.list_a_file_type(corpus_path, extension)
    documents = []
    doc_count = 0
    print 'Reading documents by paragraph:'
    for docname in doc_list:
        with open(docname, 'rU') as doc_file:
            document = eec_utils.read_a_doc(doc_file)

            # Read the file. Now process the text.
            text = ''
            got_newline_before = False
            for line in document:
                if line != "\n":
                    # This is a line of text, so add it to the text and
                    # then keep going.
                    text += line
                    got_newline_before = False
                    continue
                else:
                    # This is a newline. Check if we just got one before.
                    if not got_newline_before:
                        # We didn't see a newline before.
                        # Add it, remember seeing the newline, and
                        # keep going.
                        text += line
                        got_newline_before = True
                        continue
                    else:
                        # This is the second newline in a row that we've
                        # seen. Add it to the text and then we'll go on to
                        # append it to the document list.
                        text += line

                # Got to the end of a paragraph. Append it to documents.
                documents.append(text)
                text = ''
                got_newline_before = False

            # Append the rest of the text.
            documents.append(text)
            text = ''
            got_newline_before = False

        doc_count += 1
        if doc_count % 100 == 0:
            print '...', doc_count

    return documents


def create_corpus(self, file_name, file_extension):
    """XXX: Not sure what this function does. Looks like it
        is supposed to update stuff?
    """
    logging.debug("Getting documents.")
    # Get just the file name for when we save these new files.
    fname, fext = os.path.splitext(file_name)

    if fext == '.zip':
        zipped_documents = zippedtexts.ZippedTexts(file_name,
                                                   file_extension)
        documents = zipped_documents.get_all_texts()
    else:
        documents = self.read_documents_by_paragraph(file_extension)

    logging.debug("Getting texts.")
    texts = self.get_texts_as_bow(documents)

    logging.debug("Creating update dictionary.")
    dictionary = corpora.Dictionary(texts)
    # Now store the dictionary to disk.
    dict_filename = fname + "_dict.dict"
    dictionary.save(dict_filename)

    logging.debug("Creating update corpus.")
    corpus = [dictionary.doc2bow(text) for text in texts]
    # Now store the corpus to disk.
    corpus_filename = fname + "_corpus.mm"
    corpora.MmCorpus.serialize(corpus_filename, corpus)

    return corpus


def get_texts_from_doc(self, document):
    text_list = []
    text = ''

    for line in document:
        if line != "\n":
            # This is a line of text, so add it to the text and
            # then keep going.
            text += line
            continue
        else:
            # Found a newline character, which means we got to the end
            # of a paragraph. Append the text we have to the list.
            if text != '':
                bow = self.parse_document(text)
                text_list.append(bow)
                text = ''

    # If there's anything left, Append the rest.
    if text != '':
        bow = self.parse_document(text)
        text_list.append(bow)

    return text_list


def process_documents(self, corpus_path, corpus_file_extension):
    """
    Wrapper function for the read_document_xxx functions. Checks for
    exceptions.

    :param corpus_path: The path to the corpus files directory.

    :param corpus_extension: The file extension for the corpus's files.

    :return: List of documents, each a string object. Each document doesn't
     necessarily correspond to a file. Depending on the read_documents
     function called, each of the documents could be a chunk of a file
     based on some delineator (e.g., two consecutive newlines).
    """
    try:
        """
        documents = self.read_documents(corpus_path,
                                        corpus_file_extension)
        """
        documents = self.read_documents_by_paragraph(corpus_path,
                                                     corpus_file_extension)
    except:
        logging.warning('Reading documents encountered an error.')
        # XXX: For development, raise the exception.
        raise

    return documents


def parse_document(document):
    word_list = []
    for word in document.lower().split():
        """
        if word.isalpha() and word not in STOPLIST:
            if self.lemmatizer:
                word = self.lemmatizer.lemmatize(word)
            word_list.append(word)
        """
    return word_list
