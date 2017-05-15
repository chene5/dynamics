# -*- coding: utf-8 -*-
"""euclidean_distance.py
This function computes the Euclidean distance between two points in
    n-dimensional space.


Created on Sun Jun 28 14:27:54 2015

@author: Eric
"""
import sys
import getopt
import logging
import numpy
import scipy
from scipy.spatial import distance
# import gensim.matutils


__author__ = "Eric Chen"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 6/28/2015 14:27:54 $"
__copyright__ = "Copyright (c) 2015 Eric Chen"


def usage():
    print __doc__


# Parse through the command-line arguments
def parseArgs(argv):
    # Set the default logging level to INFO
    log_level = logging.INFO

    try:
        opts, args = getopt.getopt(argv, "hdi:o:", ["help",
                                                    "debug",
                                                    "input=",
                                                    "output="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            log_level = logging.DEBUG
            global _debug
            _debug = 1
        elif opt in ("-i", "--input"):
            # Stub
            print("input")
        elif opt in ("-o", "--output"):
            # Stub
            print("output")
    if __name__ == "__main__":
        logging.basicConfig(filename="log_euclidean_distance.txt",
                            level=log_level,
                            filemode="w")


def euclidean_distance(matrix1, matrix2):
    eu_distance = numpy.linalg.norm(matrix1 - matrix2)
    return eu_distance


def euclidean_distance_linalg(matrix1, matrix2):
    eu_distance = numpy.linalg.norm(matrix1 - matrix2)
    return eu_distance


def euclidean_distance_scipy(matrix1, matrix2):
    dst = distance.euclidean(matrix1, matrix2)
    return dst


def euclidean_distance_vec_lsi(vec_lsi_1, vec_lsi_2):
    matrix1 = []
    matrix2 = []

    # Create vector 1.
    for coord in vec_lsi_1:
        # print coord[1]
        matrix1.append(coord[1])

    # Create vector 2.
    for coord in vec_lsi_2:
        # print coord[1]
        matrix2.append(coord[1])

    eu_distance = scipy.spatial.distance.euclidean(matrix1, matrix2)
    return eu_distance


def cosine_sim_vec_lsi(vec_lsi_1, vec_lsi_2):
    vector1 = []
    vector2 = []

    # Create vector 1.
    for coord in vec_lsi_1:
        # print coord[1]
        vector1.append(coord[1])

    # Create vector 2.
    for coord in vec_lsi_2:
        # print coord[1]
        vector2.append(coord[1])

    cosine_similarity = 1 - distance.cosine(vector1, vector2)

    return cosine_similarity


def cosine_sim_origin(vec_lsi_1):
    vector1 = []
    vector2 = []

    # Create vector 1.
    for coord in vec_lsi_1:
        vector1.append(1)

    # Create vector 2.
    for coord in vec_lsi_1:
        vector2.append(coord[1])

    cosine_similarity = 1 - distance.cosine(vector1, vector2)
    # print 'version 2:', cosine_similarity

    return cosine_similarity


def main(argv):
    vector1 = numpy.array((1, 2, 3))
    vector2 = numpy.array((4, 5, 6))
    cosine_similarity = scipy.spatial.distance.cosine(vector1, vector2)
    print cosine_similarity

    a = numpy.array((1, 2, 3))
    b = numpy.array((4, 5, 6))
    c = scipy.dot(a, b.T)/scipy.linalg.norm(a)/scipy.linalg.norm(b)
    print c

    while True:
        try:
            one = int(raw_input('first1 '))
            two = int(raw_input('first2 '))
            three = int(raw_input('first3 '))

            vector1 = numpy.array([one, two, three])
            print vector1

            one = int(raw_input('second1 '))
            two = int(raw_input('second2 '))
            three = int(raw_input('second3 '))

            vector2 = numpy.array([one, two, three])
            print vector2
        except:
            print "oops"
            if raw_input('quit? ').lower() in ('yes', 'y', 'q'):
                break
            continue

        cosine_similarity = scipy.dot(vector1, vector2.T) / \
            scipy.linalg.norm(vector1) / \
            scipy.linalg.norm(vector2)
        print cosine_similarity

        if raw_input('done? ').lower() in ('yes', 'y', 'q'):
            break

# LET'S GO!!!
if __name__ == "__main__":
    main(sys.argv[1:])
