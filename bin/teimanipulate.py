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

    def enclose_bibliography_tags(self, xpath, top_tag, sub_tag, attrib, attribvalue):
        #tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')
        # load the DOM
        tree = self.load_dom_tree()

        parent = None

        # find the parent
        try:
            parent = tree.xpath('//tei:body', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        except:
            return

        new_element = etree.Element(top_tag)
        sub_element = etree.Element(sub_tag)

        sub_element.attrib[attrib] = attribvalue

        new_element.insert(0, sub_element)

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

    def downsize_headings(self, root_size, size):
        tree = self.load_dom_tree()

        nodes_to_downsize = tree.xpath(u'//tei:head[@meTypesetSize=\'{0}\']'.format(str(size)),
                                       namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        for node_to_downsize in nodes_to_downsize:
            node_to_downsize.attrib['meTypesetSize'] = root_size

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

        # move the elements
        for element in child:
            if index >= start_index:
                div = etree.Element(new_enclose)
                element.getparent().addnext(div)
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



