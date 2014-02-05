__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from manipulate import Manipulate
from lxml import etree
import re


class NlmManipulate(Manipulate):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        self.dom_to_load = self.gv.nlm_file_path
        self.dom_temp_file = self.gv.nlm_temp_file_path
        self.namespaces = {'jats':'http://dtd.nlm.nih.gov/publishing/3.0/journalpublishing3.dtd',
                          'xmlns:xlink':'http://www.w3.org/1999/xlink'}
        self.mod_name = 'NLM'
        Manipulate.__init__(self, gv)


    @staticmethod
    def handle_nested_elements(iter_node, move_node, node, node_parent, outer_node, tag_name, tail_stack,
                               tail_stack_objects):
        while iter_node.tag != tag_name:
            tail_stack.append(iter_node.tag)
            tail_stack_objects.append(iter_node)
            iter_node = iter_node.getparent()

        # get the tail (of the comment) and style it
        append_location = None
        tail_text = node.tail
        iterator = 0
        tail_stack.reverse()
        tail_stack_objects.reverse()
        # rebuild the styled tree on a set of subelements
        for node_to_add in tail_stack:
            sub_element = etree.Element(node_to_add)
            if iterator == len(tail_stack) - 1:
                sub_element.text = node.tail

            if iterator == 0:
                outer_node = sub_element

            iterator += 1
            if append_location is None:
                tail_stack_objects[0].addnext(sub_element)
                append_location = sub_element
            else:
                append_location.append(sub_element)
                append_location = sub_element

        # remove the old node (this is in the element above)
        node.getparent().remove(node)
        # set the search node to the outermost node so that we can find siblings
        node_parent = iter_node
        node = outer_node
        move_node = True
        return move_node, node, node_parent

    @staticmethod
    def search_and_copy(last_node, move_node, nested_sibling, new_element, node, node_parent):
        append_location = new_element
        new_nodes_to_copy = node.xpath('following-sibling::node()')
        last_append = None
        for new_node in new_nodes_to_copy:
            if type(new_node) is etree._ElementStringResult or type(new_node) is etree._ElementUnicodeResult:
                if last_append is None:
                    last_append = append_location
                    if move_node:
                        node.tail = new_node
                        last_append.append(node)
                    else:
                        last_append.text = new_node
                else:
                    last_append.tail = new_node
            else:
                append_location.append(new_node)
                last_append = new_node
        if nested_sibling is None:
            node_parent.addnext(new_element)
            node_parent.tail = ''
            nested_sibling = new_element
        else:
            nested_sibling.addnext(new_element)
            nested_sibling = new_element

        # remove the original tail (all text after the line break, for example)
        # <!--meTypeset:br-->A third break <-- "a third break" is the tail
        if not move_node:
            node.tail = ''
            last_node = new_element
        else:
            last_node = None
        return last_node

    def process_node_for_tags(self, nested_sibling, node, search_xpath, tag_name):
        last_node = node
        new_element = etree.Element(tag_name)
        new_element.text = ''
        nodes_to_copy = node.xpath('//{0}/following-sibling::node()'.format(search_xpath))
        self.debug.print_debug(self, 'Found {0} nodes to copy: {1}'.format(len(nodes_to_copy),
                                                                           nodes_to_copy))
        #for element in nodes_to_copy:
        element = nodes_to_copy[0]
        # noinspection PyProtectedMember
        if not type(element) is etree._Element:
            if node.tail == element:
                # this should handle cases where a tag spans the break
                # for example: <p>Some text <italic>some italic text<!--meTypeset:br-->
                # more italic text</italic> more text</p>
                node_parent = node.getparent()
                iter_node = node_parent
                tail_stack = []
                tail_stack_objects = []
                move_node = False
                outer_node = None

                if node_parent.tag != tag_name:
                    # the element here is nested (bold etc), so we need to move the tail to be the tail of the
                    # outermost element and change "node" to be correct for its siblings to be the rest of
                    # the element. So we might find the last part is in italics and bold, so we build a list and
                    # iterate over it within the new copied element
                    move_node, node, node_parent = self.handle_nested_elements(iter_node, move_node, node,
                                                                               node_parent, outer_node, tag_name,
                                                                               tail_stack, tail_stack_objects)

                # search for all siblings and copy them into a new element below
                last_node = self.search_and_copy(last_node, move_node, nested_sibling, new_element, node,
                                                 node_parent)

            else:
                new_element.tail = node.tail
                node.tail = ''
        else:
            new_element.append(element)
        if not last_node is None:
            last_node.addnext(new_element)
            node.getparent().remove(node)

    @staticmethod
    def add_error_tag(node, error_number):
        rend = 'error-{0}'.format(error_number)

        if u'rend' in node.attrib:
            if not rend in node.attrib['rend']:
                # append the new value
                rend = u'{0} {1}'.format(node.attrib[u'rend'], rend)
            else:
                # just re-write the old value
                rend = node.attrib[u'rend']

        node.attrib[u'rend'] = rend

    def close_and_open_tag(self, search_xpath, tag_name):
        """
        Opens and closes an XML tag within a document. This is primarily useful when we have a marker such as
        meTypeset:br in comments which corresponds to no JATS/NLM equivalent. We use this function in certain
        behavioural modes to close the preceding paragraph and open the next.

        @param search_xpath: the node that serves as a marker
        @param tag_name: the tag name that will be open and closed
        """
        tree = self.load_dom_tree()

        initial_nodes = tree.xpath('//{0}//{1}'.format(tag_name, search_xpath))
        self.debug.print_debug(self, 'Found {0} {1} nodes on which to close and open tag {2}'.format(
            len(initial_nodes), search_xpath, tag_name))

        nested_sibling = None
        bail = False

        if len(initial_nodes) > 80 and int(self.gv.settings.args["--aggression"]) < 11:
            self.debug.print_debug(self, 'Bailing from replacement of tag {0} [limit exceeded]'.format(search_xpath))
            self.debug.write_error(self,
                                   'Bailing from replacement of tag {0} [limit exceeded]'.format(search_xpath),
                                   '001')
            bail = True

        if not bail:
            for node in initial_nodes:
                if not bail:
                    self.process_node_for_tags(nested_sibling, node, search_xpath, tag_name)
        else:
            # add an error tag to p elements where there are more than 3 comments within
            children = tree.xpath('//*[count(comment()[.="meTypeset:br"]) > 3]'.format(search_xpath))

            for child in children:
                self.add_error_tag(child, u'001')

        tree.write(self.dom_temp_file)
        tree.write(self.dom_to_load)

    def insert_break(self, search_xpath, tag_name):
        """
        Opens and closes an XML tag within a document. This is primarily useful when we have a marker such as
        meTypeset:br in comments which corresponds to no JATS/NLM equivalent. We use this function in certain
        behavioural modes to close the preceding paragraph and open the next.

        @param search_xpath: the node that serves as a marker
        @param tag_name: the tag name that will be open and closed
        """
        tree = self.load_dom_tree()

        initial_nodes = tree.xpath('//{0}//{1}'.format(tag_name,search_xpath))
        self.debug.print_debug(self, 'Found {0} {1} nodes on which to insert break: {2}'.format(
            len(initial_nodes), search_xpath, tag_name))

        for node in initial_nodes:
            break_element = etree.Element('break')
            node.addnext(break_element)
            node.getparent().remove(node)

        tree.write(self.dom_temp_file)
        tree.write(self.dom_to_load)

    def tag_inline_refs(self):
        tree = self.load_dom_tree()

        for paragraph in tree.xpath('//*//text()'):
            # tag numbered refs
            xref_paragraph_numbered = re.sub(r'(,|\[)([0-9]{1,3})(,|\])',
                                             r'\[<xref id="\2" ref-type="bibr">\2</xref>\]', paragraph)
            # tag authorname refs
            # first_author_list does not currently exist!

            # populate a dummy first_author_list for testing
            first_author_list = ['Eve']

            for authorname in first_author_list:
                match = re.match(r'(?P<before>.+?)\((?P<author>.*?' + authorname + r'.*?[^amp])(;|\))(?P<after>.+)',
                                 xref_paragraph_numbered)

                if match:
                    xref = etree.Element('xref', {'id':'INSERT ID HERE', 'ref-type':'bibr'})
                    xref.text = u'({0})'.format(match.group('author'))
                    xref.tail = match.group('after')

                    paragraph.getparent().text = match.group('before')
                    paragraph.getparent().insert(0, xref)


                    self.debug.print_debug(self, u'Inline reference handler detected and replaced '
                                                 u'{0}'.format(u'({0})'.format(match.group('author'))))

        tree.write(self.gv.nlm_file_path)

    def reflist_indent_method(self, tree):
        # tag the last item as a reference list
        indentmethod = tree.xpath('(//sec[title][disp-quote] | //sec[title][list])[last()]')
        if indentmethod:
            for item in indentmethod:
                item.attrib['reflist'] = 'yes'

    def reflist_year_match_method(self, tree):
        sections = tree.xpath('//sec')
        for element in sections:
            found_other = False
            found_one = False
            for p in element:
                if p.tag == 'p':
                    text = p.text

                    for sub_element in p:
                        text += sub_element.text
                        text += sub_element.tail

                    year_test = re.compile('((19|20)\d{2})|(n\.d\.)')

                    match = year_test.search(text)

                    if not match:
                        found_other = True
                        break
                    else:
                        found_one = True
                        p.attrib['rend'] = 'ref'

            if found_one and not found_other:
                element.attrib['reflist'] = 'yes'

    def find_or_create_element(self, tree, element_tag, add_xpath, is_sibling):
        # find_or_create_elements(tree, 'back', '//body', true)
        ret = None
        try:
            ret = tree.xpath(u'//' + element_tag, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
            self.debug.print_debug(self, u'Found existing {0}. Using it.'.format(element_tag))
        except:
            self.debug.print_debug(self, u'Unable to find an existing {0} element.'.format(element_tag))

        if ret is None:
            self.debug.print_debug(self, u'Creating new {0} element.'.format(element_tag))
            ret = tree.xpath(add_xpath)[0]
            new_element = etree.Element(element_tag)

            if is_sibling:
                ret.addnext(new_element)
            else:
                ret.append(new_element)

            ret = new_element

        return ret

    def find_reference_list(self):
        tree = self.load_dom_tree()

        # look for indents
        #self.reflist_indent_method(tree)

        # look for sections where very paragraph contains a year; likely to be a reference
        self.reflist_year_match_method(tree)

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

    def tag_bibliography_refs(self):
        tree = self.load_dom_tree()

        rid = 1

        self.find_or_create_element(tree, 'back', '//body', True)
        ref_list = self.find_or_create_element(tree, 'ref-list', '//back', False)

        # change this to find <ref-list> elements after we're more certain of how to identify them
        for refs in tree.xpath('//sec[@reflist="yes"]/p[@rend="ref"] | //sec[@reflist="yes"]/title '
                               '| //sec[@reflist="yes"]/*/list-item'):

            if refs.tag == 'title':
                self.debug.print_debug(self, 'Removing title element from reference item')
                refs.getparent().remove(refs)
            else:
                self.debug.print_debug(self, 'Tagging element "{0}" as reference item'.format(refs.tag))
                refs.tag = 'ref'
                refs.attrib['rid'] = str(rid)
                rid += 1
                ref_list.append(refs)

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)
