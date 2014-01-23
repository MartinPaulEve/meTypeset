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


class ListClassifier(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'List Classifier')

    @staticmethod
    def set_dom_tree(filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

        return etree.parse(filename, p)

    def process_dash_list(self, tree, manipulate):
        # select all p elements followed by another p element
        expression = u'//tei:p[starts-with(.,"- ")][following-sibling::tei:p[starts-with(.,"- ")]]'

        elements = tree.xpath(expression, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        iteration = 0
        in_list_run = False
        list_element = None
        to_append = None

        for element in elements:
            self.debug.print_debug(self, u'Handling list element {0}'.format(element.text))

            if not in_list_run:
                list_element = etree.Element('list')
                element.addnext(list_element)
                to_append = None
                in_list_run = True

            if not element.getnext().text is None:
                if element.getnext().text.startswith(u'- ') and not element.getnext() in elements:
                    # this element is the last in this list
                    in_list_run = False
                    to_append = element.getnext()

            element.tag = 'item'
            element.text = element.text[2:]
            list_element.append(element)

            if not in_list_run:
                to_append.tag = 'item'
                to_append.text = to_append.text[2:]
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

