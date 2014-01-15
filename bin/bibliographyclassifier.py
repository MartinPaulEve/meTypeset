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
        self.size_cutoff = 16
        Debuggable.__init__(self, 'Bibliography Classifier')