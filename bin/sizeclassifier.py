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
        expression = u'//tei:p[count(tei:hi) = count(tei:hi[contains(@rend, "bold")]) ' \
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

    def handle_misstacked(self, next_size, section_ids, section_stack):

        if float(next_size) > float(self.size_cutoff):
            # normalize the size
            next_size = self.size_cutoff

        sibling_size = 0
        for x in section_stack:
            if x > next_size:
                sibling_size = x
        self.debug.print_debug(self, u'Mis-stacked element ordering, using {0} as sibling size'.format(sibling_size))
        sibling_id = section_ids[section_stack.index(sibling_size)]
        return sibling_id

    def enclose_larger_heading(self, iteration, manipulate, next_size, section_ids, section_stack, size, next_id):
        self.debug.print_debug(self,
                               u'Encountered larger block as following (size: {0}, next size: {1}) '
                               u'[size ID: #{2}]'.format(str(size), str(next_size), str(iteration)))

        # find appropriate previous sibling
        if next_size in section_stack:
            sibling_id = section_ids[section_stack.index(next_size)]
        else:
            sibling_id = self.handle_misstacked(next_size, section_ids, section_stack)


        # enclose the REST OF THE DOCUMENT underneath this /next heading/
        manipulate.enclose(u"//tei:head[@meTypesetHeadingID=\'{0}\']".format(str(iteration + 1)),
                           u"//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:head["
                           u"@meTypesetHeadingID=\'{1}\']]".format(
                               str(next_id), str(next_id)))

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

    def enclose_last_heading(self, iteration, manipulate, section_ids, section_stack, size):
        self.debug.print_debug(self,
                               u'Encountered final heading (size: {0}) [size ID: #{1}]'.format(str(size),
                                                                                               str(iteration)))

        # find appropriate previous sibling
        if size in section_stack and float(size) != float(self.size_cutoff):
            sibling_id = section_ids[(len(section_stack) - 1) - section_stack[::-1].index(size)]
        else:
            # here, we need to figure out if the current size is bigger than anything else
            sibling_size = -1
            for x in section_stack:
                if float(x) < float(size):
                    sibling_size = x

            if sibling_size != -1:
                # this element should be treated as root
                sibling_id = section_ids[0]
                self.debug.print_debug(self, u'Treating final element as on par with root')
            else:
                # figure out if the current size is smaller than anything else
                for x in section_stack:
                    if float(x) > float(size):
                        sibling_size = x

                if float(sibling_size) == float(section_stack[len(section_stack) - 1]):
                    # this element is smaller than all others
                    sibling_id = -1
                    self.debug.print_debug(self, u'Treating final element as smaller than all others')
                else:
                    # use the sibling at the nearest depth
                    if float(size) == float(self.root) or float(size) == float(self.size_cutoff):
                        self.debug.print_debug(self, u'Selecting root element as sibling')
                        sibling_id = 0
                    else:
                        for index in section_stack[::-1]:
                            if float(size) == float(index):
                                sibling_id = section_ids[index]

                        if not sibling_id:
                            self.debug.print_debug(self, u'Selecting root element as sibling as none found')
                            sibling_id = section_ids[0]

                    self.debug.print_debug(self, u'Treating final element as on par with sibling')

        # enclose the REST OF THE DOCUMENT underneath this /next heading/
        manipulate.enclose(u"//tei:head[@meTypesetHeadingID=\'{0}\']".format(str(iteration)),
                           u"//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:head["
                           u"@meTypesetHeadingID=\'{1}\']]".format(
                               str(iteration), str(iteration)))

        if sibling_id != -1:
        # move this heading to directly beneath the previous sibling
            manipulate.move_size_div(iteration, sibling_id)

        self.debug.print_debug(self,u'Moving block ID #{0} to be sibling of block ID #{1}'.format(str(iteration),
                                                                                                  str(sibling_id)))

    def enclose_smaller_heading(self, iteration, manipulate, next_size, size):
        self.debug.print_debug(self,
                               u'Encountered smaller block as following (size: {0}, next size: {1}) [size ID: #{2}]'
                               .format(str(size), str(next_size), str(iteration)))

        manipulate.enclose(u"//tei:head[@meTypesetHeadingID=\'{0}\']".format(str(iteration)),
                           u"//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:head["
                           u"@meTypesetHeadingID=\'{1}\']]".format(
                               str(iteration), str(iteration)))

    def enclose_same_size_heading(self, iteration, manipulate, size, next_id):
        self.debug.print_debug(self,
                               u'Encountered block of same size as following (size: {0}) [size ID: {1}]'.format(
                                   str(size), str(iteration)))
        manipulate.enclose(u"//tei:head[@meTypesetHeadingID=\'{0}\']".format(str(iteration)),
                           u"//tei:head[@meTypesetHeadingID=\'{0}\'] | //*[preceding-sibling::tei:"
                           u"head[@meTypesetHeadingID=\'{1}\'] and following-sibling::tei:head["
                           u"@meTypesetHeadingID=\'{2}\']]".format(
                               str(iteration), str(iteration), str(next_id)))

    def get_next_size(self, iteration, sizes_ordered):
        next_size = sizes_ordered[iteration + 1]
        plusint = 1
        while float(next_size) < float(self.size_cutoff):
            next_size = sizes_ordered[iteration + plusint + 1]
            plusint += 1

        return next_size, iteration + plusint

    def process_subsequent_headings(self, iteration, manipulate, processed_flag, section_ids, section_stack, size,
                                    sizes_ordered):
        if not processed_flag:
            last = True

            # determine if is last
            for index in range(iteration + 1, len(sizes_ordered) - 1):
                if float(sizes_ordered[index]) >= float(self.size_cutoff):
                    last = False

            # ascertain the next size
            if not last:
                next_size, next_id = self.get_next_size(iteration, sizes_ordered)

                if float(size) == float(next_size):
                    self.enclose_same_size_heading(iteration, manipulate, size, next_id)

                if float(size) > float(next_size):
                    self.enclose_smaller_heading(iteration, manipulate, next_size, size)

                elif float(size) < float(next_size):
                    self.enclose_larger_heading(iteration, manipulate, next_size, section_ids, section_stack,
                                                size, next_id)

                    self.debug.print_debug(self, u'Previous section stack: {0}'.format(section_stack))

                    # create a slice of the stack so that we can modify the original while iterating
                    temp_stack = section_stack[:]
                    pointer = len(section_stack)

                    # pop the stack until the current level
                    while temp_stack[pointer - 1] > size and (pointer - 1) != 0:
                        section_stack.pop()
                        section_ids.pop()
                        pointer -= 1

                    self.debug.print_debug(self, u'New section stack: {0}'.format(section_stack))

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
        for size in sizes:
            manipulate.change_outer("//tei:hi[@meTypesetSize='" + size + "']", "head", size)

        tree = self.set_dom_tree(self.gv.tei_file_path)
        sizes_ordered = self.get_sizes_ordered(tree)
        section_count = {}
        iteration = 0
        section_stack = []
        section_ids = []
        processed_flag = False

        root_size = sizes_ordered[0]
        self.root = root_size

        # handle occasions when root_size is lower than size_cutoff
        if float(root_size) < float(self.size_cutoff):
            manipulate.resize_headings(root_size, str(self.size_cutoff))

            sizes = [self.size_cutoff if x == root_size else x for x in sizes]
            sizes_ordered = [self.size_cutoff if x == root_size else x for x in sizes_ordered]

            root_size = str(self.size_cutoff)

        # assign IDs to every single heading tag for easy manipulation
        manipulate.tag_headings()

        # normalize sizes: we cannot have a size bigger than the root node; there's no sensible way to detect this
        for size in sizes:
            if float(size) >= float(self.size_cutoff):
                if float(size) > float(root_size):
                    self.debug.print_debug(self,
                                           u'Downsizing headings of {0} '
                                           u'to maximum root size {1}'.format(str(size),
                                                                              str(root_size)))
                    manipulate.resize_headings(size, root_size)
                    sizes_ordered = [root_size if x == size else x for x in sizes_ordered]

        if len(set(sizes_ordered)) == 1:
            self.debug.print_debug(self, u'After normalization, found a single heading size. Treating as such')
            self.handle_single_size(manipulate, sizes)
            self.debug.print_debug(self, u'Shutting down module')
            return

        for size in sizes_ordered:
            if float(size) >= float(self.size_cutoff):
                if not size in section_count:
                    section_count[size] = 0

                if len(section_stack) == 0:
                    # this section should span the entire document and enclose the first title
                    # manipulate.enclose("//tei:head[@meTypesetSize='" + size + "']",
                    # section_count[size], "(//*)[last()]")

                    # done automatically?
                    pass
                else:
                    # this block is triggered when we reach any heading but the first
                    processed_flag = self.process_subsequent_headings(iteration, manipulate, processed_flag,
                                                                      section_ids, section_stack, size, sizes_ordered)

                section_count[size] += 1

                if not processed_flag:
                    if not size in section_stack:
                        if not type(size) is str:
                            size = str(size)
                        section_stack.append(size)
                        section_ids.append(iteration)
                    else:
                        section_ids[section_stack.index(size)] = iteration

                iteration += 1

            else:
                self.debug.print_debug(self, u'Ignoring heading {0} because its size ({1}) '
                                             u'is less than {2}'.format(iteration, size, self.size_cutoff))

                # fix for regression at b55b890f202557a8ceee917cc3ddced932bf2bb7 handled by size normalization in
                # mismatched size handler
                iteration += 1

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

            for count in range(len(sorted_list) - 1, 8):
                key = u'heading {0}'.format(count + 1)
                headings[key] = 100 - 10 * count
        else:
            headings = {'heading 1': 100, 'heading 2': 90, 'heading 3': 80, 'heading 4': 70, 'heading 5': 60,
                        'heading 6': 50, 'heading 7': 40, 'heading 8': 30, 'heading 9': 20}

            headings = dict(headings.items() + {'Heading 1': 100, 'Heading 2': 90, 'Heading 3': 80, 'Heading 4': 70,
                                              'Heading 5': 60, 'Heading 6': 50, 'Heading 7': 40, 'Heading 8': 30,
                                              'Heading 9': 20}.items())

        for key, value in headings.iteritems():
            self.debug.print_debug(self, u'Changing {0} to size {1}'.format(key, value))
            self.handle_heading(manipulate, key, float(value))

        # reload the DOM
        tree = self.set_dom_tree(self.gv.tei_file_path)
        return tree

    def handle_single_size(self, manipulate, sizes):
        handled = False

        for size in sizes:
            if not handled:
                handled = True

                if float(size) >= float(self.size_cutoff):
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

                    # assign IDs to every single heading tag for easy manipulation
                    heading_count = manipulate.tag_headings()

                    if heading_count > 1:
                        for heading_id in range(0, heading_count):
                            self.debug.print_debug(self, u'Handling heading ID {0}'.format(heading_id))
                            if heading_id < heading_count - 1:
                                expression = u'//tei:head[@meTypesetHeadingID="{1}"] | ' \
                                             u'//*[following-sibling::tei:head[@meTypesetHeadingID="{0}"] and ' \
                                             u'preceding-sibling::tei:head[' \
                                             u'@meTypesetHeadingID="{1}"]]'.format(heading_id + 1,
                                                                                   heading_id)
                                # enclose all of these entries within section tags
                                manipulate.enclose_all(expression, 'div', 1)
                            else:
                                # enclose to the end of the document
                                expression = u'//tei:head[@meTypesetHeadingID="{0}"] | ' \
                                             u'//*[preceding-sibling::tei:head[' \
                                             u'@meTypesetHeadingID="{0}"]]'.format(heading_id)
                                manipulate.enclose_all(expression, 'div', 1)
                    else:
                    # enclose to the end of the document
                        expression = u'//tei:head[@meTypesetHeadingID="{0}"] | ' \
                                     u'//*[preceding-sibling::tei:head[' \
                                     u'@meTypesetHeadingID="{0}"]]'.format(u"1")
                        manipulate.enclose_all(expression, 'div', 1)

    def run(self):
        if int(self.gv.settings.args['--aggression']) < int(self.gv.settings.get_setting('sizeclassifier', self,
                                                                                         domain='aggression')):
            self.debug.print_debug(self, u'Aggression level less than 5: exiting module.')
            return

        manipulate = TeiManipulate(self.gv)

        # transform bolded paragraphs into size-attributes with an extremely high threshold (so will be thought of as
        # root nodes)
        self.handle_bold_only_paragraph(manipulate, self.size_cutoff)

        tree = self.correlate_styled_headings(manipulate)

        # refresh the size list
        sizes = self.get_sizes(tree)

        if len(sizes) == 1:
            self.handle_single_size(manipulate, sizes)

        elif len(sizes) > 1:
            self.create_sections(manipulate, sizes)
