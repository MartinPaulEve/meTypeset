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


class ListClassifier(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'List Classifier')

    @staticmethod
    def set_dom_tree(filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

        return etree.parse(filename, p)

    def process_enclosed_ref_list(self, tree, manipulate):
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

        for element in elements:
            # ascertain if there are other document references. If so, this is probably a footnote
            footnote_test = '//text()[contains(self::text(), "[1]")]'
            footnotes = tree.xpath(footnote_test, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            is_footnote = len(footnotes) > 1

            if is_footnote:
                # todo handle footnotes
                pass
            else:
                if iteration == 0:
                    if not elements[0].text.startswith(u'[1] '):
                        self.debug.print_debug(self, u'Reference list PANIC: {0}'.format(element.text))
                        break
                    else:
                        offset = 4

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
                element.text = element.text[(int(offset) + int(math.floor(int(iteration/10)))):]
                list_element.append(element)

                if not in_list_run:
                    if not to_append is None:
                        if not to_append.text is None:
                            to_append.tag = 'p'
                            to_append.attrib['rend'] = u'Bibliography'
                            to_append.text = to_append.text[(int(offset) + int(math.floor(int(iteration/10)))):]
                            self.debug.print_debug(self, u'Appending anomalous ref element: {0}'.format(to_append.text))
                            list_element.append(to_append)

        manipulate.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')

        tree.write(self.gv.tei_file_path)

    def process_dash_list(self, tree, manipulate):
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

    def process_curly_list(self, tree, manipulate):
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
        # load the DOM
        tree = self.set_dom_tree(self.gv.tei_file_path)

        manipulate = TeiManipulate(self.gv)

        # look for dash separated list
        # - Item 1
        # - Item 2
        self.process_dash_list(tree, manipulate)

        # look for curly bracket separated list
        # (1) Item 1
        # (2) Item 2
        self.process_curly_list(tree, manipulate)

        # look for reference list [1], [2] etc.
        self.process_enclosed_ref_list(tree, manipulate)

