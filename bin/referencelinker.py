#!/usr/bin/env python
from teimanipulate import *

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that looks for references to link in an NLM file and joins them to the corresponding reference entry

"""

from debug import Debuggable
import lxml


class ReferenceLinker(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Reference Linker')

    def run(self):
        pass
