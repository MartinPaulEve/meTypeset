#!/usr/bin/env python
from teimanipulate import *

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that scans for, stores and retrieves NLM citations

"""

from debug import Debuggable
import tempfile
from nlmmanipulate import NlmManipulate
import os

class BibliographyDatabase(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        self.size_cutoff = 16
        Debuggable.__init__(self, 'Bibliography Database')


    def scan(self):
        self.gv.nlm_file_path = self.gv.settings.args['<input>']
        handle, self.gv.nlm_temp_path = tempfile.mkstemp()
        os.close(handle)

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.return_elements('//element-citation')

        for item in tree:
            # todo: if we have an author and a title, store this in the database
            print item