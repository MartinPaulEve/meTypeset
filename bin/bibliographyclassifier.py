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

    def linguistic_cues(self, manipulate, tree):
        language_list = self.gv.value_for_tag(self.gv.settings, 'references-languages')

        for language in language_list:
            with open ('{0}/../languages/ref_marker_{1}.txt'.format(self.gv.script_dir,
                                                                    language), 'r') as lang_file:
                lines = lang_file.read().split('\n')

                for line in lines:
                    manipulate.find_references_from_cue(line, tree)


    def run(self):
        if int(self.gv.settings.args['--aggression']) < 4:
            self.debug.print_debug(self, 'Aggression level less than 4: exiting module.')
            return

        tei_manipulator = TeiManipulate(self.gv)

        tei_manipulator.find_reference_list_in_word_list()

        tree = tei_manipulator.load_dom_tree()

        self.linguistic_cues(tei_manipulator, tree)

        tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')