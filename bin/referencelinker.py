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
from bare_globals import GV


class ReplaceObject(Debuggable):
    def __init__(self, global_variables, paragraph, replace_text, reference_to_link):
        self.paragraph = paragraph
        self.replace_text = replace_text
        self.reference_to_link = reference_to_link
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Reference Linker Object')

    def replace_in_text(self, id, element):
        before_after = element.text.split(self.replace_text, 1)
        element.text = before_after[0]

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = unicode(id)
        new_element.attrib['ref-type'] = 'bibr'
        new_element.text = self.replace_text
        new_element.tail = ''.join(before_after[1:])

        element.append(new_element)

    def replace_in_tail(self, id, element):

        before_after = element.tail.split(self.replace_text, 1)

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = unicode(id)
        new_element.attrib['ref-type'] = 'bibr'
        new_element.text = self.replace_text
        new_element.tail = ''.join(before_after[1:])

        element.getparent().insert(element.getparent().index(element) + 1, new_element)

        element.tail = before_after[0]

        return new_element

    def link(self):
        # this procedure is more complex than desirable because the content can appear between tags (like italic)
        # otherwise it would be a straight replace

        bib_id = ''

        if 'id' in self.reference_to_link.attrib:
            bib_id = self.reference_to_link.attrib['id']
        else:
            hash_object = hashlib.sha256(etree.tostring(self.reference_to_link))
            hex_dig = hash_object.hexdigest()
            self.reference_to_link.attrib['id'] = hex_dig
            bib_id = hex_dig

        if self.replace_text in self.paragraph.text:
            self.replace_in_text(bib_id, self.paragraph)

            self.debug.print_debug(self, u'Successfully linked {0} to {1}'.format(self.replace_text, bib_id))
            return

        for sub_element in self.paragraph:
            if sub_element.tag != 'xref':
                if self.replace_text in sub_element.text:
                    self.replace_in_text(bib_id, sub_element)

                    self.debug.print_debug(self,
                                           u'Successfully linked {0} to {1} from sub-element'.format(self.replace_text,
                                                                                                     bib_id))
                    return

            if sub_element.tail is not None and self.replace_text in sub_element.tail:
                new_element = self.replace_in_tail(bib_id, sub_element)

                self.debug.print_debug(self,
                                       u'Successfully linked {0} to {1} from sub-tail'.format(self.replace_text, bib_id))

                return

        self.debug.print_debug(self, u'Failed to link {0} to {1}'.format(self.replace_text, bib_id))


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
            #pass

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)


def main():
    #bare_gv = GV()

    rl_instance = ReferenceLinker()
    #rl_instance.run()


if __name__ == '__main__':
    main()