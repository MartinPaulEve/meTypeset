#!/usr/bin/env python
from lxml import etree
from re import sub
import os
from manipulate import Manipulate

__author__ = "Martin Paul Eve, Dulip Withanage"
__email__ = "martin@martineve.com"


class TeiManipulate(Manipulate):
    def __init__(self, gv):
        self.gv = gv
        self.module_name = "TEI"
        self.debug = self.gv.debug
        self.dom_to_load = self.gv.tei_file_path
        self.dom_temp_file = self.gv.tei_temp_file_path
        super(TeiManipulate, self).__init__(gv)

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

    def change_wmf_image_links(self):
        tree = self.set_dom_tree(self.gv.tei_file_path)
        for imagelink in tree.xpath('//tei:graphic',namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            converted_imagelink = re.sub(r'\.wmf','.png',imagelink.xpath('@url')[0])
            imagelink.attrib['url'] = converted_imagelink
        tree.write(self.gv_tei_file_path)

    def run(self):
        self.update_tmp_file(self.gv.tei_file_path, self.gv.tei_temp_file_path)
        text = self.get_file_text(self.gv.tei_temp_file_path)
        text = self.replace_value_of_tag(text, 'ssssssssss')
        self.write_output(self.gv.tei_file_path, text)
        os.remove(self.gv.tei_temp_file_path)



