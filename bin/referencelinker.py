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
import hashlib


class ReplaceObject(Debuggable):
    def __init__(self, global_variables, paragraph, replace_text, reference_to_link):
        self.paragraph = paragraph
        self.replace_text = replace_text
        self.reference_to_link = reference_to_link
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Reference Linker Object')

    def link(self):
        # this procedure is more complex than desirable because the content can appear between tags (like italic)
        # otherwise it would be a straight replace

        id = ''

        if 'id' in self.reference_to_link.attrib:
            id = self.reference_to_link.attrib['id']
        else:
            hash_object = hashlib.sha256(etree.tostring(self.reference_to_link))
            hex_dig = hash_object.hexdigest()
            self.reference_to_link.attrib['id'] = hex_dig
            id = hex_dig

        self.debug.print_debug(self, u'Attempting to link {0} to {1}'.format(self.replace_text, id))

        if self.replace_text in self.paragraph.text:
            before_after = self.paragraph.text.split(self.replace_text)

            self.paragraph.text = before_after[0]

            new_element = etree.Element('xref')
            new_element.attrib['rid'] = 'AFJD'
            new_element.attrib['ref-type'] = 'bibr'
            new_element.text = self.replace_text
            new_element.tail = before_after[1]

            self.paragraph.append(new_element)

        pass


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
                            to_link.append(ReplaceObject(self.gv, p, item.strip(), ref))

        for link in to_link:
            link.link()

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)


