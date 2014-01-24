#!/usr/bin/env python
from teimanipulate import *

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that assists with bibliography classification.
"""

from debug import Debuggable

class BibliographyClassifier(Debuggable):

    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Bibliography Classifier')

    def run(self):
        tei_manipulator = TeiManipulate(self.gv)

        tei_manipulator.find_reference_list_in_word_list()
        tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')