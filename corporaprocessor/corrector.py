# -*- coding: utf-8 -*-
"""corrector.py
Spelling corrector.

From Peter Norvig:
http://norvig.com/spell-correct.html

Created on Mon Jun 29 20:34:35 2015

@author: Eric
"""
import re, collections

class Corrector:
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    def __init__(self, dictionary):
        # XXX Not sure if I want to carry around the whole dictionary in memory
        #self.dictionary = dictionary
        self.NWORDS = self.train(self.words(dictionary))

    def words(self, text): 
        return re.findall('[a-z]+', text.lower()) 

    def train(self, features):
        model = collections.defaultdict(lambda: 1)
        for f in features:
            model[f] += 1
        return model

    def edits1(self, word):
       splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
       deletes    = [a + b[1:] for a, b in splits if b]
       transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
       replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
       inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
       return set(deletes + transposes + replaces + inserts)

    def known_edits2(self, word):
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.NWORDS)

    def known(self, words): 
        return set(w for w in words if w in self.NWORDS)

    def correct(self, word):
        print "    Checking", word
        candidates = self.known([word])
        if candidates:
            print "        I know", word
            return max(candidates, key=self.NWORDS.get)
        candidates = self.known(self.edits1(word)) or self.known_edits2(word)
        print "        Candidates:", candidates
        if candidates:
            suggestion = max(candidates, key=self.NWORDS.get)
            response = raw_input("Did you mean {}? ".format(suggestion)).lower()
            if response == 'yes' or response == '':
                print '    ok'
            else:
                print '    nevermind then'
                suggestion = word

        print "    Here's the word:", suggestion
        return suggestion


def check_corrector():
    corrector = Corrector(file('big.txt').read())
    while True:
        new_word = raw_input('---> ')
        if new_word.lower() == 'abandon ship':
            print("Goodbye!")
            break
        print corrector.correct(new_word)

# LET'S GO!!!
if __name__ == "__main__":
    check_corrector()

