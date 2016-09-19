__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from manipulate import Manipulate
from lxml import etree
import re
import uuid


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

    def remove_reference_numbering(self):
        tree = self.load_dom_tree()

        for ref in tree.xpath('//ref'):
            if hasattr(ref, 'text') and ref.text is not None:
                text = ref.text

                ref.text = re.sub(r'^\d\d*\s*\.?\s*', r'', text)

        self.save_tree(tree)

    def remove_empty_elements(self, element):
        tree = self.load_dom_tree()

        for paragraph in tree.xpath(element):
            found = False
            text = self.get_stripped_text(paragraph).strip()

            if text == '':
                for item in paragraph:
                    if self.get_stripped_text(item) != '' or item.tag == 'graphic':
                        found = True
                        break
            else:
                found = True

            if not found and (paragraph.tail is None or paragraph.tail == ''):
                paragraph.getparent().remove(paragraph)
                self.save_tree(tree)
                self.debug.print_debug(self, u'Removed an empty element')
            elif not found and paragraph.tail != '':
                sibling = paragraph.getprevious()

                if sibling is None:
                    if paragraph.getparent().text is not None:
                        paragraph.getparent().text += paragraph.tail
                    else:
                        paragraph.getparent().text = paragraph.tail
                else:
                    sibling.tail = paragraph.tail

                paragraph.getparent().remove(paragraph)
                self.save_tree(tree)
                self.debug.print_debug(self, u'Removed an empty element but preserved tail')

        self.save_tree(tree)

    @staticmethod
    def handle_nested_elements(iter_node, move_node, node, node_parent, outer_node, tag_name, tail_stack,
                               tail_stack_objects):
        if iter_node is None:
            return None, None, None

        while iter_node.tag != tag_name:
            tail_stack.append(iter_node.tag)
            tail_stack_objects.append(iter_node)
            iter_node = iter_node.getparent()
            if iter_node is None:
                return None, None, None

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
                Manipulate.append_safe(append_location, sub_element, None)
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
                        Manipulate.append_safe(last_append, node, None)
                    else:
                        last_append.text = new_node
                else:
                    last_append.tail = new_node
            else:
                Manipulate.append_safe(append_location, new_node, None)
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

    def process_node_for_tags(self, nested_sibling, node, search_xpath, tag_name, new_tag='SAME'):
        if new_tag == 'SAME':
            new_tag = tag_name

        last_node = node
        new_element = etree.Element(new_tag)
        new_element.text = ''
        nodes_to_copy = node.xpath('//{0}/following-sibling::node()'.format(search_xpath))

        if len(nodes_to_copy) == 0:
            return

        self.debug.print_debug(self, u'Found {0} nodes to copy: {1}'.format(len(nodes_to_copy),
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
            Manipulate.append_safe(new_element, element, self)
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

    def close_and_open_tag_not_styled(self, search_xpath, tag_name):
        """
        Opens and closes an XML tag within a document. This is primarily useful when we have a marker such as
        meTypeset:br in comments which corresponds to no JATS/NLM equivalent. We use this function in certain
        behavioural modes to close the preceding paragraph and open the next.

        This variant only performs this action when the subsequent text does not look like a heading.

        @param search_xpath: the node that serves as a marker
        @param tag_name: the tag name that will be open and closed
        """
        tree = self.load_dom_tree()

        initial_nodes = tree.xpath('//{0}//{1}'.format(tag_name, search_xpath))
        self.debug.print_debug(self, u'Found {0} {1} nodes on which to close and open tag {2}'.format(
            len(initial_nodes), search_xpath, tag_name))

        nested_sibling = None
        bail = False

        if len(initial_nodes) > 80 and int(self.gv.settings.args["--aggression"]) < 11:
            self.debug.print_debug(self, u'Bailing from replacement of tag {0} [limit exceeded]'.format(search_xpath))
            self.debug.write_error(self,
                                   'Bailing from replacement of tag {0} [limit exceeded]'.format(search_xpath),
                                   '001')
            bail = True

        if not bail:
            for node in initial_nodes:
                sibling = node

                while sibling.getnext() is not None:
                    try:
                        if sibling.tag.endswith('bold'):
                            bail = True
                    except:
                        bail = True
                        break

                if not bail:
                    self.process_node_for_tags(nested_sibling, node, search_xpath, tag_name, 'p')
        else:
            # add an error tag to p elements where there are more than 3 comments within
            children = tree.xpath('//*[count(comment()[.="meTypeset:br"]) > 3]'.format(search_xpath))

            for child in children:
                self.add_error_tag(child, u'001')

        self.save_tree(tree)

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
        self.debug.print_debug(self, u'Found {0} {1} nodes on which to close and open tag {2}'.format(
            len(initial_nodes), search_xpath, tag_name))

        nested_sibling = None
        bail = False

        if len(initial_nodes) > 80 and int(self.gv.settings.args["--aggression"]) < 11:
            self.debug.print_debug(self, u'Bailing from replacement of tag {0} [limit exceeded]'.format(search_xpath))
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

        self.save_tree(tree)

    def save_tree(self, tree):
        tree.write(self.dom_temp_file, pretty_print=True)
        tree.write(self.dom_to_load, pretty_print=True)

    def find_text(self, paragraph, text):
        if paragraph.text and text in paragraph.text:
            return paragraph, False

        if paragraph.tail and text in paragraph.tail:
            return paragraph, True

        for sub_element in paragraph:
            ret, tail = self.find_text(sub_element, text)

            if ret is not None:
                return ret, tail

        return None, False

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
        self.debug.print_debug(self, u'Found {0} {1} nodes on which to insert break: {2}'.format(
            len(initial_nodes), search_xpath, tag_name))

        for node in initial_nodes:
            break_element = etree.Element('break')
            node.addnext(break_element)
            node.getparent().remove(node)

        self.save_tree(tree)

    def reflist_indent_method(self, tree):
        # tag the last item as a reference list
        indentmethod = tree.xpath('(//sec[title][disp-quote] | //sec[title][list])[last()]')
        if indentmethod:
            for item in indentmethod:
                item.attrib['reflist'] = 'yes'

    def reflist_year_match_method(self, tree, root, tolerance):
        sections = tree.xpath(root)

        # work upwards as the last section is most likely to contain references
        for element in reversed(sections):
            found_other = False
            count = 0
            use_tag = None
            diff_count = 0

            for p in element:
                # use either p or disp-quote, but not a mix
                if use_tag is None:
                    if p.tag == 'p' or p.tag == 'disp-quote' or p.tag == 'list-item':
                        use_tag = p.tag

                if p.tag == use_tag:
                    for sub_element in p:
                        if sub_element.tag == 'p':
                            p = sub_element
                            break

                    text = self.get_stripped_text(p)

                    year_test = re.compile('((18|19|20)\d{2}[a-z]?)|(n\.d\.)')

                    match = year_test.findall(text)

                    if not match:
                        blank_text = re.compile('XXXX')
                        match_inner = blank_text.findall(text)
                        if not match_inner:
                            diff_count += 1

                            if diff_count > tolerance:
                                self.debug.print_debug(self, u'Too many different non-year matches found in this'
                                                             u' {1} section to classify as a reference block. '
                                                             u'(Allowed: {0})'.format(tolerance, root))
                                found_other = True
                                break
                        elif len(match_inner) == 1:
                            count += 1
                            p.attrib['rend'] = 'ref'
                        else:
                            page_test = re.compile('(((18|19|20)\d{2})\-((18|19|20)\d{2}))')
                            is_page_range = page_test.search(text)

                            if not is_page_range:
                                self.debug.print_debug(self, u'More than one year match found in this {0}'.format(root))
                                found_other = True
                                break
                    elif len(match) == 1:
                        # only do this if we find 1 match on the line; otherwise, it's a problem
                        count += 1
                        p.attrib['rend'] = 'ref'
                    else:
                        page_test = re.compile('(((18|19|20)\d{2})\-((18|19|20)\d{2}))')
                        is_page_range = page_test.search(text)

                        if not is_page_range:
                            self.debug.print_debug(self, u'More than one year match found in this {0}'.format(root))
                            found_other = True
                            break

                elif p.tag != 'title' and not use_tag is None:
                    # found a tag other than the one we want or 'title'
                    diff_count += 1

                    if diff_count > tolerance:
                        self.debug.print_debug(self, u'Too many different elements found in this {1} section to '
                                                     u'classify as a reference block. (Allowed: {0})'.format(tolerance,
                                                                                                             root))
                        found_other = True
                        break

            if count > 1 and not found_other:
                self.debug.print_debug(self, u'Found a reference list in a {0} block with '
                                             u'tolerance {1}'.format(root, tolerance))
                while element.tag != 'sec':
                    element = element.getparent()

                element.attrib['reflist'] = 'yes'
                return True
            else:
                for p in element:
                    if 'rend' in p.attrib:
                        del p.attrib['rend']

        return False

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
                Manipulate.append_safe(ret, new_element, self)

            ret = new_element

        return ret

    def delete_special_lines(self):
        tree = self.load_dom_tree()

        special_regex = re.compile('^[\-\.\,\+\#\'\;\:]+$')

        to_remove = []

        for ref in tree.xpath('//p'):
            text = self.get_stripped_text(ref)

            if special_regex.match(text):
                ref.getparent().remove(ref)
                self.save_tree(tree)
                self.debug.print_debug(self, u'Removing special character line: {0}'.format(text))

    def clean_refs(self):
        tree = self.load_dom_tree()

        ref_regex = re.compile('^(?P<prelim>\s*\d+[\.\,]?\s+)(?P<reference>.+)')

        for ref in tree.xpath('//back/ref-list/ref'):
            if ref.text and ref_regex.match(ref.text):
                ref.text = ref_regex.sub('\\g<reference>', ref.text)
                self.save_tree(tree)
                self.debug.print_debug(self,
                                       u'Removing number/whitespace from start of reference: {0}'.format(ref.text))

        for ref in tree.xpath('//back/ref-list/ref[not(element-citation)]'):
            new_ref = etree.Element('ref')
            ref.addnext(new_ref)

            ref.tag = 'mixed-citation'
            new_ref.append(ref)

            if 'id' in ref.attrib:
                new_ref.attrib['id'] = ref.attrib['id']
                del ref.attrib['id']

        self.save_tree(tree)
        self.debug.print_debug(self, u'Encapsulated any loose refs inside mixed-citation blocks')

    def final_clean(self):
        self.delete_special_lines()
        self.handle_stranded_reference_titles_from_cues()
        self.clean_refs()
        self.remove_empty_elements('//fn-group')
        self.remove_empty_elements('//ref-list')

    def find_reference_list(self):
        if self.gv.used_list_method or self.gv.used_square_reference_method:
            return

        tree = self.load_dom_tree()

        # look for sections where very paragraph contains a year; likely to be a reference
        tags = ['//sec', '//sec/list']

        found = False

        for tag in tags:
            found = self.reflist_year_match_method(tree, tag, 0)

            if not found:
                found = self.reflist_year_match_method(tree, tag, 1)

            if not found:
                found = self.reflist_year_match_method(tree, tag, 2)

            if not found:
                found = self.reflist_year_match_method(tree, tag, 3)

        self.save_tree(tree)

    def handle_stranded_reference_titles_from_cues(self):
        # this method looks for paragraphs with one title element and nothing else whose text is in our
        # linguistic cues documents. It then removed them as superfluous.

        self.debug.print_debug(self, u'Checking for any stranded titles as a result of reference parsing')

        tree = self.load_dom_tree()

        xpath = '//sec[(count(p) = 0) and (count(title) = 1)]'

        language_list = self.gv.settings.get_setting('reference-languages', self).split(',')

        reference_terms = []

        for language in language_list:
            with open ('{0}/language/ref_marker_{1}.txt'.format(self.gv.script_dir, language), 'r') as lang_file:
                lines = lang_file.read().split('\n')

                for line in lines:
                    reference_terms.append(line.lower())

        for sections in tree.xpath(xpath):
            process = True
            for item in sections:
                if item.tag != 'title':
                    process = False

            if process:
                for item in sections:
                    text = self.get_stripped_text(item).strip()

                    if text.lower() in reference_terms:
                        sections.getparent().remove(sections)
                        self.save_tree(tree)
                        self.debug.print_debug(self, u'Removed a stranded title: {0}'.format(text))

    def fuse_references(self):
        tree = self.load_dom_tree()

        for ref in tree.xpath('//back/ref-list/ref'):
            text = self.get_stripped_text(ref)

            year_test = re.compile('((18|19|20)\d{2}[a-z]?)|(n\.d\.)')
            match = year_test.findall(text)

            if not match and ref.getprevious() is not None:
                ref.tag = 'REMOVE'
                ref.getprevious().append(ref)

                etree.strip_tags(tree, 'REMOVE')

                self.save_tree(tree)
                self.debug.print_debug(self, u'Appending {0} to previous ref'.format(text))

    def tag_bibliography_refs(self):

        tree = self.load_dom_tree()

        existing_refs = tree.xpath('//back/ref-list')

        if len(existing_refs) > 0:
            return

        self.find_or_create_element(tree, 'back', '//body', True)
        ref_list = self.find_or_create_element(tree, 'ref-list', '//back', False)

        # change this to find <reflist> elements after we're more certain of how to identify them
        for refs in tree.xpath('//sec[@reflist="yes"]/p[@rend="ref"] | //sec[@reflist="yes"]/title '
                               '| //sec[@reflist="yes"]/*/listitem/p[@rend="ref"] | '
                               '//sec[@reflist="yes"]/*/p[@rend="ref"]'):

            if refs.tag == 'title':
                self.debug.print_debug(self, u'Removing title element from reference item')
                refs.getparent().remove(refs)
            else:
                self.debug.print_debug(self, u'Tagging element "{0}" as reference item'.format(refs.tag))
                refs.tag = 'ref'
                refs.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))

                if 'rend' in refs.attrib:
                        del refs.attrib['rend']

                Manipulate.append_safe(ref_list, refs, self)

        self.save_tree(tree)