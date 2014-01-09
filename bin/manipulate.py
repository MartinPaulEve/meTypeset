#!/usr/bin/env python
from lxml import etree
from lxml import objectify
from copy import deepcopy
import uuid
import os
import shutil
import re

__author__ = "Martin Paul Eve, Dulip Withanage"
__email__ = "martin@martineve.com"


class Manipulate():
    def __init__(self, gv):
        self.gv = gv
        self.module_name = "XML Manipulator"
        self.debug = self.gv.debug

    def get_module_name(self):
        return self.module_name

    @staticmethod
    def search_and_replace_dom(tree, search_section, search_element, surround_with):
        for p in tree.xpath(".//" + search_section):
            search_results = p.findall(".//" + search_element)
            i = 0
            for result in search_results:
                i += 1
                new_elem = etree.Element(surround_with)
                new_elem.set("order", str(i))
                new_elem.set("uuid", str(uuid.uuid4()))
                if len(result) > 0:
                    elem_copy = deepcopy(result[0])
                    result.clear()
                    new_elem.append(elem_copy)
                    result.append(new_elem)
                else:
                    new_elem.text = result.text
                    result.clear()
                    result.append(new_elem)
        return tree

    @staticmethod
    def set_dom_tree(filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
        return etree.parse(filename, p)

    @staticmethod
    def update_tmp_file(fr, to):
        shutil.copy2(fr, to)

    @staticmethod
    def get_file_text(filename):
        f = open(filename)
        text = f.read()
        f.close()
        return text

    @staticmethod
    def xml_start(tag):
        return '<' + tag + '>'

    @staticmethod
    def xml_end(tag):
        return '</' + tag + '>'

    #replaces a given tag with a list of replace tags
    def replace(self, text, tag, *params):
        replace_start = ''
        replace_end = ''

        if len(params) > 0:
            for i in params:
                replace_start += self.xml_start(i)
                replace_end += self.xml_end(i)

            text = text.replace(self.xml_start(tag), replace_start).replace(self.xml_end(tag), replace_end)

        else:
            self.debug.print_debug(self, "No parameters passed to replace function")
        return text

    @staticmethod
    def write_output(f, text):
        out = open(f, 'w')
        out.write(text)
        out.close()

    # Returns the value after a searching a list of regex or None if nothing found.
    @staticmethod
    def try_list_of_regex(file_string, *regex):
        if len(regex) > 0:
            for i in regex:
                val = re.findall(file_string, i)
                if val:
                    return val
            return None
        else:
            return None

    @staticmethod
    def replace_value_of_tag(text, new_value):
        obj = objectify.fromstring(text)
        # noinspection PyProtectedMember
        obj.teiHeader.fileDesc.titleStmt.title._setText(new_value)
        return etree.tostring(obj.getroottree())

    def tag_headings(self):
        # load the DOM
        self.update_tmp_file(self.gv.TEI_FILE_PATH, self.gv.TEI_TEMP_FILE_PATH)
        tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

        iterator = 0

        # search the tree and grab the parent
        for child in tree.xpath("//tei:head", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            child.attrib['meTypesetHeadingID'] = str(iterator)
            iterator += 1

        tree.write(self.gv.TEI_FILE_PATH)

    # changes the parent element of the outer_xpath expression to the new_value
    def change_outer(self, outer_xpath, new_value, size_attribute):
        # load the DOM
        self.update_tmp_file(self.gv.TEI_FILE_PATH, self.gv.TEI_TEMP_FILE_PATH)
        tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

        # search the tree and grab the parent
        for child in tree.xpath(outer_xpath + "/..", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            child.tag = new_value
            child.attrib['meTypesetSize'] = size_attribute

        tree.write(self.gv.TEI_FILE_PATH)

    def move_size_div(self, heading_id, sibling_id):
        # load the DOM
        self.update_tmp_file(self.gv.TEI_FILE_PATH, self.gv.TEI_TEMP_FILE_PATH)
        tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

        source_node = tree.xpath(u'//tei:head[@meTypesetHeadingID=\'{0}\']/..'.format(str(heading_id)),
                                 namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        destination_node = tree.xpath(u'//tei:head[@meTypesetHeadingID=\'{0}\']/..'.format(str(sibling_id)),
                                      namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

        destination_node.addnext(source_node)

        tree.write(self.gv.TEI_FILE_PATH)

    def downsize_headings(self, root_size, size):
        # load the DOM
        self.update_tmp_file(self.gv.TEI_FILE_PATH, self.gv.TEI_TEMP_FILE_PATH)
        tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

        nodes_to_downsize = tree.xpath(u'//tei:head[@meTypesetSize=\'{0}\']'.format(str(size)),
                                       namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        for node_to_downsize in nodes_to_downsize:
            node_to_downsize.attrib['meTypesetSize'] = root_size

        tree.write(self.gv.TEI_FILE_PATH)

    def enclose(self, start_xpath, select_xpath):
        # load the DOM
        self.update_tmp_file(self.gv.TEI_FILE_PATH, self.gv.TEI_TEMP_FILE_PATH)
        tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

        node = tree.xpath(start_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        div = etree.Element('div')
        node.addprevious(div)

        self.debug.print_debug(self, 'Selecting for enclosure: {0}'.format(select_xpath))

        # search the tree and grab the elements
        child = tree.xpath(select_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        # move the elements
        for element in child:
            div.append(element)

        tree.write(self.gv.TEI_FILE_PATH)

    def run(self):
        self.update_tmp_file(self.gv.TEI_FILE_PATH, self.gv.TEI_TEMP_FILE_PATH)
        text = self.get_file_text(self.gv.TEI_TEMP_FILE_PATH)
        text = self.replace_value_of_tag(text, 'ssssssssss')
        self.write_output(self.gv.TEI_FILE_PATH, text)
        os.remove(self.gv.TEI_TEMP_FILE_PATH)



