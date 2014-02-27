#!/usr/bin/env python
from teimanipulate import *

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that looks for common list encodings and handles them properly.

1.) Identifies lists
2.) Converts them to proper TEI list format
"""

from debug import Debuggable
import math
from copy import copy
import re


class ListClassifier(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'List Classifier')

    @staticmethod
    def set_dom_tree(filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

        return etree.parse(filename, p)

    def handle_reference_item(self, element, elements, in_list_run, iteration, list_element, offset, to_append):
        iteration += 1
        # treat as ref list
        self.debug.print_debug(self, u'Handling reference element {0}'.format(element.text))
        if not in_list_run:
            list_element = etree.Element('ref')
            list_element.attrib['target'] = 'None'
            to_append = None
            in_list_run = True
            element.addprevious(list_element)
        if not element.getnext().text is None:
            if element.getnext().text.startswith(u'[') and not element.getnext() in elements:
                # this element is the last in this list
                in_list_run = False
                to_append = element.getnext()
            elif not element.getnext().text.startswith(u'['):
                # anomalous ref
                self.debug.print_debug(self, u'Ref missing marker {0}'.format(element.getnext().text))
                element.text = element.text + element.getnext().text
                element.getnext().text = ''
        else:
            # this can happen with italics
            self.debug.print_debug(self, u'Ref run/anomaly on {0}'.format(element.getnext()))
            for sub_element in element.getnext():
                element.append(sub_element)
            in_list_run = False
            to_append = element.getnext()

        element.tag = 'p'
        element.attrib['rend'] = u'Bibliography'

        element.text = element.text[(int(offset) + int(math.floor(int(iteration / 10)))):]
        list_element.append(element)

        if not in_list_run:
            if not to_append is None:
                if not to_append.text is None:
                    to_append.tag = 'p'
                    to_append.attrib['rend'] = u'Bibliography'
                    to_append.text = to_append.text[(int(offset) + int(math.floor(int(iteration / 10)))):]
                    self.debug.print_debug(self, u'Appending ref element: {0}'.format(to_append.text))
                    list_element.append(to_append)
        return iteration

    def handle_footnote_item(self, element, elements, in_list_run, iteration, list_element, offset, to_append):
        iteration += 1
        # treat as fn-list list
        self.debug.print_debug(self, u'Handling footnote element {0}'.format(element.text))
        if not in_list_run:
            list_element = etree.Element('fn-group')
            to_append = None
            in_list_run = True
            element.addprevious(list_element)
        if not element.getnext().text is None:
            if element.getnext().text.startswith(u'[') and not element.getnext() in elements:
                # this element is the last in this list
                in_list_run = False
                to_append = element.getnext()
            elif not element.getnext().text.startswith(u'['):
                # anomalous ref
                self.debug.print_debug(self, u'Footnote missing marker {0}'.format(element.getnext().text))
                element.text = element.text + element.getnext().text
                element.getnext().text = ''
        else:
            # this can happen with italics
            self.debug.print_debug(self, u'Footnote run/anomaly on {0}'.format(element.getnext()))
            for sub_element in element.getnext():
                element.append(sub_element)
            in_list_run = False
            to_append = element.getnext()
        element.tag = 'note'
        element.attrib['id'] = 'fn_from_list{0}'.format(iteration)
        element.text = element.text[(int(offset) + int(math.floor(int(iteration / 10)))):]
        list_element.append(element)

        if not in_list_run:
            if not to_append is None:
                if not to_append.text is None:
                    to_append.tag = 'note'
                    to_append.attrib['id'] = 'fn_from_list{0}'.format(iteration + 1)
                    to_append.text = to_append.text[(int(offset) + int(math.floor(int(iteration / 10)))):]
                    self.debug.print_debug(self, u'Appending fn element: {0}'.format(to_append.text))
                    list_element.append(to_append)

        return iteration, list_element

    def process_enclosed_ref_list(self, tree, manipulate, treestring):

        if not u'>[' in treestring:
            return

        # find it we have a list of enclosed references
        # todo work with hi tags
        expression = u'//tei:div[last()]//tei:p[starts-with(.,"[")][following-sibling::tei:p[starts-with(.,"[")]]'

        elements = tree.xpath(expression, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        in_list_run = False
        list_element = None
        to_append = None
        iteration = 0
        offset = 0
        process = True
        last_element = None
        acted = False

        # ascertain if there are other document references. If so, this is probably a footnote
        footnote_test = '//text()[contains(self::text(), "[1]")]'
        footnotes = tree.xpath(footnote_test, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        is_footnote = len(footnotes) > 1

        # append an attribute to the preceding element to signal a return point for references if they were wrongly
        # classified

        if not is_footnote and len(elements) > 0:
            prev = elements[0].getprevious()
            print prev

            if prev is not None:
                prev.attrib['rend'] = 'ref-list-before'
            else:
                prev = elements[0].getparent()
                if prev is not None:
                    prev.attrib['rend'] = 'ref-list-parent'

        for element in elements:
            if iteration == 0:
                if not elements[0].text.startswith(u'[1] '):
                    self.debug.print_debug(self, u'Reference list PANIC: {0}'.format(element.text))
                    break
                else:
                    offset = 4

            if is_footnote:
                self.debug.print_debug(self, u'Found in-text footnotes: processing')
                iteration, list_element = self.handle_footnote_item(element, elements,
                                                                    in_list_run, iteration, list_element, offset,
                                                                    to_append)
            else:
                acted = True

                iteration = self.handle_reference_item(element, elements, in_list_run, iteration, list_element, offset,
                                                       to_append)
        if acted:
            manipulate.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')

        if is_footnote:
            back = manipulate.find_or_create_element(tree, 'back', '//tei:body', True)

            back.append(list_element)

            new_element_list = list_element

            for count in range(1, iteration + 2):

                footnote_test = '//tei:p//text()[contains(self::text(), "[{0}]")]'.format(count)
                footnote = tree.xpath(footnote_test, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

                note = copy(new_element_list[count - 1])

                split = footnote.split("[{0}]".format(count))
                footnote.getparent().text = split[0]
                footnote.getparent().append(note)
                note.tail = split[1]

            back.remove(list_element)

        tree.write(self.gv.tei_file_path)

    def process_dash_list(self, tree, manipulate, treestring):

        if not u'>-' in treestring:
            return

        # select all p elements followed by another p element
        expression = u'//tei:p[starts-with(.,"- ")][following-sibling::tei:p[starts-with(.,"- ")]]'

        elements = tree.xpath(expression, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        in_list_run = False
        list_element = None
        to_append = None

        for element in elements:
            self.debug.print_debug(self, u'Handling list element {0}'.format(element.text))

            if not in_list_run:
                list_element = etree.Element('list')
                to_append = None
                in_list_run = True
                element.addprevious(list_element)

            if not element.getnext().text is None:
                if element.getnext().text.startswith(u'- ') and not element.getnext() in elements:
                    # this element is the last in this list
                    in_list_run = False
                    to_append = element.getnext()
                elif not element.getnext().text.startswith(u'- ') and not element.getnext() in elements:
                    in_list_run = False
                    to_append = None
            else:
                # this element is the last in this list
                self.debug.print_debug(self, u'Ending list run on {0}'.format(element.getnext()))
                in_list_run = False
                to_append = element.getnext()

            element.tag = 'item'
            element.text = element.text[2:]
            list_element.append(element)

            if not in_list_run:
                if not to_append is None:
                    if not to_append.text is None:
                        to_append.tag = 'item'
                        to_append.text = to_append.text[2:]
                        self.debug.print_debug(self, u'Appending final list element: {0}'.format(to_append.text))
                        list_element.append(to_append)

        tree.write(self.gv.tei_file_path)

    def process_superscript_footnotes(self, tree, manipulate):
        self.debug.print_debug(self, 'Scanning for superscripted footnote entries')

        superscripts = reversed(tree.xpath('//*[@rend="superscript"]'))

        footnote_list = []
        footnote_text = []

        for item in superscripts:
            text = manipulate.get_stripped_text(item).strip()
            if self.gv.is_number(text):
                footnote_list.append(item)
                footnote_text.append(text)

        if len(footnote_list) == 0:
            self.debug.print_debug(self, 'Found no superscripted footnote entries')
            return

        # if it doesn't work, this is an expensive operation
        # however, once we've found all we can stop, so it's worth doing

        whole_document = reversed(tree.xpath('//tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))

        current = 0
        current_value = footnote_text[current]

        found = []

        for item in whole_document:
            text = manipulate.get_stripped_text(item).strip()

            if text.startswith(current_value):
                found.append(item)

                current += 1

                if current > len(footnote_text) - 1:
                    break

                current_value = footnote_text[current]

        # note: all lists are reversed by this point (ie go from the back of the document upwards)

        if len(found) == len(footnote_list):
            self.debug.print_debug(self, 'Found superscripted footnote entries')

            current = 0
            for footnote in footnote_list:
                # null the text (this will be generated automatically)
                footnote.text = ''

                footnote.tag = 'note'
                footnote.attrib['id'] = 'fn_from_list{0}'.format(current)

                footnote.append(found[current])

                replace_regex = '^({0}[\.\s\)]*)'.format(len(found) - current)

                if found[current].text and not found[current].text.startswith(str(len(found) - current)):
                    # in this case the footnote text is inside a sub-element
                    for sub_element in found:
                        if sub_element.text and sub_element.text.startswith(str(len(found) - current)):
                            sub_element.text = re.sub(replace_regex, '', sub_element.text)
                            break
                    pass
                elif found[current].text:
                    found[current].text = re.sub(replace_regex, '', found[current].text)

                current += 1
        else:
            self.debug.print_debug(self, 'Found {0} superscripted footnote entries but could not correlate this with'
                                         ' {1} paragraph entries'.format(len(footnote_list), len(found)))

        tree.write(self.gv.tei_file_path)

    def process_curly_list(self, tree, manipulate, treestring):

        if not u'>(' in treestring:
            return

        # select all p elements followed by another p element
        expression = u'//tei:p[starts-with(.,"(")][following-sibling::tei:p[starts-with(.,"(")]]'

        elements = tree.xpath(expression, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        in_list_run = False
        list_element = None
        to_append = None
        iteration = 0

        for element in elements:
            self.debug.print_debug(self, u'Handling list element {0}'.format(element.text))

            if iteration == 0:
                if not elements[0].text.startswith(u'(1) '):
                    self.debug.print_debug(self, u'Reference list PANIC: {0}'.format(element.text))
                    break
                else:
                    offset = 4

            iteration += 1

            if not in_list_run:
                list_element = etree.Element('list')
                list_element.attrib[u'type'] = u'ordered'
                to_append = None
                in_list_run = True
                element.addprevious(list_element)

            if not element.getnext().text is None:
                if element.getnext().text.startswith(u'(') and not element.getnext() in elements:
                    # this element is the last in this list
                    in_list_run = False
                    to_append = element.getnext()
                elif not element.getnext().text.startswith(u'(') and not element.getnext() in elements:
                    in_list_run = False
                    to_append = None
            else:
                # this element is the last in this list
                self.debug.print_debug(self, u'Ending list run on {0}'.format(element.getnext()))
                in_list_run = False
                to_append = element.getnext()

            element.tag = 'item'
            element.text = element.text[(int(offset) + int(math.floor(int(iteration/10)))):]
            list_element.append(element)

            if not in_list_run:
                if not to_append is None:
                    if not to_append.text is None:
                        to_append.tag = 'item'
                        to_append.text = to_append.text[(int(offset) + int(math.floor(int(iteration/10)))):]
                        self.debug.print_debug(self, u'Appending final list element: {0}'.format(to_append.text))
                        list_element.append(to_append)

        tree.write(self.gv.tei_file_path)

    def run(self):
        if int(self.gv.settings.args['--aggression']) < 4:
            self.debug.print_debug(self, 'Aggression level less than 4: exiting module.')
            return

        # load the DOM
        tree = self.set_dom_tree(self.gv.tei_file_path)

        manipulate = TeiManipulate(self.gv)

        string_version = etree.tostring(tree)

        # look for dash separated list
        # - Item 1
        # - Item 2
        self.process_dash_list(tree, manipulate, string_version)

        # look for curly bracket separated list
        # (1) Item 1
        # (2) Item 2
        self.process_curly_list(tree, manipulate, string_version)

        if int(self.gv.settings.args['--aggression']) >= 10:
            backup_tree = copy(tree)
            try:
                # look for footnote list [1], [2] etc.
                self.process_enclosed_ref_list(tree, manipulate, string_version)
            except:
                self.debug.print_debug(self, 'Error processing footnote or reference list. Reverting to backup tree')
                tree = backup_tree
                tree.write(self.gv.tei_file_path)

        self.process_superscript_footnotes(tree, manipulate)