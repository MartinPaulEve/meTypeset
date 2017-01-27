#!/usr/bin/env python
from lxml import etree
from lxml import objectify
import re
import os
from manipulate import Manipulate

__author__ = "Martin Paul Eve, Dulip Withanage"
__email__ = "martin@martineve.com"


class TeiManipulate(Manipulate):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        self.dom_to_load = self.gv.tei_file_path
        self.dom_temp_file = self.gv.tei_temp_file_path
        self.mod_name = 'TEI'
        Manipulate.__init__(self, gv)

    def save_tree(self, tree):
        tree.write(self.dom_temp_file, pretty_print=self.gv.settings.args['--prettytei'])
        tree.write(self.dom_to_load, pretty_print=self.gv.settings.args['--prettytei'])

    def get_object_list(self, xpath, start_text, wrap_tag):
        # load the DOM
        tree = self.load_dom_tree()

        object_list = []

        # search the tree and grab the parent
        for child in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if not (child.text is None):
                if child.text.startswith(start_text):
                    object_list.append(objectify.fromstring(u'<{1}><entry>{0}'
                                                            u'</entry></{1}>'.format(etree.tostring(child),
                                                                                     wrap_tag)))

        return object_list

    def drop_addin_json(self, xpath, start_text, replace_tag, attribute, caller):
        # load the DOM
        tree = self.load_dom_tree()

        # search the tree and grab the parent
        for child in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if not (child.text is None):
                # check that this is a known addin
                if child.text.startswith(start_text):
                    tag_to_parse = re.sub(r'.+}\s?', '', child.text)

                    new_element = etree.Element(replace_tag, rel=attribute)
                    new_element.text = tag_to_parse

                    child.addnext(new_element)

                    for subchild in child:
                        if type(subchild) is etree._Element:
                            Manipulate.append_safe(new_element, subchild, self)

                    child.getparent().remove(child)

        self.save_tree(tree)

    def do_list_bibliography(self, xpath):
        found = False
        year_test =  re.compile('((1|2)\d{3}[a-z]?)|(n\.d\.)')

        for last_list in xpath:
            if last_list.tag.endswith('list'):
                if len(last_list) > 0:

                    text = self.get_stripped_text(last_list[0])
                    match = year_test.findall(text)

                    if match:
                        # it is a list, so change to reference list
                        self.debug.print_debug(self, u'Found a list as last element. Treating as bibliography.')
                        self.gv.used_list_method = True
                        found = True
                        last_list.tag = '{http://www.tei-c.org/ns/1.0}div'
                        last_list.attrib['rend'] = u'Bibliography'

                        parent_element = None

                        # now convert each line
                        for list_item in last_list:
                            new_element = etree.Element('p')
                            new_element.attrib['rend'] = u'Bibliography'

                            list_item.addnext(new_element)
                            Manipulate.append_safe(new_element, list_item, self)
                            list_item.tag = '{http://www.tei-c.org/ns/1.0}ref'
                            list_item.attrib['target'] = 'None'
            elif last_list.tag.endswith('item'):

                text = self.get_stripped_text(last_list)
                match = year_test.findall(text)

                if match:
                    # it is a list, so change to reference list
                    self.debug.print_debug(self, u'Found a list as last element via item. Treating as bibliography.')
                    self.gv.used_list_method = True
                    last_list = last_list.getparent()
                    found = True
                    last_list.tag = '{http://www.tei-c.org/ns/1.0}div'
                    last_list.attrib['rend'] = u'Bibliography'

                    parent_element = None

                    # now convert each line
                    for list_item in last_list:
                        new_element = etree.Element('p')
                        new_element.attrib['rend'] = u'Bibliography'

                        list_item.addnext(new_element)
                        Manipulate.append_safe(new_element, list_item, self)
                        list_item.tag = '{http://www.tei-c.org/ns/1.0}ref'
                        list_item.attrib['target'] = 'None'
            else:
                self.debug.print_debug(self, u'Last element in document was {0}. Not treating as '
                                             u'bibliography.'.format(xpath[0].tag))
        return found

    def do_cit_bibliography(self, xpath):
        found = False

        for last_list in xpath:

            if last_list.tag == '{http://www.tei-c.org/ns/1.0}cit':
                # it is a list, so change to reference list
                self.debug.print_debug(self, u'Found a cit as last element. Treating as bibliography.')
                found = True

                sibling_tag = last_list.tag

                sibling = last_list.getprevious()

                while sibling.tag == sibling_tag:
                    next_sibling = sibling.getprevious()

                    new_element = etree.Element('p')
                    new_element.attrib['rend'] = u'Bibliography'

                    sibling.addnext(new_element)
                    Manipulate.append_safe(new_element, sibling, self)
                    sibling.tag = '{http://www.tei-c.org/ns/1.0}ref'
                    sibling.attrib['target'] = 'None'

                    sibling = next_sibling


                new_element = etree.Element('p')
                new_element.attrib['rend'] = u'Bibliography'

                last_list.addnext(new_element)
                Manipulate.append_safe(new_element, last_list, self)
                last_list.tag = '{http://www.tei-c.org/ns/1.0}ref'
                last_list.attrib['target'] = 'None'


            else:
                self.debug.print_debug(self, u'Last element in document was {0}. Not treating as '
                                             u'bibliography.'.format(xpath[0].tag))
        return found

    def find_reference_list_in_word_list(self, tree):
        # determine if the last element in the document is a list
        select = u'(//tei:div/*[not(self::tei:div)])[last()]'

        found = False

        # remove any empty lists
        tree = self.load_dom_tree()

        for item in tree.xpath('//tei:list', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if len(item) == 0:
                item.tag = 'REMOVE'

        etree.strip_elements(tree, 'REMOVE')

        xpath = tree.xpath(select, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        found = self.do_list_bibliography(xpath)

        if not found:
            # iterate up one more paragraph
            try:
                last_para = tree.xpath(select, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

                second_last = last_para.getprevious()

                found = self.do_list_bibliography(second_last)

            except:
                pass

        if not found:
            self.do_cit_bibliography(xpath)

        self.save_tree(tree)

        self.debug.print_debug(self, u'Ascertaining if last element is a bibliographic list')

        return found

    def find_or_create_element(self, tree, element_tag, add_xpath, is_sibling):
        # find_or_create_elements(tree, 'back', '//body', true)
        ret = None
        try:
            ret = tree.xpath(u'//tei:' + element_tag, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
            self.debug.print_debug(self, u'Found existing {0}. Using it.'.format(element_tag))
        except:
            self.debug.print_debug(self, u'Unable to find an existing {0} element.'.format(element_tag))

        if ret is None:
            self.debug.print_debug(self, u'Creating new {0} element.'.format(element_tag))
            ret = tree.xpath(add_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
            new_element = etree.Element(element_tag)

            if is_sibling:
                ret.addnext(new_element)
            else:
                Manipulate.append_safe(ret, new_element, self)

            ret = new_element

        return ret

    def enclose_bibliography_tags(self, xpath, top_tag, sub_tag, attrib, attribvalue):
        #tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')

        # load the DOM
        tree = self.load_dom_tree()

        if len(tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})) == 0:
            return False

        parent = None

        # find the parent
        parent = self.find_or_create_element(tree, 'back', '//tei:body', True)

        if not (parent.tag == top_tag) and not (parent.tag == '{http://www.tei-c.org/ns/1.0}' + top_tag):
            new_element = etree.Element(top_tag)
            self.debug.print_debug(self, u'Mismatch {0} {1}.'.format(parent.tag, top_tag))
        else:
            new_element = parent

        try:
            sub_element = tree.xpath('//tei:back/tei:div[@type="bibliogr"]',
                                     namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
            self.debug.print_debug(self, u'Found existing bibliography block. Using it.')
        except:
            self.debug.print_debug(self, u'Creating bibliography block.')
            sub_element = etree.Element(sub_tag)
            sub_element.attrib[attrib] = attribvalue
            new_element.insert(0, sub_element)

        if not parent.tag == top_tag and not parent.tag == '{http://www.tei-c.org/ns/1.0}' + top_tag:
            parent.addnext(new_element)

        for element in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            Manipulate.append_safe(sub_element, element, self)

        # remove all refs within
        if len(tree.xpath(xpath + u'/tei:ref', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})) > 0:
            for ref in tree.xpath(xpath + u'/tei:ref',
                                  namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

                # ensure that the ref is just a dud and not a valid link to a protocol schema
                if 'target' in ref.attrib and not ':' in ref.attrib['target']:
                    ref.tag = 'p'
                    ref.attrib['rend'] = 'Bibliography'
                    if 'target' in ref.attrib:
                        del ref.attrib['target']

                    ref_parent = ref.getparent()

                    ref_parent.addnext(ref)
                    if ref_parent.getparent() is not None:  
                      ref_parent.getparent().remove(ref_parent)
        else:
            for ref in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
                ref.tag = 'p'
                ref.attrib['rend'] = 'Bibliography'

        self.save_tree(tree)

        self.debug.print_debug(self, u'Processed bibliography')
        return True

    def contains_graphic(self, element):
        for item in element:
            if item.tag.endswith('graphic'):
                return True

            sub = self.contains_graphic(item)

            if sub is True:
                return True

        return False

    def check_for_continued_references(self, found_element, numeric_start_test, count, elements_to_parse, year_test,
                                       blank_text):
        self.debug.print_debug(self, u'Enumerating next section for references')
        next_div = found_element.getparent().getnext()

        a_child = None
        stop = False

        if next_div is not None and len(next_div) > 0:

            child = next_div[0]
            a_child = child
            text = self.get_stripped_text(child)

            numeric_start = numeric_start_test.findall(text)

            if numeric_start:
                self.debug.print_debug(self, u'Halting parsing of references after break as numeric start found '
                                             u'(triggered by {0})'.format(text))
                return False

            match = year_test.findall(text)
            inner_match = blank_text.findall(text)

            if match or inner_match:
                count += 1
                elements_to_parse.append(child)
                self.debug.print_debug(self, u'[REF{0}] Adding {1} from next section'.format(count, text))

                for sibling in child.itersiblings():
                    # once we've got a definite section that is references, we will add all of it

                    text = self.get_stripped_text(sibling)
                    numeric_start = numeric_start_test.findall(text)

                    if numeric_start:
                        self.debug.print_debug(self, u'Halting parsing of references after break as numeric start found'
                                                     u' (triggered by {0})'.format(text))
                        return False

                    count += 1
                    elements_to_parse.append(sibling)
                    self.debug.print_debug(self, u'[REF{0}] Adding {1} from next section'.format(count, text))
            else:
                return False

        if a_child is not None:
            should_fail = self.check_for_continued_references(a_child, numeric_start_test, count, elements_to_parse,
                                                              year_test, blank_text)

            if not should_fail:
                return False

        return True

    def find_references_from_cue(self, cue, tree):
        # load the DOM

        found_element = None

        remove = ['cit', 'quote']

        for child in tree.xpath('//tei:p | //tei:head',
                                namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

            skip = self.contains_graphic(child)

            if not skip:
                stripped_text = self.get_stripped_text(child).strip(':.')

                if stripped_text.lower().strip() == cue.lower().strip():
                    found_element = child
                    self.debug.print_debug(self, u'Found linguistic cue: {0}'.format(stripped_text.lower().strip()))
                    break

        # the endgame switch is set when we're handling the last two lines (which are sometimes acknowledgements etc)
        endgame = False
        last = None

        # pre-compile all needed regular expressions
        year_test =  re.compile('((1|2)\d{3}[a-z]?)|(n\.d\.)')
        blank_text = re.compile('XXXX')
        numeric_start_test = re.compile('^(?P<start>[\[{(]*?[\d\.]+[\]})]*?\s*?).+')
        break_index = 0

        elements_to_parse = []

        if found_element is not None:
            found_element.attrib['rend'] = 'REMOVE'
            count = 0

            for sibling in found_element.itersiblings():

                text = self.get_stripped_text(sibling)

                count += 1
                elements_to_parse.append(sibling)
                self.debug.print_debug(self, u'[REF{0}] Adding {1}'.format(count, text))

            break_index = count - 1

            self.check_for_continued_references(found_element, numeric_start_test, count, elements_to_parse, year_test,
                                                blank_text)

            # at this point we have a list with all potential reference elements in it
            # we also have an index to that list after which references have spanned section breaks
            # after this point, we want to be more cautious in joining references together

            count = 0
            failcount = 0

            for item in elements_to_parse:
                count += 1

                text = self.get_stripped_text(item)
                match = year_test.findall(text)
                inner_match = blank_text.findall(text)

                if match or inner_match:
                    # this is straightforward: the reference looks like a reference
                    self.debug.print_debug(self, u'[REF{0}] Adding bibliography element from linguistic '
                                                 u'cue'.format(count))
                    item.attrib['rend'] = 'Bibliography'
                    item.tag = 'p'
                    last = item

                    failcount = 0

                    for child in item:
                        for remove_tag in remove:
                            if child.tag is not None and child.tag.endswith(remove_tag):
                                child.tag = 'REMOVE'

                elif elements_to_parse.index(item) > (len(elements_to_parse) - 3) and last is not None:
                    # this is the last two lines of a reference block when it doesn't look like a reference
                    # it could easily be some stranded acknowledgements, so we leave it unless it's just a link
                    parsed = False

                    if item.text is None or item.text == '':
                        for child in item:
                            if child.tag is not None and child.tag.endswith('ref') \
                                    and (child.tail == '' or child.tail is None):
                                item.tag = 'hi'
                                last.append(item)
                                parsed = True

                                self.debug.print_debug(self, u'[REF{0}] Appending to previous element '
                                                             u'despite endgame condition'.format(count))

                    if not parsed:
                        self.debug.print_debug(self, u'[REF{0}] Left item in situ'.format(count))

                elif count - 1 > break_index and last is not None:
                    # we treat this portion more sensitively because it is spanning sections and bail if more than
                    # two references in a row do not match
                    failcount += 1

                    if failcount > 2:
                        self.debug.print_debug(self, u'Bailing from linguistic cue parsing on fail count condition')
                        break
                    else:
                        self.debug.print_debug(self, u'[REF{0}] Appending to previous element'.format(count))
                        item.tag = 'hi'
                        last.append(item)

                elif last is not None:
                    # otherwise, we will add this reference to the last block used
                    self.debug.print_debug(self, u'[REF{0}] Appending to previous element'.format(count))
                    item.tag = 'hi'
                    last.append(item)

                else:
                    self.debug.print_debug(self, u'[REF{0}] Left item in situ'.format(count))

            etree.strip_tags(found_element.getparent(), 'REMOVE')

            found_element.getparent().remove(found_element)

            self.save_tree(tree)

            return True

        return False

    def tag_bibliography(self, xpath, start_text, caller, parent_tag=u'{http://www.tei-c.org/ns/1.0}sec',
                         classify_siblings=False, sibling_tag=u'{http://www.tei-c.org/ns/1.0}cit',
                         sub_xpath='//tei:quote/tei:p | //tei:quote/tei:head'):
        # load the DOM
        tree = self.load_dom_tree()

        found = False

        for child in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if not type(child) is etree._Element:
                if child.text.startswith(start_text):
                    child.text = child.text.replace(start_text, '')
                    found = True
            elif child.text and child.text.startswith(start_text):
                found = True
                child.text = child.text.replace(start_text, '')
            else:
                if not len(child.getchildren()) == 0:
                    if child.getchildren()[0].tag == "{http://www.tei-c.org/ns/1.0}hi":
                        if not child.getchildren()[0].text is None:
                            if child.getchildren()[0].text.startswith(start_text):
                                found = True
                                child.getchildren()[0].text = child.getchildren()[0].text.replace(start_text, '')

            if not found:
                return

            parent = child.getparent()

            while parent is not None:

                if parent.tag == parent_tag:
                    parent.attrib['rend'] = 'Bibliography'
                    parent = None
                else:
                    parent = parent.getparent()

            if classify_siblings:
                parent = child.getparent()

                sibling = None

                while parent is not None:
                    if parent.tag == sibling_tag:
                        sibling = parent
                        parent = None
                    else:
                        parent = parent.getparent()

                if sibling is not None:
                    for child in sibling.itersiblings():
                        for element in child.xpath(sub_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
                            text = self.get_stripped_text(element)

                            element.attrib['rend'] = 'Bibliography'
                else:
                    self.debug.print_debug(self, u'Failed to find sibling in bibliographic addin classification')

        self.save_tree(tree)

    def tag_bibliography_non_csl(self, xpath, start_text, caller):
        # load the DOM
        tree = self.load_dom_tree()
        change_element = None

        for child in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            try:
                if child.text.startswith(start_text):
                    child.text = child.text.replace(start_text, '')
                    change_element = child.getparent().getparent()
            except:
                pass

        if not change_element is None:
            # change the "sec" above to "p"
            change_element.tag = 'div'

            new_element = etree.Element('div')
            change_element.addnext(new_element)
            Manipulate.append_safe(new_element, change_element, self)

            # change all sub-elements to ref
            for element in change_element:
                if element.tag == '{http://www.tei-c.org/ns/1.0}head':
                    self.debug.print_debug(self, u'Dropping head element: {0}'.format(etree.tostring(element)))
                    change_element.remove(element)
                elif element.tag == '{http://www.tei-c.org/ns/1.0}p':
                    outer = etree.Element('p')
                    outer.attrib['rend'] = 'Bibliography'
                    element.tag = 'ref'
                    element.attrib['target'] = 'None'

                    Manipulate.append_safe(outer, element, self)
                    Manipulate.append_safe(new_element, outer, self)

            new_element.remove(change_element)



        self.save_tree(tree)

    def drop_addin(self, xpath, start_text, sub_tag, replace_tag, attribute, caller, wrap_tag, delete_original):
        # load the DOM
        tree = self.load_dom_tree()

        # search the tree and grab the parent
        for child in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if not (child.text is None):
                # check that this is a known addin
                if child.text.startswith(start_text):
                    # parse the (encoded) text of this element into a new tree
                    tag_to_parse = re.sub(r'&', '&amp;', child.text)
                    sub_tree = etree.fromstring(u'<{1}><entry>{0}</entry></{1}>'.format(tag_to_parse, wrap_tag))

                    # extract the sub element from this new tree and preserve the tail text
                    sub_element = sub_tree.xpath('//entry/{0}'.format(sub_tag),
                                                 namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

                    if len(sub_element) > 0:
                        sub_element = sub_element[0]
                        self.debug.print_debug(self, u'Preserving tail of '
                                                     u'dropped {0} element: {1}'.format(caller.get_module_name(),
                                                                                        sub_element.tail))

                        # add the preserved tail text within the specified replacement tag type
                        new_element = etree.Element(replace_tag, rel = attribute)
                        new_element.text = sub_element.tail
                        child.addnext(new_element)

                    if delete_original:
                        child.getparent().remove(child)

        self.save_tree(tree)

    def tag_headings(self):
        # load the DOM
        tree = self.load_dom_tree()

        iterator = 0

        # search the tree and grab the parent
        for child in tree.xpath("//tei:head", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            child.attrib['meTypesetHeadingID'] = str(iterator)
            iterator += 1

        self.save_tree(tree)

        self.debug.print_debug(self, u'Assigned IDs to all headings')

        return iterator

    def check_for_disallowed_elements(self, allowed_elements, sub_element, exception_elements):
        add = True

        if sub_element.tag \
            and not sub_element.tag.replace('{http://www.tei-c.org/ns/1.0}', '') in allowed_elements:
            add = False
            self.debug.print_debug(self, u'Guessed title contained a disallowed '
                                         u'element ({0}). Skipping.'.format(sub_element.tag))
        return add

    def change_outer(self, outer_xpath, new_value, size_attribute):
        # changes the parent element of the outer_xpath expression to the new_value
        tree = self.load_dom_tree()

        allowed_elements = ['bold', 'italic', 'p', 'hi', 'seg', 'lb', 'ref']
        exception_elements = ['lb']

        # search the tree and grab the parent
        for child in tree.xpath(outer_xpath + "/..", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            add = True

            for sub_element in child:
                add = self.check_for_disallowed_elements(allowed_elements, sub_element, exception_elements)

                if not add:
                    break

                for sub_child in sub_element:
                    add = self.check_for_disallowed_elements(allowed_elements, sub_child, exception_elements)

                    if not add:
                        break

                if not add:
                    break

            if add:
                child.tag = new_value
                child.attrib['meTypesetSize'] = size_attribute

        self.save_tree(tree)

    # changes the parent element of the outer_xpath expression to the new_value
    def change_self_size(self, outer_xpath, size_attribute):
        tree = self.load_dom_tree()

        # search the tree and grab the parent
        for child in tree.xpath(outer_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            child.attrib[u'meTypesetSize'] = size_attribute
            if 'rend' in child.attrib and not (child.attrib['rend'] is None):
                if u'bold' in child.attrib[u'rend']:
                    child.attrib[u'rend'] = child.attrib[u'rend'].replace(u'bold', u'')

        self.save_tree(tree)

    # changes the parent element of the outer_xpath expression to the new_value
    def enclose_and_change_self_size(self, outer_xpath, size_attribute, tag, change_tag):
        tree = self.load_dom_tree()

        # search the tree and grab the parent
        for child in tree.xpath(outer_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            self.debug.print_debug(self, u'Enclosing and changing size: {0} to {1}'.format(child.tag, change_tag))
            new_element = etree.Element(tag)
            child.attrib[u'meTypesetSize'] = size_attribute
            if child.tag == '{http://www.tei-c.org/ns/1.0}' + change_tag:
                child.tag = 'REMOVE'
            else:
                for sub_element in child:
                    if sub_element.tag == '{http://www.tei-c.org/ns/1.0}' + change_tag:
                        child.tag = 'REMOVE'

            if child.tag != 'REMOVE':
                child.tag = change_tag

            child.addnext(new_element)
            Manipulate.append_safe(new_element, child, self)

            if child.tag == 'REMOVE':
                etree.strip_tags(child.getparent(), 'REMOVE')

            if not (child.attrib['rend'] is None):
                if u'bold' in child.attrib[u'rend']:
                    child.attrib[u'rend'] = child.attrib[u'rend'].replace(u'bold', u'')

        self.save_tree(tree)

    def move_size_div(self, heading_id, sibling_id):
        tree = self.load_dom_tree()

        source_node = tree.xpath(u'//tei:head[@meTypesetHeadingID=\'{0}\']/..'.format(str(heading_id)),
                                 namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

        while source_node.tag != '{http://www.tei-c.org/ns/1.0}div':
            source_node = source_node.getparent()

            if source_node is None:
                self.debug.print_debug(self, u'Encountered no div traversing up tree. Bailing.')
                return

        destination_node = tree.xpath(u'//tei:head[@meTypesetHeadingID=\'{0}\']/..'.format(str(sibling_id)),
                                      namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

        while destination_node.tag != '{http://www.tei-c.org/ns/1.0}div':
            destination_node = destination_node.getparent()

            if destination_node is None:
                self.debug.print_debug(self, u'Encountered no div traversing up tree. Bailing.')
                return

        destination_node.addnext(source_node)

        self.save_tree(tree)

    def resize_headings(self, old_size, new_size):
        tree = self.load_dom_tree()

        nodes_to_downsize = tree.xpath(u'//tei:head[@meTypesetSize=\'{0}\']'.format(str(old_size)),
                                       namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        for node_to_downsize in nodes_to_downsize:
            node_to_downsize.attrib['meTypesetSize'] = new_size
            self.debug.print_debug(self, u'Resizing node from: {0} to {1}'.format(old_size, new_size))

        self.save_tree(tree)

    def enclose(self, start_xpath, select_xpath):
        tree = self.load_dom_tree()

        node = tree.xpath(start_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        div = etree.Element('div')
        node.addprevious(div)

        self.debug.print_debug(self, u'Selecting for enclosure: {0}'.format(select_xpath))

        # search the tree and grab the elements
        child = tree.xpath(select_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        # move the elements
        for element in child:
            Manipulate.append_safe(div, element, self)

        self.save_tree(tree)

    def enclose_all(self, start_xpath, new_enclose, start_index):
        tree = self.load_dom_tree()

        self.debug.print_debug(self, u'Selecting for enclosure: {0}'.format(start_xpath))

        # search the tree and grab the elements
        child = tree.xpath(start_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        index = 0
        added = False
        div = etree.Element(new_enclose)

        # move the elements
        for element in child:
            if not added:
                element.getparent().addprevious(div)
                added = True

            Manipulate.append_safe(div, element, self)
            index += 1

        self.save_tree(tree)

    def change_wmf_image_links(self):
        tree = self.load_dom_tree()
        count = 0

        for image_link in tree.xpath('//tei:graphic', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            count += 1
            converted_image_link = re.sub(r'\.(w|e)mf', '.png', image_link.xpath('@url')[0])
            image_link.attrib['url'] = converted_image_link

        self.save_tree(tree)
        self.debug.print_debug(self, u'Replaced {0} WMF images with open equivalents'.format(count))

    def cleanup(self):
        tree = self.load_dom_tree()

        count = 0

        for element in tree.xpath('//tei:ref[@target="None"] | //tei:p[not(node())]',
                                  namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if len(element) == 0:
                self.debug.print_debug(self, u'Removing element {0} in cleanup'.format(element.tag))
                element.getparent().remove(element)
                count += 1

        # find and remove sections where there is a single title and it is the /only/ element therein
        for element in tree.xpath('//tei:div[not(node())]',
                                  namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if len(element) == 0:
                self.debug.print_debug(self, u'Removing element {0} in cleanup'.format(element.tag))
                element.getparent().remove(element)
                count += 1

        self.save_tree(tree)
        self.debug.print_debug(self, u'Removed {0} nodes during cleanup'.format(count))

        count = 0
        # normalize dud lists at end of document
        for element in tree.xpath('//tei:back/tei:div[@type="bibliogr"]/'
                                  'tei:p[@type="ordered" and @rend="Bibliography"]/tei:item',
                                  namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            element.tag = 'p'
            element.attrib['rend'] = 'Bibliography'
            element.getparent().tag = 'REMOVE'
            count += 1

        etree.strip_tags(tree, 'REMOVE')

        self.save_tree(tree)
        self.debug.print_debug(self, u'Cleaned {0} nested item bibliographic tags during cleanup'.format(count))

    def handle_metypesetdeleted(self, keep):
        tree = self.load_dom_tree()

        if keep:
            etree.strip_tags(tree, '{http://www.tei-c.org/ns/1.0}meTypesetDeleted')
        else:
            etree.strip_elements(tree, '{http://www.tei-c.org/ns/1.0}meTypesetDeleted', with_tail=False)

        self.save_tree(tree)
        self.debug.print_debug(self, u'Handled deleted text')

    def run(self):
        self.handle_metypesetdeleted(self.gv.settings.args['--includedeleted'])

        if int(self.gv.settings.args['--aggression']) > int(self.gv.settings.get_setting('wmfimagereplace', self,
                                                                                         domain='aggression')):
            # convert .wmf image links to png
            if not self.gv.settings.args['--noimageprocessing']:
                self.change_wmf_image_links()

        if int(self.gv.settings.args['--aggression']) > int(self.gv.settings.get_setting('teicleanup', self,
                                                                                         domain='aggression')):
            self.cleanup()

        os.remove(self.dom_temp_file)



