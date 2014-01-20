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
        self.size_cutoff = 16
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

    @staticmethod
    def set_dom_tree(filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

        return etree.parse(filename, p)

    @staticmethod
    def handle_bold_only_paragraph(manipulate, root_size):
        """
        This method looks for paragraphs that contain only bold text. It then transforms them to titles.
        @param manipulate: a TeiManipulator object
        @param root_size: the size styling to apply to these elements
        """
        expression = u'////tei:p[* and not(text()) and not(*[not(self::tei:hi[@rend="bold"])])]/tei:hi'

        manipulate.change_self_size(expression, str(root_size))

    def enclose_larger_heading(self, iteration, manipulate, next_size, section_ids, section_stack, size):
        self.debug.print_debug(self,
                               u'Encountered larger block as following (size: {0}, next size: {1}) '
                               u'[size ID: #{2}]'.format(str(size), str(next_size), str(iteration)))

        # find appropriate previous sibling
        if next_size in section_stack:
            sibling_id = section_ids[section_stack.index(next_size)]
        else:
            sibling_id = -1

        # enclose the REST OF THE DOCUMENT underneath this /next heading/
        manipulate.enclose(u"//tei:head[@meTypesetHeadingID=\'{0}\']".format(str(iteration + 1)),
                           u"//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:head["
                           u"@meTypesetHeadingID=\'{1}\']]".format(
                               str(iteration + 1), str(iteration + 1)))

        if sibling_id != -1:
            # move the /next heading/ to directly beneath the previous sibling
            self.debug.print_debug(self,
                       u'Moving block ID #{0} to be sibling of block ID #{1}'.format(str(iteration + 1),
                                                                                     str(sibling_id)))

            manipulate.move_size_div(iteration + 1, sibling_id)

        # update the sibling stack
        if next_size in section_stack:
            if section_stack.index(next_size) in section_ids:
                section_ids[section_stack.index(next_size)] = iteration + 1

        # now handle the enclosure of the current block
        manipulate.enclose('//tei:head[@meTypesetHeadingID="' + str(iteration) + '"]',
                           u'//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:head['
                           u'@meTypesetHeadingID=\'{1}\']]'.format(
                               str(iteration), str(iteration)))

        # if we have an erroneous size (-1) then handle here
        if sibling_id == -1:
            self.debug.print_debug(self,
                       u'Moving block ID #{0} to be sibling of block ID #{1}'.format(str(iteration + 1),
                                                                                     str(iteration)))

            manipulate.move_size_div(iteration + 1, iteration)


    def enclose_last_heading(self, iteration, manipulate, section_ids, section_stack, size):
        self.debug.print_debug(self,
                               u'Encountered final heading (size: {0}) [size ID: #{1}]'.format(str(size),
                                                                                               str(iteration)))
        # find appropriate previous sibling
        if size in section_stack:
            sibling_id = section_ids[section_stack.index(size)]
        else:
            sibling_id = -1

        # enclose the REST OF THE DOCUMENT underneath this /next heading/
        manipulate.enclose(u"//tei:head[@meTypesetHeadingID=\'{0}\']".format(str(iteration)),
                           u"//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:head["
                           u"@meTypesetHeadingID=\'{1}\']]".format(
                               str(iteration), str(iteration)))

        self.debug.print_debug(self,u'Moving block ID #{0} to be sibling of block ID #{1}'.format(
            str(iteration),str(sibling_id)))

        if sibling_id != -1:
        # move this heading to directly beneath the previous sibling
            manipulate.move_size_div(iteration, sibling_id)

    def enclose_smaller_heading(self, iteration, manipulate, next_size, size):
        self.debug.print_debug(self,
                               u'Encountered smaller block as following (size: {0}, next size: {1}) [size ID: #{2}]'
                               .format(str(size), str(next_size), str(iteration)))

        manipulate.enclose(u"//tei:head[@meTypesetHeadingID=\'{0}\']".format(str(iteration)),
                           u"//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:head["
                           u"@meTypesetHeadingID=\'{1}\']]".format(
                               str(iteration), str(iteration)))

    def enclose_same_size_heading(self, iteration, manipulate, size):
        self.debug.print_debug(self,
                               u'Encountered block of same size as following (size: {0}) [size ID: {1}]'.format(
                                   str(size), str(iteration)))
        manipulate.enclose(u"//tei:head[@meTypesetHeadingID=\'{0}\']".format(str(iteration)),
                           u"//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:"
                           u"head[@meTypesetHeadingID=\'{1}\'] and following-sibling::tei:head["
                           u"@meTypesetHeadingID=\'{2}\']]".format(
                               str(iteration), str(iteration), str(iteration + 1)))

    def process_subsequent_headings(self, iteration, manipulate, processed_flag, section_ids, section_stack, size,
                                    sizes_ordered):
        if not processed_flag:

            # ascertain the next size
            if iteration < (len(sizes_ordered) - 1):
                next_size = sizes_ordered[iteration + 1]

                if size == next_size:
                    self.enclose_same_size_heading(iteration, manipulate, size)

                if size > next_size:
                    self.enclose_smaller_heading(iteration, manipulate, next_size, size)

                elif size < next_size:
                    self.enclose_larger_heading(iteration, manipulate, next_size, section_ids, section_stack,
                                                size)

                    # create a slice of the stack so that we can modify the original while iterating
                    temp_stack = section_stack[:]
                    pointer = len(section_stack)

                    # pop the stack until the current level
                    while temp_stack[pointer - 1] > size and (pointer - 1) != 0:
                        section_stack.pop()
                        section_ids.pop()
                        pointer -= 1

                    # set the processed flag so that the next enclosure isn't handled
                    processed_flag = True
            else:
            # this is the last heading so there is no future comparator
                self.enclose_last_heading(iteration, manipulate, section_ids, section_stack, size)

        else:
            self.debug.print_debug(self, u'Size ID: {0} was already processed'.format(str(iteration)))
            processed_flag = False
        return processed_flag

    def create_sections(self, manipulate, sizes):
        # first, we want a sorted representation (of tuples) of the frequency dictionary
        iteration = 0
        for size in sizes:
            # disregard sizes below the cut-off
            if size >= self.size_cutoff:
                manipulate.change_outer("//tei:hi[@meTypesetSize='" + size + "']", "head", size)
                iteration += 1

        tree = self.set_dom_tree(self.gv.tei_file_path)
        sizes_ordered = self.get_sizes_ordered(tree)
        section_count = {}
        iteration = 0
        section_stack = []
        section_ids = []
        processed_flag = False

        root_size = sizes_ordered[0]

        # assign IDs to every single heading tag for easy manipulation
        manipulate.tag_headings()
        # normalize sizes: we cannot have a size bigger than the root node; there's no sensible way to detect this
        for size in sizes:
            if int(size) > int(root_size):
                self.debug.print_debug(self,
                                       u'Downsizing headings of {0} to maximum root size {1}'.format(str(size),
                                                                                                     str(root_size)))
                manipulate.downsize_headings(root_size, size)
                sizes_ordered = [root_size if x == size else x for x in sizes_ordered]

        for size in sizes_ordered:
            if not size in section_count:
                section_count[size] = 0

            if len(section_stack) == 0:
                # this section should span the entire document and enclose the first title
                # manipulate.enclose("//tei:head[@meTypesetSize='" + size + "']", section_count[size], "(//*)[last()]")

                # done automatically?
                pass
            else:
                # this block is triggered when we reach any heading but the first
                processed_flag = self.process_subsequent_headings(iteration, manipulate, processed_flag, section_ids,
                                                                  section_stack, size, sizes_ordered)

            section_count[size] += 1

            if not processed_flag:
                if not size in section_stack:
                    section_stack.append(size)
                    section_ids.append(iteration)
                else:
                    section_ids[section_stack.index(size)] = iteration

            iteration += 1

    def run(self):
        # load the DOM
        tree = self.set_dom_tree(self.gv.tei_file_path)

        manipulate = TeiManipulate(self.gv)

        # transform bolded paragraphs into size-attributes with an extremely high threshold (so will be thought of as
        # root nodes)
        self.handle_bold_only_paragraph(manipulate, 100)

        # reload the DOM
        tree = self.set_dom_tree(self.gv.tei_file_path)

        # get a numerical list of explicit size values inside meTypesetSize attributes
        sizes = self.get_values(tree, "meTypesetSize")

        if len(sizes) > 0:
            self.debug.print_debug(self,
                                   u'Explicitly specified size variations and their frequency of '
                                   u'occurrence: {0}'.format(str(sizes)))

        if len(sizes) == 1:
            for size in sizes:
                # loop will only execute once
                if int(size) >= int(self.size_cutoff):
                    # if the size is greater than or equal to 16, treat it as a heading
                    self.debug.print_debug(self,
                                           u'Found single explicitly specified size ({0}) greater '
                                           u'than or equal to {1}. '
                                           u'Treating as a heading.'.format(str(size),
                                                                            str(self.size_cutoff)))

                    # instruct the manipulator to change the parent tag of every tag it finds containing
                    # a "hi" tag with meTypesetSize set to the value found to "title"
                    # so, for example <p><hi meTypesetSize="18">some text</hi></p>
                    # will be transformed to
                    # <title><hi meTypesetSize="18">some text</hi></title>
                    manipulate.change_outer('//tei:hi[@meTypesetSize=\'{0}\']'.format(size), 'head', size)

                    # enclose all of these entries within section tags
                    manipulate.enclose_all('//tei:hi[@meTypesetSize=\'{0}\']/..'.format(size), 'div', 1)

        elif len(sizes) > 1:
            self.create_sections(manipulate, sizes)
