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
                    tag_to_parse = re.sub(r'.+}', '', child.text)

                    new_element = etree.Element(replace_tag, rel=attribute)
                    new_element.text = tag_to_parse

                    child.addnext(new_element)

                    for subchild in child:
                        if type(subchild) is etree._Element:
                            new_element.append(subchild)

                    child.getparent().remove(child)

        tree.write(self.gv.tei_file_path)

    def find_reference_list_in_word_list(self):
        # load the DOM
        tree = self.load_dom_tree()

        # determine if the last element in the document is a list
        select = u'//tei:div[last()]/*[last()]'

        for last_list in tree.xpath(select, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if last_list.tag == '{http://www.tei-c.org/ns/1.0}list':
                # it is a list, so change to reference list
                self.debug.print_debug(self, u'Found a list as last element. Treating as bibliography.')
                last_list.tag = '{http://www.tei-c.org/ns/1.0}div'
                last_list.attrib['rend'] = u'Bibliography'

                parent_element = None

                # now convert each line
                for list_item in last_list:
                    new_element = etree.Element('p')
                    new_element.attrib['rend'] = u'Bibliography'

                    list_item.addnext(new_element)
                    new_element.append(list_item)
                    list_item.tag = '{http://www.tei-c.org/ns/1.0}ref'
                    list_item.attrib['target'] = 'None'

        tree.write(self.gv.tei_file_path)

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
                ret.append(new_element)

            ret = new_element

        return ret

    def enclose_bibliography_tags(self, xpath, top_tag, sub_tag, attrib, attribvalue):
        #tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')
        # load the DOM
        tree = self.load_dom_tree()

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
            self.debug.print_debug(self, u'Found existing back block. Using it.')
        except:
            self.debug.print_debug(self, u'Creating back block.')
            sub_element = etree.Element(sub_tag)
            sub_element.attrib[attrib] = attribvalue
            new_element.insert(0, sub_element)

        if not parent.tag == top_tag:
            parent.addnext(new_element)

        for element in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            sub_element.append(element)

        # remove all refs within
        for ref in tree.xpath('//tei:p[@rend="Bibliography"]/tei:ref',
                              namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            ref.tag = 'p'
            ref.attrib['rend'] = 'Bibliography'
            del ref.attrib['target']

            ref_parent = ref.getparent()

            ref_parent.addnext(ref)

            ref_parent.getparent().remove(ref_parent)

        tree.write(self.gv.tei_file_path)

    def tag_bibliography(self, xpath, start_text, caller):
        # load the DOM
        tree = self.load_dom_tree()

        for child in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if child.text.startswith(start_text):
                child.text = child.text.replace(start_text, '')

        tree.write(self.gv.tei_file_path)

    def tag_bibliography_non_csl(self, xpath, start_text, caller):
        # load the DOM
        tree = self.load_dom_tree()
        change_element = None

        for child in tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            if child.text.startswith(start_text):
                child.text = child.text.replace(start_text, '')
                try:
                    change_element = child.getparent().getparent()
                except:
                    pass

        if not change_element is None:
            # change the "sec" above to "p"
            change_element.tag = 'div'

            new_element = etree.Element('div')
            change_element.addnext(new_element)
            new_element.append(change_element)

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

                    outer.append(element)
                    new_element.append(outer)

            new_element.remove(change_element)



        tree.write(self.gv.tei_file_path)

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

        tree.write(self.gv.tei_file_path)

    def tag_headings(self):
        # load the DOM
        tree = self.load_dom_tree()

        iterator = 0

        # search the tree and grab the parent
        for child in tree.xpath("//tei:head", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            child.attrib['meTypesetHeadingID'] = str(iterator)
            iterator += 1

        tree.write(self.gv.tei_file_path)

        return iterator

    # changes the parent element of the outer_xpath expression to the new_value
    def change_outer(self, outer_xpath, new_value, size_attribute):
        tree = self.load_dom_tree()

        # search the tree and grab the parent
        for child in tree.xpath(outer_xpath + "/..", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            child.tag = new_value
            child.attrib['meTypesetSize'] = size_attribute

        tree.write(self.gv.tei_file_path)

    # changes the parent element of the outer_xpath expression to the new_value
    def change_self_size(self, outer_xpath, size_attribute):
        tree = self.load_dom_tree()

        # search the tree and grab the parent
        for child in tree.xpath(outer_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            child.attrib[u'meTypesetSize'] = size_attribute
            if not (child.attrib['rend'] is None):
                if u'bold' in child.attrib[u'rend']:
                    child.attrib[u'rend'] = child.attrib[u'rend'].replace(u'bold', u'')

        tree.write(self.gv.tei_file_path)

    # changes the parent element of the outer_xpath expression to the new_value
    def enclose_and_change_self_size(self, outer_xpath, size_attribute, tag, change_tag):
        tree = self.load_dom_tree()

        # search the tree and grab the parent
        for child in tree.xpath(outer_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            self.debug.print_debug(self, 'Enclosing and changing size: {0}'.format(child.tag))
            new_element = etree.Element(tag)
            child.attrib[u'meTypesetSize'] = size_attribute
            child.tag = change_tag
            child.addnext(new_element)
            new_element.append(child)

            if not (child.attrib['rend'] is None):
                if u'bold' in child.attrib[u'rend']:
                    child.attrib[u'rend'] = child.attrib[u'rend'].replace(u'bold', u'')

        tree.write(self.gv.tei_file_path)

    def move_size_div(self, heading_id, sibling_id):
        tree = self.load_dom_tree()

        source_node = tree.xpath(u'//tei:head[@meTypesetHeadingID=\'{0}\']/..'.format(str(heading_id)),
                                 namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

        destination_node = tree.xpath(u'//tei:head[@meTypesetHeadingID=\'{0}\']/..'.format(str(sibling_id)),
                                      namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

        destination_node.addnext(source_node)

        tree.write(self.gv.tei_file_path)

    def resize_headings(self, old_size, new_size):
        tree = self.load_dom_tree()

        nodes_to_downsize = tree.xpath(u'//tei:head[@meTypesetSize=\'{0}\']'.format(str(old_size)),
                                       namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        for node_to_downsize in nodes_to_downsize:
            node_to_downsize.attrib['meTypesetSize'] = new_size

        tree.write(self.gv.tei_file_path)

    def enclose(self, start_xpath, select_xpath):
        tree = self.load_dom_tree()

        node = tree.xpath(start_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        div = etree.Element('div')
        node.addprevious(div)

        self.debug.print_debug(self, 'Selecting for enclosure: {0}'.format(select_xpath))

        # search the tree and grab the elements
        child = tree.xpath(select_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        # move the elements
        for element in child:
            div.append(element)

        tree.write(self.gv.tei_file_path)

    def enclose_all(self, start_xpath, new_enclose, start_index):
        tree = self.load_dom_tree()

        self.debug.print_debug(self, 'Selecting for enclosure: {0}'.format(start_xpath))

        # search the tree and grab the elements
        child = tree.xpath(start_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        index = 0
        added = False
        div = etree.Element(new_enclose)

        # move the elements
        for element in child:
            if not added:
                element.getparent().addnext(div)
                added = True

            div.append(element)
            index += 1

        tree.write(self.gv.tei_file_path)

    def change_wmf_image_links(self):
        tree = self.load_dom_tree()
        for image_link in tree.xpath('//tei:graphic', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            converted_image_link = re.sub(r'\.wmf', '.png', image_link.xpath('@url')[0])
            image_link.attrib['url'] = converted_image_link
        tree.write(self.gv.tei_file_path)

    def run(self):
        # convert .wmf image links to png
        self.change_wmf_image_links()
        os.remove(self.dom_temp_file)



