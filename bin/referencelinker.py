#!/usr/bin/env python
"""referencelinker.py: a tool to link parenthetical references to ref-list elements in a JATS file

Usage:
    referencelinker.py scan <input> [options]
    referencelinker.py link <input> <source_id> <dest_id> [options]
    referencelinker.py prune <input> [options]

Options:
    -d, --debug                                     Enable debug output
    --interactive                                   Prompt the user to assist in interactive tagging
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
from interactive import Interactive


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
    def __init__(self, global_variables, paragraph, replace_text, tree, manipulate):
        self.paragraph = paragraph
        self.replace_text = replace_text
        self.gv = global_variables
        self.debug = self.gv.debug
        self.tree = tree
        self.manipulate = manipulate
        Debuggable.__init__(self, 'Reference Stub Linker Object')

    def replace_in_text(self, element):
        if not self.replace_text in element.text:
            # safety check: if not in the text, just return
            return element

        before_after = element.text.split(self.replace_text, 1)

        encapsulate = etree.Element(element.tag)
        encapsulate.text = before_after[0]

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = 'TO_LINK'
        new_element.attrib['ref-type'] = 'bibr'
        new_element.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))
        new_element.text = self.replace_text
        new_element.tail = ''.join(before_after[1:])

        Manipulate.append_safe(encapsulate, new_element, self)

        for sub_element in element:
            Manipulate.append_safe(encapsulate, sub_element, self)

        element.addnext(encapsulate)
        element.getparent().remove(element)

        return encapsulate

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

    def replace_in_text_and_update_others(self, object_list):
        to_update = []
        if object_list is not None:
            for item in object_list:
                if item.paragraph is self.paragraph:
                    to_update.append(item)

        self.paragraph = self.replace_in_text(self.paragraph)

        for item in to_update:
            item.paragraph = self.paragraph

    def link(self, object_list = None):
        # this procedure is more complex than desirable because the content can appear between tags (like italic)
        # otherwise it would be a straight replace

        if self.replace_text is not None and self.replace_text == '':
            self.debug.print_debug(self, u'Replace text is empty: bailing')
            return

        if self.paragraph.text and self.replace_text in self.paragraph.text and len(self.paragraph) > 0:
            self.replace_in_text_and_update_others(object_list)

            self.manipulate.save_tree(self.tree)

            self.debug.print_debug(self, u'Successfully linked {0} stub with sub elements'.format(self.replace_text))

            self.tree = self.manipulate.load_dom_tree()

            return

        if self.paragraph.text and self.replace_text in self.paragraph.text and len(self.paragraph) == 0:
            self.replace_in_text_and_update_others(object_list)
            self.paragraph = self.replace_in_text(self.paragraph)

            self.manipulate.save_tree(self.tree)

            self.debug.print_debug(self, u'Successfully linked {0} stub'.format(self.replace_text))

            self.tree = self.manipulate.load_dom_tree()
            return

        for sub_element in self.paragraph:
            if sub_element.tag != 'xref':
                if sub_element.text and self.replace_text in sub_element.text:
                    self.replace_in_text(sub_element)

                    self.manipulate.save_tree(self.tree)

                    self.debug.print_debug(self,
                                           u'Successfully linked {0} stub from sub element'.format(self.replace_text))
                    return

            if sub_element.tail is not None and self.replace_text in sub_element.tail:
                new_element = self.replace_in_tail(sub_element)

                self.manipulate.save_tree(self.tree)

                self.debug.print_debug(self,
                                       u'Successfully linked {0} stub from sub element tail'.format(self.replace_text))

                return


        self.debug.print_debug(self, u'Failed to link {0} stub'.format(self.replace_text))


class ReferenceLinker(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Reference Linker')

    def run(self, interactive):
        if interactive:
            self.run_prompt()
            return

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        ref_items = tree.xpath('//back/ref-list/ref')

        parsed = 0

        for ref in ref_items:
            if ref.text is not None and ord(ref.text[0]) == 8212 and ord(ref.text[1]) == 8212 and \
                            ord(ref.text[2]) == 8212 and ref.text[3] == '.':
                try:
                    current = ref

                    while True:
                        previous = current
                        current = current.getprevious()

                        if current is None:
                            break

                        if current.text is not None and ord(current.text[0]) != 8212:
                            authorname = current.text.split('.')[0]

                            ref.text = authorname + ref.text[3:]
                            parsed += 1
                            break

                except:
                    pass

        if parsed > 0:

            tree.write(self.gv.nlm_file_path)
            tree.write(self.gv.nlm_temp_file_path)

            self.debug.print_debug(self, u'Replace {0} instances of "---." at start of references'.format(parsed))

        to_link = []
        to_stub = []

        for p in tree.xpath('//sec/p[not(mml:math)]',
                            namespaces={'mml': '"http://www.w3.org/1998/Math/MathML"'}):

            text = manipulate.get_stripped_text(p)

            reference_test = re.compile('^.+\((?P<text>.+?)\)')
            matches = reference_test.finditer(text)

            for match in matches:
                for item in match.group('text').split(u';'):
                    to_stub.append(ReplaceStub(self.gv, p, item.strip(), tree, manipulate))

        for link in to_stub:
            link.link(to_stub)
            #pass

        if len(ref_items) == 0:
            self.debug.print_debug(self, u'Found no references to link')

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
            self.debug.print_debug(self, u'Found no references to link')

        for link in to_link:
            link.link()
            #pass

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

    def search_references(self, search_term, ref_items, manipulate, input_block):
        results = []

        for ref in ref_items:
            found = True

            bare_ref = manipulate.get_stripped_text(ref)

            bare_refs = bare_ref.split(' ')

            replace_chars = ',.<>\(\);:@\'\#~}{[]"'

            found_ref = False

            for sub_ref in bare_refs:
                if search_term.strip(replace_chars).lower() == sub_ref.strip(replace_chars).lower():
                    found_ref = True
                    break

            if not found_ref:
                found = False

            if found:
                results.append(ReplaceObject(self.gv, input_block, ref))

        return results

    def link_items(self, source_id, dest_id):
        self.debug.print_debug(self, u'Attempting to link XREF {0} to REF {1}'.format(source_id, dest_id))

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        source = tree.xpath('//xref[@id="{0}"]'.format(source_id))[0]
        dest = tree.xpath('//ref[@id="{0}"]'.format(dest_id))[0]

        ReplaceObject(self.gv, source, dest).link()

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

    def handle_search(self, manipulate, opts, p, prompt, ref_items):
        name = prompt.input_('Enter search term:')
        result_list = self.search_references(name, ref_items, manipulate, p)
        sel = prompt.choose_candidate(result_list, manipulate, opts)

        self.handle_input(manipulate, opts, p, prompt, ref_items, sel, result_list)
        pass

    def extract_contents(self, p):
        p.tag = 'REMOVE'

        etree.strip_tags(p.getparent(), 'REMOVE')

    def handle_input(self, manipulate, opts, p, prompt, ref_items, sel, candidates=None):
        if sel == 'a':
            prompt.print_(u"Leaving interactive mode on user command")
            return "abort"
        elif sel == 'd':
            # delete the surrounding xref
            self.debug.print_debug(self, u'Deleting reference {0}'.format(p.attrib['id']))
            self.extract_contents(p)
            pass
        elif sel == 'e':
            # let the user search references
            self.handle_search(manipulate, opts, p, prompt, ref_items)
        elif sel == 'l':
            # directly link the item
            ref_id = prompt.input_('Enter reference ID:')
            self.link_items(p.attrib['id'], ref_id)
            pass
        elif sel == 's':
            # skip this item
            prompt.print_(u'Skipping this item')
            pass
        elif sel == 't':
            # delete all
            self.debug.print_debug(self, u'Deleting reference {0}'.format(p.attrib['id']))
            self.extract_contents(p)
            return "delall"
        else:
            # numerical input
            selected = candidates[sel - 1]

            # do link
            selected.link()


    def run_prompt(self):
        self.debug.print_debug(self, u'Entering interactive mode')

        prompt = Interactive(self.gv)

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        ref_items = tree.xpath('//back/ref-list/ref')

        # note that we don't want to exit even if there are no references to link because the user may want to delete
        # some

        delete_all = False

        for p in tree.xpath('//xref[@ref-type="bibr"]'):
            text = manipulate.get_stripped_text(p)

            if 'rid' in p.attrib and p.attrib['rid'] == 'TO_LINK':
                prompt.print_(u"Found an unhandled reference marker: {0}".format(text))
            elif 'rid' in p.attrib:
                remote = next((x for x in ref_items if x.attrib['id'] == p.attrib['rid']), None)
                remote_text = manipulate.get_stripped_text(remote)
                prompt.print_(u"Found a handled reference marker: \"{0}\" which links to \"{1}\"".format(text,
                                                                                                         remote_text))

            opts = ('Skip', 'Delete', 'deleTe all', 'Enter search', 'enter Link id', 'Abort')

            sel = ''

            if delete_all:
                sel = 'd'
            else:
                sel = prompt.input_options(opts)

            result = self.handle_input(manipulate, opts, p, prompt, ref_items, sel)

            if result == 'abort':
                return
            elif result == 'delall':
                delete_all = True

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

    def prune(self):
        self.debug.print_debug(self, u'Deleting all stubs from article')

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        for p in tree.xpath('//xref[@ref-type="bibr" and @rid="TO_LINK"]'):
            self.extract_contents(p)

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)


def main():
    args = docopt(__doc__, version='meTypeset 0.1')
    bare_gv = GV(args)

    if args['--debug']:
        bare_gv.debug.enable_debug()

    rl_instance = ReferenceLinker(bare_gv)

    if args['scan']:
        rl_instance.run(args['--interactive'])

    elif args['link']:
        rl_instance.link_items(args["<source_id>"], args["<dest_id>"])

    elif args['prune']:
        rl_instance.prune()

if __name__ == '__main__':
    main()