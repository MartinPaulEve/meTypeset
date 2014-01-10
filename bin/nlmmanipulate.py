__author__ = 'martin'

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from manipulate import Manipulate
from lxml import etree

class NlmManipulate(Manipulate):
    def __init__(self, gv):
        self.gv = gv
        self.module_name = "NLM"
        self.debug = self.gv.debug
        self.dom_to_load = self.gv.nlm_file_path
        self.dom_temp_file = self.gv.nlm_temp_file_path
        super(NlmManipulate, self).__init__(gv)

    def close_and_open_tag(self, search_xpath):
        tree = self.load_dom_tree()

        initial_nodes = tree.xpath('//{0}'.format(search_xpath))

        self.debug.print_debug(self, 'Found nodes: {0}'.format(initial_nodes))

        for node in initial_nodes:
            # ascertain the parent node type
            self.debug.print_debug(self, 'Found parent of node with type "{0}"'.format(node.getparent().tag))
            new_element = etree.Element(node.getparent().tag)
            new_element.text = ''

            nodes_to_copy = node.xpath('following-sibling::node()')
            print(nodes_to_copy)

            for element in nodes_to_copy:
                if not type(element) is etree._Element:
                    new_element.text += element
                else:
                    new_element.append(element)

            print (etree.tostring(new_element))

            node.getparent().addnext(new_element)

            # todo: remove the old nodes from the tree
            # see: http://hustoknow.blogspot.co.uk/2011/09/lxml-bug.html


        tree.write(self.dom_temp_file)
        tree.write(self.dom_to_load)



