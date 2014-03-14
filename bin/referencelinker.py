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
            bib_id = self.reference_to_link.attrib['id']

        self.paragraph.attrib['rid'] = bib_id

        self.debug.print_debug(self, u'Linked {0}'.format(bib_id))


class ReplaceStub(Debuggable):
    def __init__(self, global_variables, paragraph, replace_text, tree, manipulate, link_text='TO_LINK',
                 length_ignore=False):
        self.paragraph = paragraph
        self.replace_text = replace_text
        self.gv = global_variables
        self.debug = self.gv.debug
        self.tree = tree
        self.manipulate = manipulate
        self.link_text = link_text
        self.length_ignore = length_ignore
        Debuggable.__init__(self, 'Reference Stub Linker Object')

    def replace_in_text(self, element, link_text):
        if not self.replace_text in element.text:
            # safety check: if not in the text, just return
            return element

        before_after = element.text.split(self.replace_text, 1)

        encapsulate = etree.Element(element.tag)
        encapsulate.text = before_after[0]

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = link_text
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

    def replace_in_tail(self, element, link_text):

        before_after = element.tail.split(self.replace_text, 1)

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = link_text
        new_element.attrib['ref-type'] = 'bibr'
        new_element.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))
        new_element.text = self.replace_text
        new_element.tail = ''.join(before_after[1:])

        element.getparent().insert(element.getparent().index(element) + 1, new_element)

        element.tail = before_after[0]

        return new_element

    def replace_in_text_and_update_others(self, object_list, link_text):
        to_update = []
        if object_list is not None:
            for item in object_list:
                if item.paragraph is self.paragraph:
                    to_update.append(item)

        self.paragraph = self.replace_in_text(self.paragraph, self.link_text)

        for item in to_update:
            item.paragraph = self.paragraph

    def link(self, object_list=None):
        # this procedure is more complex than desirable because the content can appear between tags (like italic)
        # otherwise it would be a straight replace
        linked = False
        in_xref = False

        if self.replace_text is not None and self.replace_text == '':
            self.debug.print_debug(self, u'Replace text is empty: bailing')
            return

        if not self.length_ignore and len(self.replace_text) < 3:
            try:
                attempt = int(self.replace_text)
            except:
                self.debug.print_debug(self, u'Replace text is too short: bailing')
                return

        if self.paragraph.text and self.replace_text in self.paragraph.text and len(self.paragraph) > 0:
            self.replace_in_text_and_update_others(object_list, self.link_text)

            self.manipulate.save_tree(self.tree)

            self.debug.print_debug(self, u'Successfully linked {0} stub with sub elements'.format(self.replace_text))
            linked = True

            self.tree = self.manipulate.load_dom_tree()

        if self.paragraph.text and self.replace_text in self.paragraph.text and len(self.paragraph) == 0:
            self.replace_in_text_and_update_others(object_list, self.link_text)
            self.paragraph = self.replace_in_text(self.paragraph, self.link_text)

            self.manipulate.save_tree(self.tree)

            self.debug.print_debug(self, u'Successfully linked {0} stub'.format(self.replace_text))
            linked = True

            self.tree = self.manipulate.load_dom_tree()

        for sub_element in self.paragraph:
            if sub_element.tag != 'xref':
                if sub_element.text and self.replace_text in sub_element.text:
                    self.replace_in_text(sub_element, self.link_text)

                    self.manipulate.save_tree(self.tree)

                    self.debug.print_debug(self,
                                           u'Successfully linked {0} stub from sub element'.format(self.replace_text))
                    linked = True
            else:
                in_xref = True

            if sub_element.tail is not None and self.replace_text in sub_element.tail:
                new_element = self.replace_in_tail(sub_element, self.link_text)

                self.manipulate.save_tree(self.tree)

                self.debug.print_debug(self,
                                       u'Successfully linked {0} stub from sub element tail'.format(self.replace_text))
                linked = True

        if not linked:
            if not in_xref:
                # likelihood here is that we have something like this:
                # (<italic>Text Name</italic> 354)
                # or
                # (text <italic>something</italic>)
                # this requires a more complex approach: we will fallback to the less safe method of using tostring
                # doing a regex replace and then re-encapsulating with fromstring

                in_string = etree.tostring(self.paragraph)

                regex = u'\((?P<text>.*?'

                # add each word and allow for tags in between. Do not allow the term "xref" to appear.
                for sub_string in self.replace_text.split(' '):
                    regex += u'[^(xref)]*?'

                regex += u')\)'

                xref_before = u'<xref ref-type="bibr" ' \
                              u'id="{0}" rid="{1}">'.format(u'ID{0}'.format(unicode(uuid.uuid4())), self.link_text)
                xref_after = u'</xref>'

                new_text = re.sub(regex, u'({0}\g<text>{1})'.format(xref_before, xref_after), in_string)

                new_element = etree.fromstring(new_text)

                if etree.tostring(new_element) == in_string:
                    self.debug.print_debug(self, u'Did not link {0} stub'.format(self.replace_text))
                else:
                    # a change has been made
                    self.paragraph.addnext(new_element)
                    self.paragraph.tag = 'REMOVE'
                    self.debug.print_debug(self, u'Linked {0} stub using regex method'.format(self.replace_text))

                    self.manipulate.save_tree(self.tree)


class ReferenceLinker(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        self.ibid = None
        Debuggable.__init__(self, 'Reference Linker')

    def process_ibid_authors(self, ref_items):
        parsed = 0
        # this checks for items beginning with "---." and replaces them with the real author name
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

            elif ref.text is not None and ref.text.startswith('_'):
                ref.text = ref.text.strip('_')

                try:
                    current = ref

                    while True:
                        previous = current
                        current = current.getprevious()

                        if current is None:
                            break

                        if current.text is not None and ord(current.text[0]) != 8212 or current.text[0] != '_':
                            authorname = current.text.split('.')[0]

                            ref.text = authorname + ref.text
                            parsed += 1
                            break

                except:
                    pass

        return parsed

    def clean_ref_items(self, tree, ref_items, manipulate):
        allowed_tags = ['italic', 'bold', 'sup', 'sub']

        for ref in ref_items:
            for item in ref:
                if not item.tag in allowed_tags:
                    item.tag = 'REMOVE'

        etree.strip_tags(tree, 'REMOVE')

        manipulate.save_tree(tree)
        self.debug.print_debug(self, u'Stripped disallowed tags from reference tree')

    def run(self, interactive):
        if interactive:
            self.run_prompt()
            return

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        # pre-cleanup: remove all empty ext-links as these break the linker
        items_to_clean = tree.xpath('//ext-link')

        count = 0

        for item in items_to_clean:
            if '{http://www.w3.org/1999/xlink}href' in item.attrib and \
                    item.attrib['{http://www.w3.org/1999/xlink}href'] == '':
                count += 1
                item.tag = 'REMOVE'
                etree.strip_tags(item.getparent(), 'REMOVE')

        if count > 0:
            manipulate.save_tree(tree)
            self.debug.print_debug(self, u'Removed {0} blank ext-link tags'.format(count))

        ref_items = tree.xpath('//back/ref-list/ref')

        self.clean_ref_items(tree, ref_items, manipulate)

        # handle numbered reference items
        references_and_numbers = {}

        for ref in ref_items:
            text = manipulate.get_stripped_text(ref)
            ref_match = re.compile('^(?P<number>\d+)\.*')
            result = ref_match.match(text)

            if result:
                references_and_numbers[result.group('number')] = ref

        parsed = self.process_ibid_authors(ref_items)

        if parsed > 0:

            manipulate.save_tree(tree)

            self.debug.print_debug(self, u'Replace {0} instances of "---." at start of references'.format(parsed))

        to_link = []
        to_stub = []

        square_bracket_count = {}


        for p in tree.xpath('//sec//p[not(mml:math)] | //td',
                            namespaces={'mml': 'http://www.w3.org/1998/Math/MathML'}):

            text = manipulate.get_stripped_text(p)

            reference_test = re.compile('\((?P<text>.+?)\)')
            matches = reference_test.finditer(text)

            # exclude any square brackets with numbers inside
            sub_match = re.compile('\[(?P<square>\d*[,\-;\d\s]*)\]')
            smatch = sub_match.search(text)

            if smatch:
                smatches = sub_match.finditer(text)
                for smatch in smatches:
                    self.debug.print_debug(self, u'Handling references in square '
                                                 u'brackets: [{0}] '.format(smatch.group('square')))
                    for item in re.split(';|,', smatch.group('square')):
                        if '-' in item:
                            parent, tail = manipulate.find_text(p, item)

                            if parent is not None:
                                new_string = ''

                                try:
                                    split_range = item.strip().split('-')
                                    for no in range(int(split_range[0]), int(split_range[1]) + 1):
                                        new_string += str(no) + ','
                                except:
                                    self.debug.print_debug(self, u'Unable to parse reference '
                                                                 u'number in range {0}'.format(item))
                                    break

                                if new_string.endswith(',') and not item.endswith(','):
                                    new_string = new_string[0:len(new_string) - 1]

                                if tail and new_string != '':
                                    parent.tail = parent.tail.replace(item, new_string)
                                elif not tail and new_string != '':
                                    parent.text = parent.text.replace(item, new_string)

                                try:
                                    split_range = item.strip().split('-')
                                    for no in range(int(split_range[0]), int(split_range[1]) + 1):
                                        self.debug.print_debug(self, u'Parsing reference '
                                                                     u'number in range {0}'.format(str(no)))

                                        to_stub.append(ReplaceStub(self.gv, p, str(no), tree, manipulate,
                                                                   'TO_LINK_NUMBER', length_ignore=True))
                                except:
                                    self.debug.print_debug(self, u'Unable to parse reference '
                                                                 u'number in range {0}'.format(item))
                                    break

                            else:
                                # just replace the components
                                split_range = item.strip().split('-')
                                for link in split_range:
                                    to_stub.append(ReplaceStub(self.gv, p, link, tree, manipulate,
                                                               'TO_LINK_NUMBER', length_ignore=True))
                        else:
                            if len(item.strip()) < 60:
                                to_stub.append(ReplaceStub(self.gv, p, item.strip(), tree, manipulate, 'TO_LINK_NUMBER',
                                                           length_ignore=True))

                        square_bracket_count[item.strip()] = 1
            else:
                for match in matches:
                    for item in match.group('text').split(u';'):
                        if len(item.strip()) < 60:
                            to_stub.append(ReplaceStub(self.gv, p, item.strip(), tree, manipulate))

        for link in to_stub:
            link.link(to_stub)
            #pass

        etree.strip_elements(tree, 'REMOVE')

        use_index_method = False

        if len(square_bracket_count) != len(references_and_numbers):
            # we found more than 3 [1], [2] style references but no reference elements beginning with numbers
            # so, we will simply try to use the /index/ of the reference item (-1 for zero-based compensation)
            self.debug.print_debug(self, u'Using indexical method for square bracket correlation')
            use_index_method = True

        if len(ref_items) == 0:
            self.debug.print_debug(self, u'Found no references to link')

            manipulate.save_tree(tree)

            return

        for p in tree.xpath('//xref[@rid="TO_LINK_NUMBER"]'):
            text = manipulate.get_stripped_text(p)

            if not use_index_method:
                if text in references_and_numbers:
                    ReplaceObject(self.gv, p, references_and_numbers[text]).link()
                else:
                    p.attrib['rid'] = 'TO_LINK'
            else:
                try:
                    ReplaceObject(self.gv, p, ref_items[int(text) - 1]).link()
                except:
                    self.debug.print_debug(self, u'Failed to link to reference {0} + 1 using '
                                                 u'indexical method'.format(text))
                    p.attrib['rid'] = 'TO_LINK'

        for p in tree.xpath('//xref[@rid="TO_LINK"]'):
            text = manipulate.get_stripped_text(p)

            item = text

            bare_items = item.strip().replace(u',', '').split(u' ')

            for ref in ref_items:
                found = True

                bare_ref = manipulate.get_stripped_text(ref)

                bare_refs = bare_ref.split(' ')

                replace_chars = '[,\.\<\>\(\)\;\:\@\'\#\~\}\{\[\]\"]'

                for sub_item in bare_items:
                    found_ref = False
                    for sub_ref in bare_refs:
                        if re.sub(replace_chars, '', sub_item.strip()).strip() == sub_ref.strip(replace_chars):
                            found_ref = True
                            break

                    if not found_ref:
                        found = False

                if len(bare_items) > 0 and found:
                    to_link.append(ReplaceObject(self.gv, p, ref))

                elif len(bare_items) > 0:
                    replace_chars = '[,\.\<\>\(\)\;\:\@\'\#\~\}\{\[\]\"\d]'
                    found = True

                    for sub_item in bare_items:
                        found_ref = False
                        subbed_text = re.sub(replace_chars, '', sub_item.strip()).strip()
                        for sub_ref in bare_refs:
                            sub_ref = re.sub(replace_chars, '', sub_ref.strip()).strip()

                            if subbed_text == '' and len(bare_items) > 1:
                                found_ref = True
                                break

                            if subbed_text == sub_ref and subbed_text != '' and sub_ref != '':
                                found_ref = True
                                break

                        if not found_ref:
                            found = False

                    # we don't allow linking to the last item here because it is almost universally wrong
                    if len(bare_items) > 0 and found and ref_items.index(ref) != len(ref_items) - 1:
                        to_link.append(ReplaceObject(self.gv, p, ref))


        if len(to_link) == 0:
            self.debug.print_debug(self, u'Found no references to link')

        for link in to_link:
            link.link()
            #pass

        manipulate.save_tree(tree)

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

    def link_items(self, source_id, dest_id, manipulate=None, tree=None):
        self.debug.print_debug(self, u'Attempting to link XREF {0} to REF {1}'.format(source_id, dest_id))

        if manipulate is None:
            manipulate = NlmManipulate(self.gv)

        if tree is None:
            tree = manipulate.load_dom_tree()

        source = tree.xpath('//xref[@id="{0}"]'.format(source_id))[0]
        dest = tree.xpath('//ref[@id="{0}"]'.format(dest_id))[0]

        ReplaceObject(self.gv, source, dest).link()

        manipulate.save_tree(tree)

    def handle_search(self, manipulate, opts, p, prompt, ref_items):
        name = prompt.input_('Enter search term:')
        result_list = self.search_references(name, ref_items, manipulate, p)
        sel = prompt.choose_candidate(result_list, manipulate, opts)

        self.handle_input(manipulate, opts, p, prompt, ref_items, sel, result_list)
        pass

    def cleanup(self):
        manipulate = NlmManipulate(self.gv)
        manipulate.remove_reference_numbering()

    def extract_contents(self, p):
        p.tag = 'REMOVE'

        etree.strip_tags(p.getparent(), 'REMOVE')

    def handle_input(self, manipulate, opts, p, prompt, ref_items, sel, candidates=None, tree=None):
        if sel == 'r':
            prompt.print_(u"Leaving interactive mode on user command")
            return "abort"
        elif sel == 'd':
            # delete the surrounding xref
            self.debug.print_debug(self, u'Deleting reference {0}'.format(p.attrib['id']))
            self.extract_contents(p)
            self.ibid = None
        elif sel == 'e':
            # let the user search references
            self.handle_search(manipulate, opts, p, prompt, ref_items)
        elif sel == 'i':
            if self.ibid is None:
                self.debug.print_debug(self, u'Cannot ibid')
                sel = prompt.input_options(opts)
                self.handle_input(manipulate, opts, p, prompt, ref_items, sel)
            else:
                self.debug.print_debug(self, u'Linking to ibid ID {0}'.format(self.ibid))

                self.link_items(p.attrib['id'], self.ibid, manipulate=manipulate, tree=tree)
        elif sel == 'l':
            # directly link the item
            ref_id = prompt.input_('Enter reference ID:')
            self.link_items(p.attrib['id'], ref_id)
            self.ibid = ref_id
            pass
        elif sel == 'c':
            text = manipulate.get_stripped_text(p.getparent())
            replace_text = manipulate.get_stripped_text(p)

            text = text.replace(replace_text, prompt.colorize('green', replace_text))

            prompt.print_(text)
            sel = prompt.input_options(opts)
            result = self.handle_input(manipulate, opts, p, prompt, ref_items, sel, tree=tree)
            return result
        elif sel == 's':
            # skip this item
            prompt.print_(u'Skipping this item')
            self.ibid = None
            pass
        elif sel == 't':
            # delete all
            self.debug.print_debug(self, u'Deleting reference {0}'.format(p.attrib['id']))
            self.extract_contents(p)
            self.ibid = None
            return "delall"
        else:
            # numerical input
            selected = candidates[sel - 1]

            # do link
            selected.link()

            self.ibid = selected.reference_to_link.attrib['id']

    def run_prompt(self):
        self.run(False)
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
                remote = next((x for x in ref_items if 'id' in x.attrib and (x.attrib['id'] == p.attrib['rid'])), None)
                remote_text = manipulate.get_stripped_text(remote)
                prompt.print_(u"Found a handled reference marker: \"{0}\" which links to \"{1}\"".format(text,
                                                                                                         remote_text))

            opts = ('Skip', 'Delete', 'deleTe all', 'Enter search', 'Ibid', 'enter Link id',
                    'skip Rest', 'show Context')

            sel = ''

            if delete_all:
                sel = 'd'
            else:
                sel = prompt.input_options(opts)

            result = self.handle_input(manipulate, opts, p, prompt, ref_items, sel, tree=tree)

            if result == 'abort':
                manipulate.save_tree(tree)
                return
            elif result == 'delall':
                delete_all = True

            manipulate.save_tree(tree)

    def prune(self):
        self.debug.print_debug(self, u'Deleting all stubs from article')

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        for p in tree.xpath('//xref[@ref-type="bibr" and @rid="TO_LINK"]'):
            self.extract_contents(p)

        manipulate.save_tree(tree)


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