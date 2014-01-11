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

    def close_and_open_tag(self, search_xpath, tag_name):
        """
        Opens and closes an XML tag within a document. This is primarily useful when we have a marker such as
        meTypeset:br in comments which corresponds to no JATS/NLM equivalent. We use this function in certain
        behavioural modes to close the preceding paragraph and open the next.

        @param search_xpath: the node that serves as a marker
        @param tag_name: the tag name that will be open and closed
        """
        tree = self.load_dom_tree()

        initial_nodes = tree.xpath('//{0}'.format(search_xpath))
        self.debug.print_debug(self, 'Found {0} nodes on which to close and open tag: {1}'.format(
            len(initial_nodes), initial_nodes))

        nested_sibling = None

        for node in initial_nodes:
            last_node = node

            new_element = etree.Element(tag_name)
            new_element.text = ''

            nodes_to_copy = node.xpath('following-sibling::node()')
            self.debug.print_debug(self, 'Found {0} nodes on which to copy: {1}'.format(len(initial_nodes),
                                                                                        nodes_to_copy))

            for element in nodes_to_copy:
                # noinspection PyProtectedMember
                if not type(element) is etree._Element:
                    if node.tail == element:
                        # this should handle cases where a tag spans the break
                        # for example: <p>Some text <italic>some italic text<!--meTypeset:br-->
                        # more italic text</italic> more text</p>
                        self.debug.print_debug(self, 'Recursively handling nested search element: {0}'.format(node))

                        tail_stack = []

                        iter_node = node.getparent()
                        while iter_node.tag != tag_name:
                            tail_stack.append(iter_node.tag)
                            iter_node =  iter_node.getparent()

                        node_parent = iter_node

                        tail_stack.reverse()

                        append_location = new_element

                        for node_to_add in tail_stack:
                            sub_element = etree.Element(node_to_add)
                            append_location.append(sub_element)
                            append_location = sub_element

                        append_location.text = node.tail

                        if nested_sibling is None:
                            node_parent.addnext(new_element)
                            nested_sibling = new_element
                        else:
                            nested_sibling.addnext(new_element)
                            nested_sibling = new_element

                        # remove the original tail
                        node.tail = ''

                        last_node = new_element
                    else:
                        new_element.tail = node.tail
                        node.tail = ''
                else:
                    new_element.append(element)

            last_node.addnext(new_element)
            node.getparent().remove(node)

        tree.write(self.dom_temp_file)
        tree.write(self.dom_to_load)



