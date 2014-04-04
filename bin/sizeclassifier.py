#!/usr/bin/env python
from teimanipulate import *

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that scans for meTypeset size fields in a TEI file.

1.) Identifies a list of sizes
2.) Ascertains the density and likelihood of the size being a heading
3.) Returns a manipulator ready to implement all the changes to the TEI file
"""

from debug import Debuggable


class SizeClassifier(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        self.size_cutoff = int(self.gv.settings.get_setting('minimum-heading-size', self))
        self.max_headings = 40
        self.root = 0
        self.tree = None
        Debuggable.__init__(self, 'Size Classifier')

    @staticmethod
    def get_values(tree, search_attribute):
        # this function searches the DOM tree for TEI "hi" elements with the specified search_attribute
        sizes = {}
        for child in tree.xpath('//tei:hi[@' + search_attribute + '=not("")]',
                                namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if child.get(search_attribute) in sizes:
                sizes[child.get(search_attribute)] += 1
            else:
                sizes[child.get(search_attribute)] = 1

        return sizes

    @staticmethod
    def get_sizes_ordered(tree):
        # this function searches the DOM tree for TEI "head" elements with the specified search_attribute
        sizes_ordered = []

        for child in tree.xpath("//tei:head[@meTypesetSize=not('')]",
                                namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            sizes_ordered.append(child.get("meTypesetSize"))

        return sizes_ordered

    def set_dom_tree(self, filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
        self.tree = etree.parse(filename, p)

        return self.tree

    @staticmethod
    def handle_bold_only_paragraph(manipulate, root_size):
        """
        This method looks for paragraphs that contain only bold text. It then transforms them to titles.
        @param manipulate: a TeiManipulator object
        @param root_size: the size styling to apply to these elements
        """
        expression = u'//tei:p[(contains(@rend, "bold") or count(tei:hi) = count(tei:hi[contains(@rend, "bold")])) ' \
                     u'and not(text()[normalize-space()!=""])]/tei:hi'

        manipulate.change_self_size(expression, str(root_size))

    @staticmethod
    def handle_heading(manipulate, attribute, root_size):
        """
        This method looks for paragraphs that contain the specified attribute in their rend tag.
        It then transforms them to titles.
        @param manipulate: a TeiManipulator object
        @param attribute: a string to search for in the rend attribute
        @param root_size: the size styling to apply to these elements
        """
        expression = u'//tei:p[contains(@rend, "{0}")]'.format(attribute)

        manipulate.enclose_and_change_self_size(expression, str(root_size), 'p', 'hi')

    def get_sizes(self, tree):
        sizes = self.get_values(tree, "meTypesetSize")

        if len(sizes) > 0:
            self.debug.print_debug(self,
                                   u'Explicitly specified size variations and their frequency of '
                                   u'occurrence: {0}'.format(str(sizes)))
        new_sizes = {}
        for size, frequency in sizes.iteritems():
            if float(frequency) < float(self.max_headings):
                new_sizes[size] = frequency
        sizes = new_sizes
        return sizes

    def correlate_styled_headings(self, manipulate):
        # reload the DOM
        tree = self.set_dom_tree(self.gv.tei_file_path)
        # get a numerical list of explicit size values inside meTypesetSize attributes
        sizes = self.get_sizes(tree)
        sorted_list = []
        headings = {}

        # correlate tag sizes specified by true word headings ("heading 1", "heading 2" etc.) to our index
        for size, frequency in sizes.iteritems():
            if float(frequency) < float(self.max_headings) and float(size) > float(self.size_cutoff):
                sorted_list.append(size)

        sorted_list = sorted(sorted_list)

        if len(sorted_list) > 0:
            for count in range(0, len(sorted_list) - 1):
                key = u'heading {0}'.format(count + 1)
                headings[key] = sorted_list[count]

                key = u'Heading {0}'.format(count + 1)
                headings[key] = sorted_list[count]

            for count in range(len(sorted_list) - 1, 8):
                key = u'heading {0}'.format(count + 1)
                headings[key] = 100 - 10 * count

                key = u'Heading {0}'.format(count + 1)
                headings[key] = 100 - 10 * count
        else:
            headings = {'title': 100, 'heading 1': 100, 'heading 2': 90, 'heading 3': 80, 'heading 4': 70,
                        'heading 5': 60, 'heading 6': 50, 'heading 7': 40, 'heading 8': 30, 'heading 9': 20}

            headings = dict(headings.items() + {'Title': 100, 'Heading 1': 100, 'Heading 2': 90, 'Heading 3': 80,
                                                'Heading 4': 70, 'Heading 5': 60, 'Heading 6': 50, 'Heading 7': 40,
                                                'Heading 8': 30, 'Heading 9': 20}.items())

            headings = dict(headings.items() + {'H1': 100, 'H2': 90, 'H3': 80, 'H4': 70, 'H5': 60, 'H6': 50, 'H7': 40,
                                                'H8': 30, 'H9': 20}.items())

        for key, value in headings.iteritems():
            self.debug.print_debug(self, u'Changing {0} to size {1}'.format(key, value))
            self.handle_heading(manipulate, key, float(value))

        # reload the DOM
        tree = self.set_dom_tree(self.gv.tei_file_path)
        return tree



    def run(self):
        if int(self.gv.settings.args['--aggression']) < int(self.gv.settings.get_setting('sizeclassifier', self,
                                                                                         domain='aggression')):
            self.debug.print_debug(self, u'Aggression level too low: exiting module.')
            return

        manipulate = TeiManipulate(self.gv)

        # transform bolded paragraphs into size-attributes with an extremely high threshold (so will be thought of as
        # root nodes)
        self.handle_bold_only_paragraph(manipulate, self.size_cutoff)

        tree = self.correlate_styled_headings(manipulate)

        # refresh the size list
        sizes = self.get_sizes(tree)

        handled = False

        for size in sizes:

                if float(size) >= float(self.size_cutoff):
                    # if the size is greater than or equal to 16, treat it as a heading
                    self.debug.print_debug(self,
                                           u'Size ({0}) greater '
                                           u'than or equal to {1}. '
                                           u'Treating as a heading.'.format(str(size),
                                                                            str(self.size_cutoff)))

                    # instruct the manipulator to change the parent tag of every tag it finds containing
                    # a "hi" tag with meTypesetSize set to the value found to "title"
                    # so, for example <p><hi meTypesetSize="18">some text</hi></p>
                    # will be transformed to
                    # <title><hi meTypesetSize="18">some text</hi></title>
                    manipulate.change_outer('//tei:hi[@meTypesetSize=\'{0}\']'.format(size), 'head', size)

                    tree = self.set_dom_tree(self.gv.tei_file_path)

                    for normalize in tree.xpath('//tei:cit/tei:quote/tei:head',
                                                namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
                        normalize.getparent().tag = 'REMOVE'
                        normalize.getparent().getparent().tag = 'REMOVE'

                    etree.strip_tags(tree, 'REMOVE')
                    manipulate.save_tree(tree)
                    self.debug.print_debug(self, u'Normalizing nested headings inside cit/quote blocks')


                    # assign IDs to every single heading tag for easy manipulation
                    heading_count = manipulate.tag_headings()

                    manipulate.save_tree(tree)
