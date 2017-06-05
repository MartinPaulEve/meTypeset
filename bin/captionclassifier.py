#!/usr/bin/env python
"""captionclassfier: a tool to search for potential table titles and then link in-text entities

Usage:
   captionclassfier.py tables <input> [options]
   captionclassfier.py graphics <input> [options]
   captionclassfier.py all <input> [options]

Options:
    -d, --debug                                     Enable debug output
    -h, --help                                      Show this screen.
    -v, --version                                   Show version.

"""

from docopt import docopt
from bare_globals import GV
from debug import Debuggable
from nlmmanipulate import NlmManipulate
from lxml import etree
import uuid
import re
import editdistance


class CaptionClassifier(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Caption Classifier')

    def replace_in_text(self, id, element, replace_text, ref_type):
        before_after = element.text.split(replace_text, 1)
        element.text = before_after[0]

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = unicode(id)
        new_element.attrib['ref-type'] = ref_type
        new_element.text = replace_text
        new_element.tail = ''.join(before_after[1:])

        NlmManipulate.append_safe(element, new_element, self)

    def replace_in_tail(self, id, element, replace_text, ref_type):

        before_after = element.tail.split(replace_text, 1)

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = unicode(id)
        new_element.attrib['ref-type'] = ref_type
        new_element.text = replace_text
        new_element.tail = ''.join(before_after[1:])

        element.getparent().insert(element.getparent().index(element) + 1, new_element)

        element.tail = before_after[0]

        return new_element

    def link(self, table_ids, replace_texts, paragraphs, ref_type):
        # this procedure is more complex than desirable because the content can appear between tags (like italic)
        # otherwise it would be a straight replace

        for paragraph in paragraphs:
            for replace_text in replace_texts:
                table_id = table_ids[replace_texts.index(replace_text)]

                if paragraph.text is not None and replace_text in paragraph.text:
                    self.replace_in_text(table_id, paragraph, replace_text, ref_type)

                    self.debug.print_debug(self, u'Successfully linked {0} to {1}'.format(replace_text, table_id))

                for sub_element in paragraph:
                    if sub_element.tag != 'xref':
                        if sub_element.text and replace_text in sub_element.text:
                            self.replace_in_text(table_id, sub_element, replace_text, ref_type)

                            self.debug.print_debug(self,
                                                   u'Successfully linked {0} to '
                                                   u'{1} from sub-element'.format(replace_text, table_id))

                    if sub_element.tail is not None and replace_text in sub_element.tail:
                        new_element = self.replace_in_tail(table_id, sub_element, replace_text, ref_type)

                        self.debug.print_debug(self,
                                               u'Successfully linked {0} to {1} from sub-tail'.format(replace_text,
                                                                                                      table_id))

    def run_graphics_sibling(self):
        # images are hard to handle because Word/OO puts them in different places
        # for instance, the caption can come before or after;
        # <p>Figure 1: Martin Eve at the pub<graphic xlink:href="media/image1.jpeg" position="float"
        # orientation="portrait" xlink:type="simple"/>

        self.debug.print_debug(self, u'Attempting to classify captions for graphics objects [sibling]')

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        graphics = tree.xpath('//graphic')

        graphic_titles = []
        graphic_ids = []
        graphic_regex_dot = re.compile('^.+?\s*\d+\..+')
        graphic_regex_colon = re.compile('^.+?\s*\d+\:.+')

        separator = ':'

        for graphic in graphics:
            use_next = False
            use_previous = False

            # get the next sibling
            p = graphic.getparent().getnext()
            pprev = graphic.getparent().getprevious()

            if p is not None and p.tag == 'p':
                text = manipulate.get_stripped_text(p)

                if graphic_regex_colon.match(text):
                    use_next = True
                    separator = ':'
                elif graphic_regex_dot.match(text):
                    use_next = True
                    separator = '.'

            if not use_next:
                if pprev is not None and pprev.tag == 'p':
                    text = manipulate.get_stripped_text(pprev)

                    if graphic_regex_colon.match(text):
                        use_previous = True
                        separator = ':'
                    elif graphic_regex_dot.match(text):
                        use_previous = True
                        separator = '.'

            if not use_next or use_previous:
                # see if the title in this section potentially contains text we can match
                parent = graphic.getparent()

                while parent is not None and not parent.tag.endswith('sec'):
                    parent = parent.getparent()
                    if parent is not None:
                        titles = parent.xpath('title')
                    else:
                        titles = []

                if len(titles) > 0:
                    p = titles[0]

                    text = manipulate.get_stripped_text(p)

                    if graphic_regex_colon.match(text):
                        use_next = True
                        separator = ':'
                    elif graphic_regex_dot.match(text):
                        use_next = True
                        separator = '.'

            if use_next or use_previous:

                if use_next:
                    text = manipulate.get_stripped_text(p)
                else:
                    text = manipulate.get_stripped_text(pprev)
                    p = pprev

                # likely this is a table identifier
                split_title = text.split(separator)

                title = split_title[0].strip()
                caption = (''.join(split_title[1:])).strip()

                self.debug.print_debug(self, u'Handling title and caption for "{0}"'.format(title))

                title_element = None

                # use an existing title element if one exists
                try:
                    title_element = graphic.xpath('label')[0]
                except:
                    title_element = etree.Element('label')
                    graphic.insert(0, title_element)

                title_element.text = title

                caption_element = etree.Element('caption')
                new_p = etree.Element('p')
                new_p.text = caption

                NlmManipulate.append_safe(caption_element, new_p, self)
                NlmManipulate.append_safe(graphic, caption_element, self)

                if p.tag.endswith('title'):
                    new_title = etree.Element('title')
                    new_title.text = ''
                    p.addnext(new_title)
                    p.getparent().remove(p)
                else:
                    p.getparent().remove(p)

                if graphic.tail:
                    graphic.tail = graphic.tail.replace(title + separator, '')
                    graphic.tail = graphic.tail.replace(caption + separator, '')
                    graphic.tail = graphic.tail.replace(caption, '')

                if not 'id' in graphic.attrib:
                    graphic.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))

                graphic_titles.append(title)
                graphic_ids.append(graphic.attrib['id'])

        paragraphs = tree.xpath('//p')

        self.link(graphic_ids, graphic_titles, paragraphs, 'fig')

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

    def run_graphics(self):
        # images are hard to handle because Word/OO puts them in different places
        # for instance, the caption can come before or after;
        # <p>Figure 1: Martin Eve at the pub<graphic xlink:href="media/image1.jpeg" position="float"
        # orientation="portrait" xlink:type="simple"/>

        self.debug.print_debug(self, u'Attempting to classify captions for graphics objects [plain]')

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        graphics = tree.xpath('//graphic')

        graphic_titles = []
        graphic_ids = []
        graphic_regex_dot = re.compile('^.+?\s*\d+\..+')
        graphic_regex_colon = re.compile('^.+?\s*\d+\:.+')

        separator = ':'

        for graphic in graphics:
            use_next = False

            # get the next sibling
            p = graphic.getparent()

            if p is not None and p.tag == 'p':
                text = manipulate.get_stripped_text(p)

                if graphic_regex_colon.match(text):
                    use_next = True
                    separator = ':'
                elif graphic_regex_dot.match(text):
                    use_next = True
                    separator = '.'

            if use_next:
                text = manipulate.get_stripped_text(p)

                # likely this is a table identifier
                split_title = text.split(separator)

                title = split_title[0].strip()
                caption = (''.join(split_title[1:])).strip()

                self.debug.print_debug(self, u'Handling title and caption for "{0}"'.format(title))

                title_element = None

                # use an existing title element if one exists
                try:
                    title_element = graphic.xpath('label')[0]
                except:
                    title_element = etree.Element('label')
                    graphic.insert(0, title_element)

                title_element.text = title

                caption_element = etree.Element('caption')
                new_p = etree.Element('p')
                new_p.text = caption

                NlmManipulate.append_safe(caption_element, new_p, self)
                NlmManipulate.append_safe(graphic, caption_element, self)

                if graphic.tail:
                    graphic.tail = graphic.tail.replace(title + separator, '')
                    graphic.tail = graphic.tail.replace(caption + separator, '')
                    graphic.tail = graphic.tail.replace(caption, '')

                if not 'id' in graphic.attrib:
                    graphic.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))

                graphic_titles.append(title)
                graphic_ids.append(graphic.attrib['id'])

        paragraphs = tree.xpath('//p')

        self.link(graphic_ids, graphic_titles, paragraphs, 'fig')

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

        self.run_graphics_sibling()

    def run_tables(self):
        self.debug.print_debug(self, u'Attempting to classify captions for table objects')

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        tables = tree.xpath('//table-wrap')

        table_titles = []
        table_ids = []
        table_regex_dot = re.compile('^.+?[\s\-]*\d+\..+')
        table_regex_colon = re.compile('^.+?[\s\-]*\d+\:.+')
        caption_element = None

        separator = ':'

        for table in tables:
            use_next = False
            use_previous = False
            used_title = False

            # get the next sibling
            p = table.getnext()
            pprev = table.getprevious()
            old_title = None

            if p is not None and p.tag == 'p':
                cont = True
                for sub in p:
                    if sub.tag == 'graphic':
                        cont = False

                if cont:
                    text = manipulate.get_stripped_text(p)

                    if table_regex_colon.match(text):
                        use_next = True
                        separator = ':'
                    elif table_regex_dot.match(text):
                        use_next = True
                        separator = '.'

            if not use_next:
                cont = True
                for sub in pprev:
                    if sub.tag == 'graphic':
                        cont = False
                if cont:
                    if pprev is not None and pprev.tag == 'p':
                        text = manipulate.get_stripped_text(pprev)

                        if table_regex_colon.match(text):
                            use_previous = True
                            separator = ':'
                        elif table_regex_dot.match(text):
                            use_previous = True
                            separator = '.'

            if not use_next or use_previous:
                # see if the title in this section potentially contains text we can match
                parent = table.getparent()

                titles = parent.xpath('title')

                if len(titles) > 0:
                    p = titles[0]

                    text = manipulate.get_stripped_text(p)

                    if table_regex_colon.match(text):
                        use_next = True
                        separator = ':'
                        used_title = True
                    elif table_regex_dot.match(text):
                        use_next = True
                        separator = '.'
                        used_title = True

            if use_next or use_previous:

                if use_next:
                    text = manipulate.get_stripped_text(p)
                else:
                    text = manipulate.get_stripped_text(pprev)
                    p = pprev

                # likely this is a table identifier
                split_title = text.split(separator)

                title = split_title[0]
                caption = (''.join(split_title[1:])).strip()

                # strip all formatting from caption for ease of parsing
                # TODO: preserve formatting (far harder)
                new_p = etree.Element('p')
                new_p.text = caption

                if p.tag.endswith('title'):
                    new_title = etree.Element('title')
                    new_title.text = ''
                    old_title = new_title
                    p.addnext(new_title)
                    p.getparent().remove(p)
                else:
                    p.getparent().remove(p)

                p = new_p

                self.debug.print_debug(self, u'Handling title and caption for "{0}"'.format(title))

                title_element = None

                # use an existing title element if one exists
                try:
                    title_element = table.xpath('label')[0]
                except:
                    title_element = etree.Element('label')
                    table.insert(0, title_element)

                title_element.text = title

                caption_element = etree.Element('caption')
                NlmManipulate.append_safe(caption_element, p, self)
                table.insert(1, caption_element)

                if not 'id' in table.attrib:
                    table.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))

                table_titles.append(title)
                table_ids.append(table.attrib['id'])

                if used_title:
                    # if we took the title out, then we should move the parent into its previous sibling and then
                    # strip tags
                    old_title.tag = 'REMOVE'

                    etree.strip_elements(tree, 'REMOVE')

                    section = table.getparent()

                    previous = section.getprevious()

                    while previous is not None and not previous.tag.endswith('sec'):
                        previous = previous.getprevious()

                    if previous is not None:
                        previous.append(section)
                        section.tag = 'REMOVE'

                        etree.strip_tags(tree, 'REMOVE')

                        self.debug.print_debug(self, u'Moved table and siblings to previous section')
                    else:
                        previous = section.getparent()

                        if previous is not None and previous.tag.endswith('sec'):
                            previous.append(section)
                            section.tag = 'REMOVE'

                            etree.strip_tags(tree, 'REMOVE')

                            self.debug.print_debug(self, u'Moved table and siblings to parent section')

            # If none of that worked, try to find caption in table rows
            if caption_element is None:
                table_rows = table.find("table").getchildren()

                # Check if first row has fewer columns than others
                # Therefore not likely to be data or a header
                columns_count = {}
                first_column = {}
                row_number = 0

                for row in table_rows:
                    row_number += 1
                    columns_count[row_number] = len(row.getchildren())
                    first_column[row_number] = row.getchildren()[0].text
                    fewest_columns = min(columns_count, key=columns_count.get)

                if columns_count[1] == fewest_columns and columns_count[2] != fewest_columns:
                    # If it has fewest columns, also check Levenshtein distance
                    if editdistance.eval(first_column[1], first_column[2]) > editdistance.eval(first_column[2], first_column[3]):

                        # OK, we have something, move it
                        caption_element = etree.Element('caption')
                        caption_element.text = first_column[1]
                        NlmManipulate.append_safe(table, caption_element, self)
                        table.find("table").remove(table_rows[0])


        paragraphs = tree.xpath('//p')

        self.link(table_ids, table_titles, paragraphs, 'table')

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)


def main():
    args = docopt(__doc__, version='meTypeset 0.1')
    bare_gv = GV(args)

    if args['--debug']:
        bare_gv.debug.enable_debug()

    table_classifier_instance = CaptionClassifier(bare_gv)

    if args['all'] or args['tables']:
        table_classifier_instance.run_tables()

    if args['all'] or args['graphics']:
        table_classifier_instance.run_graphics()


if __name__ == '__main__':
    main()