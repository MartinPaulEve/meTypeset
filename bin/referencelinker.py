#!/usr/bin/env python
from teimanipulate import *

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that looks for references to link in an NLM file and joins them to the corresponding reference entry

"""

from debug import Debuggable
from nlmmanipulate import NlmManipulate
import re
import lxml

class ReplaceObject():
    def __init__(self, paragraph, replace_text, reference_to_link):
        self.paragraph = paragraph
        self.replace_text = replace_text
        self.reference_to_link = reference_to_link


class ReferenceLinker(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Reference Linker')

    def run(self):
        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        ref_items = tree.xpath('//back/ref-list/ref')

        if len(ref_items) == 0:
            self.debug.print_debug(self, 'Found no references to link')
            return

        to_link = []

        for p in tree.xpath('//p'):
            text = manipulate.get_stripped_text(p)

            reference_test = re.compile('\((?P<text>.+?)\)')
            matches = reference_test.finditer(text)

            for match in matches:

                for item in match.group('text').split(u';'):

                    bare_items = item.strip().replace(u',', '').split(u' ')

                    for ref in ref_items:
                        found = True

                        bare_ref = manipulate.get_stripped_text(ref)

                        bare_refs = bare_ref.split(' ')

                        for sub_item in bare_items:
                            found_ref = False
                            for sub_ref in bare_refs:
                                if sub_item == sub_ref.strip(',.<>();:@\'\#~}{[]"'):
                                    found_ref = True

                            if not found_ref:
                                found = False

                        if len(bare_items) > 0 and found:
                            to_link.append(ReplaceObject(p, item, ref))



