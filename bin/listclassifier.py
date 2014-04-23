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
        self.skiplist = []
        Debuggable.__init__(self, 'List Classifier')

    @staticmethod
    def set_dom_tree(filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

        return etree.parse(filename, p)

    def handle_reference_item(self, element, elements, in_list_run, iteration, list_element, offset, to_append):
        if element in self.skiplist:
            return iteration

        manipulate = TeiManipulate(self.gv)
        iteration += 1
        # treat as ref list
        next_text = manipulate.get_stripped_text(element.getnext())
        self.debug.print_debug(self, u'Handling reference element {0}'.format(element.text))
        if not in_list_run:
            list_element = etree.Element('ref')
            list_element.attrib['target'] = 'None'
            to_append = None
            in_list_run = True
            element.addprevious(list_element)
        if not element.getnext() is None or next_text == '':
            if next_text.startswith(u'[') and not element.getnext() in elements:
                # this element is the last in this list
                in_list_run = False
                to_append = element.getnext()
            elif not next_text.startswith(u'['):

                while not next_text.startswith(u'['):
                    # anomalous ref
                    if next_text != '':
                        self.debug.print_debug(self, u'Ref missing marker {0}'.format(next_text))
                    self.skiplist.append(element.getnext())
                    element.getnext().tag = 'hi'
                    Manipulate.append_safe(element, element.getnext(), self)

                    next_text = manipulate.get_stripped_text(element.getnext())

        else:
            # this can happen with italics
            self.debug.print_debug(self, u'Ref run/anomaly on {0}'.format(next_text))
            for sub_element in element.getnext():
                Manipulate.append_safe(element, sub_element, self)
            in_list_run = False
            to_append = element.getnext()

        element.tag = 'p'
        element.attrib['rend'] = u'Bibliography'

        element.text = element.text[(int(offset) + int(math.floor(int(iteration / 10)))):]
        Manipulate.append_safe(list_element, element, self)

        if not in_list_run:
            if not to_append is None:
                if not to_append.text is None:
                    to_append.tag = 'p'
                    to_append.attrib['rend'] = u'Bibliography'
                    to_append.text = to_append.text[(int(offset) + int(math.floor(int(iteration / 10)))):]
                    self.debug.print_debug(self, u'Appending ref element: {0}'.format(to_append.text))
                    Manipulate.append_safe(list_element, to_append, self)
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
                Manipulate.append_safe(element, sub_element, self)
            in_list_run = False
            to_append = element.getnext()
        element.tag = 'note'
        element.attrib['id'] = 'fn_from_list{0}'.format(iteration)
        element.text = element.text[(int(offset) + int(math.floor(int(iteration / 10)))):]
        Manipulate.append_safe(list_element, element, self)

        if not in_list_run:
            if not to_append is None:
                if not to_append.text is None:
                    to_append.tag = 'note'
                    to_append.attrib['id'] = 'fn_from_list{0}'.format(iteration + 1)
                    to_append.text = to_append.text[(int(offset) + int(math.floor(int(iteration / 10)))):]
                    self.debug.print_debug(self, u'Appending fn element: {0}'.format(to_append.text))
                    Manipulate.append_safe(list_element, to_append, self)

        return iteration, list_element

    def process_enclosed_ref_list(self, tree, manipulate, treestring):

        if not u'>[' in treestring and not u'> [' in treestring:
            self.debug.print_debug(self, u'Leaving enclosed reference processing')
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

        if not is_footnote:
            footnote_test = '//text()[contains(self::text(), "[1,")]'
            footnotes = tree.xpath(footnote_test, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            is_footnote = len(footnotes) > 1

        # append an attribute to the preceding element to signal a return point for references if they were wrongly
        # classified

        if is_footnote:
            self.debug.print_debug(self, u'Enclosed footnotes detected')
        else:
            self.debug.print_debug(self, u'No enclosed footnotes detected')

        if not is_footnote and len(elements) > 0:
            prev = elements[0].getprevious()

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
            self.gv.used_square_reference_method = True
            manipulate.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')

            manipulate.save_tree(tree)

            self.debug.print_debug(self, u'Enclosing bibliography')

        if is_footnote:
            back = manipulate.find_or_create_element(tree, 'back', '//tei:body', True)

            Manipulate.append_safe(back, list_element, self)

            new_element_list = list_element

            for count in range(1, iteration + 2):

                footnote_test = '//tei:p//text()[contains(self::text(), "[{0}]")]'.format(count)
                footnote = tree.xpath(footnote_test, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

                note = copy(new_element_list[count - 1])

                split = footnote.split("[{0}]".format(count))
                footnote.getparent().text = split[0]
                manipulate.append_safe(footnote.getparent(), note, self)
                note.tail = split[1]

            back.remove(list_element)

        manipulate.save_tree(tree)

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
            Manipulate.append_safe(list_element, element, self)

            if not in_list_run:
                if not to_append is None:
                    if not to_append.text is None:
                        to_append.tag = 'item'
                        to_append.text = to_append.text[2:]
                        self.debug.print_debug(self, u'Appending final list element: {0}'.format(to_append.text))
                        Manipulate.append_safe(list_element, to_append, self)

        manipulate.save_tree(tree)

    def process_superscript_footnotes(self, tree, manipulate):

        self.debug.print_debug(self, u'Scanning for superscripted footnote entries')

        superscripts = reversed(tree.xpath('//*[@rend="superscript"]'))

        footnote_list = []
        footnote_text = []

        for item in superscripts:
            text = manipulate.get_stripped_text(item).strip()
            if self.gv.is_number(text):
                footnote_list.append(item)
                footnote_text.append(text)

        if len(footnote_list) == 0:
            self.debug.print_debug(self, u'Found no superscripted footnote entries')
            return

        # if it doesn't work, this is an expensive operation
        # however, once we've found all we can stop, so it's worth doing

        try:
            footnote = int(footnote_text[len(footnote_text) - 1].strip())
        except:
            self.debug.print_debug(self, u'Unable to parse last footnote as number. Leaving footnote classifier.')
            return

        count = len(footnote_text) - 1
        offset = footnote
        failures = 0

        for number in range(int(footnote_text[len(footnote_text) - 1].strip()), int(footnote_text[0].strip())):

            if not str(int(number + (offset - 1))) in footnote_text and \
                    (int(footnote_text[count]) != int(number + (offset - 1))):
                self.debug.print_debug(self, u'Expected footnote {0}. Found {1}.'.format(int(number + (offset - 1)),
                                                                                         footnote_text[count]))
                failures += 1

                if failures > 1:
                    self.debug.print_debug(self, u'Found more than 1 misaligned footnote. Bailing.')
                    return
                else:
                    # we need to try and find the number in some text, somewhere, then re-superscript it
                    # it should occur twice only: once for the number itself and once for the paragraph that will be
                    # made into a footnote. However, if the method is a list at the end of the document it will be
                    # only a single occurrence

                    text_blocks = tree.xpath('//text()[contains(self::text()'
                                             ', "{0}")]'.format(int(number + (offset - 1))))

                    if len(text_blocks) >= 1:
                        parsed = False
                        for block_to_change in text_blocks:
                            # (1)[^\d]
                            ref_match = re.compile('^.*(?P<number>{0})[^\d].*'.format(str(int(number + (offset - 1)))))
                            result = ref_match.match(block_to_change.getparent().text)

                            if result:
                                self.debug.print_debug(self, u'Found potential point for footnote #{0}.'
                                                             u' Superscripting'.format(int(number + (offset - 1))))

                                parent = block_to_change.getparent()

                                before_after = parent.text.split(str(int(number + (offset - 1))))

                                parent.text = before_after[0]

                                encapsulate = etree.Element('sup')
                                encapsulate.text = str(int(number + (offset - 1)))
                                encapsulate.tail = ''.join(before_after[1:])

                                Manipulate.append_safe(parent, encapsulate, self)

                                footnote_list.insert(count, encapsulate)
                                footnote_text.insert(count, str(int(number + (offset - 1))))
                                offset += 1
                                parsed = True
                                break

                        if not parsed:
                            self.debug.print_debug(self, u'Unable to find footnote #{0}'.format(int(number + (offset - 1))))
                            return
                    else:
                        self.debug.print_debug(self, u'Unable to find footnote #{0}'.format(int(number + (offset - 1))))
                        return
                    pass

            count -= 1

        whole_document = reversed(tree.xpath('//tei:p[@rend="Normal" or not(@rend)]',
                                             namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))

        found = []

        footnote = int(footnote_text[0].strip())

        for item in whole_document:
            text = manipulate.get_stripped_text(item).strip()

            if text.startswith(str(footnote)):
                found.append(item)

                footnote -= 1

                if len(found) == len(footnote_list):
                    break

        if len(found) == 0:
            # last ditch: see if there is an ordered list near the end of the document that has the same number of
            # elements as the footnote list
            self.debug.print_debug(self, u'No luck locating footnote text. Attempting list method.')
            lists = reversed(tree.xpath('//tei:list[@type="ordered"]',
                                        namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))
            first = True
            for list in lists:
                if not first:
                    break
                else:
                    first = True
                    
                for item in list:
                    found.append(item)

                    if len(found) == len(footnote_list):
                        break

        # note: all lists are reversed by this point (ie go from the back of the document upwards)
        if len(found) == len(footnote_list):
            self.debug.print_debug(self, u'Found {0} superscripted footnote entries'.format(len(found)))

            current = 0
            for footnote in footnote_list:
                # null the text (this will be generated automatically)
                if Manipulate.append_safe(footnote, found[current], self):
                    footnote.text = ''

                    footnote.tag = 'note'
                    footnote.attrib['id'] = 'fn_from_list{0}'.format(current)

                    replace_regex = '^({0}[\.\s\)]*)'.format(len(found) - current)

                    if found[current].text and not found[current].text.strip().startswith(str(len(found) - current)):
                        # in this case the footnote text is inside a sub-element
                        for sub_element in found:
                            if sub_element.text and sub_element.text.strip().startswith(str(len(found) - current)):
                                sub_element.text = re.sub(replace_regex, '', sub_element.text)
                                break
                        pass
                    elif found[current].text:
                        found[current].text = re.sub(replace_regex, '', found[current].text)

                    manipulate.save_tree(tree)
                    self.debug.print_debug(self, u'Processing footnote {0}'.format(current + 1))
                else:
                    # failed to add a footnote
                    self.debug.print_debug(self, u'Footnote failure. Aborting process.')
                    return

                current += 1
        else:
            self.debug.print_debug(self, u'Found {0} superscripted footnote entries but could not correlate this with'
                                         ' {1} paragraph entries'.format(len(footnote_list), len(found)))

        manipulate.save_tree(tree)

    def process_number_list(self, tree, manipulate, treestring):

        if not u'>1' and not u'>(' in treestring:
            return

        # select all p elements followed by another p element
        expression = u'//tei:p[contains("(0123456789ivxlcmdIVXLCMD", substring(., 1, 1))]'

        elements = tree.xpath(expression, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        list_element = None
        iteration = 0
        number = None

        number_match = re.compile('^\s*(?P<rn>\(?\s*(?P<number>\d+)[\.\s\)]+).+')
        roman_match = re.compile('^(?P<rn>M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})[\.\s\)]+).+',
                                 re.IGNORECASE)

        for element in elements:
            text = manipulate.get_stripped_text(element)
            match = number_match.match(text)
            roman_result = roman_match.match(text)
            cont = False

            if match or roman_result:
                if match:
                    number = match.groups('rn')[1]
                    offset = len(match.groups('rn')[0])
                else:
                    offset = len(roman_result.groups('rn')[0])
                iteration += 1

                roman = self.int_to_roman(iteration)

                if not number == str(iteration) and not text.startswith(roman) and not text.startswith(roman.lower()):
                    if iteration > 1:
                        old_it = iteration
                        iteration = 1

                        roman = self.int_to_roman(iteration)

                        if not number == str(iteration) and not text.startswith(roman) \
                            and not text.startswith(roman.lower()):

                            self.debug.print_debug(self, u'List element was misordered and did not start new list. '
                                                         u'Expected {0}'.format(iteration))

                            iteration = old_it - 1
                        else:
                            self.debug.print_debug(self, u'Starting new numeric list from cue: {0}'.format(text))
                            cont = True
                else:
                    cont = True

                    if iteration > 1:
                        self.debug.print_debug(self, u'Handling list element {0}'.format(text))
                    else:
                        next_start = iteration + 1
                        next_element_index = elements.index(element) + 1

                        if next_element_index > len(elements):
                            cont = False
                        else:
                            next_element = elements[next_element_index]

                            next_text = manipulate.get_stripped_text(next_element)
                            next_match = number_match.match(next_text)
                            next_roman_result = roman_match.match(next_text)
                            next_number = None

                            if next_match or next_roman_result:
                                if next_match:
                                    next_number = next_match.groups('rn')[1]
                                    next_offset = len(next_match.groups('rn')[0])
                                else:
                                    next_offset = len(next_roman_result.groups('rn')[0])

                                next_roman = self.int_to_roman(iteration)

                                if not next_number == str(iteration + 1) and not next_text.startswith(next_roman)\
                                    and not next_text.startswith(next_roman.lower()):
                                    cont = False
                            else:
                                cont = False

                        if cont:
                            self.debug.print_debug(self, u'Starting new numeric list from cue: {0}'.format(text))
                        else:
                            self.debug.print_debug(self, u'Cannot start list on last element: {0}'.format(text))


                if cont:
                    if iteration == 1:
                        # start new list
                        list_element = etree.Element('list')
                        list_element.attrib[u'type'] = u'ordered'
                        element.addprevious(list_element)

                        element.tag = 'item'
                        if element.text:
                            element.text = element.text[(int(offset) + int(math.floor(int(iteration/10)))):]
                        else:
                            element.text = text[(int(offset) + int(math.floor(int(iteration/10)))):]
                        Manipulate.append_safe(list_element, element, self)

                    elif list_element is not None:
                        element.tag = 'item'
                        if element.text:
                            element.text = element.text[(int(offset) + int(math.floor(int(iteration/10)))):]
                        else:
                            element.text = text[(int(offset) + int(math.floor(int(iteration/10)))):]
                        Manipulate.append_safe(list_element, element, self)
                    else:
                        self.debug.print_debug(self, u'Reference list PANIC: {0}'.format(text))

        manipulate.save_tree(tree)

    def int_to_roman(self, input):
        if type(input) != type(1):
            raise TypeError, "expected integer, got %s" % type(input)

        if not 0 < input < 4000:
            raise ValueError, "Argument must be between 1 and 3999"

        ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
        nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
        result = ""

        for i in range(len(ints)):
            count = int(input / ints[i])
            result += nums[i] * count
            input -= ints[i] * count
        return result

    def run(self):
        if int(self.gv.settings.args['--aggression']) < int(self.gv.settings.get_setting('listclassifier',
                                                                                         self, domain='aggression')):
            self.debug.print_debug(self, u'Aggression level too low: exiting module.')
            return

        dash_lists = self.gv.settings.get_setting('dash-lists', self) == "True"
        bracket_refs = self.gv.settings.get_setting('bracket-references-and-footnotes', self) == "True"
        superscripted_footnotes = self.gv.settings.get_setting('superscripted-footnotes', self) == "True"

        if not dash_lists and not bracket_refs and not superscripted_footnotes:
            return

        # load the DOM
        tree = self.set_dom_tree(self.gv.tei_file_path)

        manipulate = TeiManipulate(self.gv)

        string_version = etree.tostring(tree)

        # look for dash separated list
        # - Item 1
        # - Item 2
        if dash_lists:
            self.process_dash_list(tree, manipulate, string_version)

        if int(self.gv.settings.args['--aggression']) >= 10 and bracket_refs:
            backup_tree = copy(tree)
            try:
                # look for footnote list [1], [2] etc.
                self.process_enclosed_ref_list(tree, manipulate, string_version)
            except:
                self.debug.print_debug(self, u'Error processing footnote or reference list. Reverting to backup tree')
                tree = backup_tree
                manipulate.save_tree(tree)

        if superscripted_footnotes:
            self.process_superscript_footnotes(tree, manipulate)

        self.process_number_list(tree, manipulate, string_version)