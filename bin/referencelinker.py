#!/usr/bin/env python
"""referencelinker.py: a tool to link parenthetical references to ref-list elements in a JATS file

Usage:
    referencelinker.py scan <input> [options]
    referencelinker.py link <input> <source_id> <dest_id> [options]

Options:
    -d, --debug                                     Enable debug output
    -h, --help                                      Show this screen.
    -v, --version                                   Show version.
"""

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
import uuid
from bare_globals import GV
from docopt import docopt


class ReplaceObject(Debuggable):
    def __init__(self, global_variables, paragraph, reference_to_link):
        self.paragraph = paragraph
        self.reference_to_link = reference_to_link
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Reference Linker Object')

    def link(self):
        bib_id = ''

        if 'id' in self.reference_to_link.attrib:
            bib_id = self.reference_to_link.attrib['id']
        else:
            self.reference_to_link.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))
            bib_id = u'ID{0}'.format(unicode(uuid.uuid4()))

        self.paragraph.attrib['rid'] = bib_id

        self.debug.print_debug(self, u'Linked {0}'.format(bib_id))


class ReplaceStub(Debuggable):
    def __init__(self, global_variables, paragraph, replace_text):
        self.paragraph = paragraph
        self.replace_text = replace_text
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Reference Stub Linker Object')

    def replace_in_text(self, element):
        before_after = element.text.split(self.replace_text, 1)
        element.text = before_after[0]

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = 'TO_LINK'
        new_element.attrib['ref-type'] = 'bibr'
        new_element.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))
        new_element.text = self.replace_text
        new_element.tail = ''.join(before_after[1:])

        element.append(new_element)

    def replace_in_tail(self, element):

        before_after = element.tail.split(self.replace_text, 1)

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = 'TO_LINK'
        new_element.attrib['ref-type'] = 'bibr'
        new_element.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))
        new_element.text = self.replace_text
        new_element.tail = ''.join(before_after[1:])

        element.getparent().insert(element.getparent().index(element) + 1, new_element)

        element.tail = before_after[0]

        return new_element

    def link(self):
        # this procedure is more complex than desirable because the content can appear between tags (like italic)
        # otherwise it would be a straight replace

        if self.replace_text in self.paragraph.text:
            self.replace_in_text(self.paragraph)

            self.debug.print_debug(self, u'Successfully linked {0} stub'.format(self.replace_text))
            return

        for sub_element in self.paragraph:
            if sub_element.tag != 'xref':
                if self.replace_text in sub_element.text:
                    self.replace_in_text(sub_element)

                    self.debug.print_debug(self,
                                           u'Successfully linked {0} stub'.format(self.replace_text))
                    return

            if sub_element.tail is not None and self.replace_text in sub_element.tail:
                new_element = self.replace_in_tail(sub_element)

                self.debug.print_debug(self,
                                       u'Successfully linked {0} stub'.format(self.replace_text))

                return

        self.debug.print_debug(self, u'Failed to link {0} stub'.format(self.replace_text))


class ReferenceLinker(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Reference Linker')

    def run(self):
        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        ref_items = tree.xpath('//back/ref-list/ref')

        to_link = []
        to_stub = []

        for p in tree.xpath('//sec/p'):
            text = manipulate.get_stripped_text(p)

            reference_test = re.compile('\((?P<text>.+?)\)')
            matches = reference_test.finditer(text)

            for match in matches:
                for item in match.group('text').split(u';'):
                    to_stub.append(ReplaceStub(self.gv, p, item.strip()))

        for link in to_stub:
            link.link()
            #pass

        if len(ref_items) == 0:
            self.debug.print_debug(self, 'Found no references to link')

            tree.write(self.gv.nlm_file_path)
            tree.write(self.gv.nlm_temp_file_path)

            return

        for p in tree.xpath('//xref[@rid="TO_LINK"]'):
            text = manipulate.get_stripped_text(p)

            item = text

            bare_items = item.strip().replace(u',', '').split(u' ')

            for ref in ref_items:
                found = True

                bare_ref = manipulate.get_stripped_text(ref)

                bare_refs = bare_ref.split(' ')

                replace_chars = ',.<>\(\);:@\'\#~}{[]"'

                for sub_item in bare_items:
                    found_ref = False
                    for sub_ref in bare_refs:
                        if sub_item.strip(replace_chars) == sub_ref.strip(replace_chars):
                            found_ref = True
                            break

                    if not found_ref:
                        found = False

                if len(bare_items) > 0 and found:
                    to_link.append(ReplaceObject(self.gv, p, ref))

        if len(to_link) == 0:
            self.debug.print_debug(self, 'Found no references to link')

        for link in to_link:
            link.link()
            #pass

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

    def link_items(self, source_id, dest_id):
        self.debug.print_debug(self, 'Attempting to link XREF {0} to REF {1}'.format(source_id, dest_id))

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        source = tree.xpath('//xref[@id="{0}"]'.format(source_id))[0]
        dest = tree.xpath('//ref[@id="{0}"]'.format(dest_id))[0]

        ReplaceObject(self.gv, source, dest).link()

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

def main():
    args = docopt(__doc__, version='meTypeset 0.1')
    bare_gv = GV(args)

    if args['--debug']:
        bare_gv.debug.enable_debug()

    rl_instance = ReferenceLinker(bare_gv)

    if args['scan']:
        rl_instance.run()
    elif args['link']:
        rl_instance.link_items(args["<source_id>"], args["<dest_id>"])

if __name__ == '__main__':
    main()