#!/usr/bin/env python
"""tableclassfier: a tool to search for potential table titles and then link in-text entities

Usage:
   tableclassfier.py <input> [options]

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

        element.append(new_element)

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

                if replace_text in paragraph.text:
                    self.replace_in_text(table_id, paragraph, replace_text, ref_type)

                    self.debug.print_debug(self, u'Successfully linked {0} to {1}'.format(replace_text, table_id))

                for sub_element in paragraph:
                    if sub_element.tag != 'xref':
                        if replace_text in sub_element.text:
                            self.replace_in_text(table_id, sub_element, replace_text, ref_type)

                            self.debug.print_debug(self,
                                                   u'Successfully linked {0} to '
                                                   u'{1} from sub-element'.format(replace_text, table_id))

                    if sub_element.tail is not None and replace_text in sub_element.tail:
                        new_element = self.replace_in_tail(table_id, sub_element, replace_text, ref_type)

                        self.debug.print_debug(self,
                                               u'Successfully linked {0} to {1} from sub-tail'.format(replace_text,
                                                                                                      table_id))

    def run_graphics(self):
        # images are hard to handle because Word/OO puts them in different places
        # for instance, the caption can come before or after;
        # <p>Figure 1: Martin Eve at the pub<graphic xlink:href="media/image1.jpeg" position="float"
        # orientation="portrait" xlink:type="simple"/>

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        graphics = tree.xpath('//graphic')

        graphic_titles = []
        graphic_ids = []

        for graphic in graphics:

            # get the next sibling
            p = graphic.getparent()

            if p is not None and p.tag == 'p':
                text = manipulate.get_stripped_text(p)

                if len(text) < 140 and u':' in text:
                    # likely this is a caption identifier
                    split_title = text.split(':')

                    title = split_title[0]
                    caption = (''.join(split_title[1:])).strip()

                    self.debug.print_debug(self, u'Handling title and caption for "{0}"'.format(title))

                    title_element = None

                    # use an existing title element if one exists
                    try:
                        title_element = graphic.xpath('title')[0]
                    except:
                        title_element = etree.Element('title')
                        graphic.insert(0, title_element)

                    title_element.text = title

                    caption_element = etree.Element('caption')
                    caption_element.append(p)
                    graphic.insert(1, caption_element)

                    p.text = p.text.replace(': ', '')
                    p.text = p.text.replace(':', '')
                    p.text = p.text.replace(title, '')

                    if graphic.tail:
                        graphic.tail = graphic.tail.replace(': ', '')
                        graphic.tail = graphic.tail.replace(':', '')
                        graphic.tail = graphic.tail.replace(title, '')

                    if not 'id' in graphic.attrib:
                        graphic.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))

                    graphic_titles.append(title)
                    graphic_ids.append(graphic.attrib['id'])

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

    def run_tables(self):
        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        tables = tree.xpath('//table-wrap')

        table_titles = []
        table_ids = []

        for table in tables:
            # get the next sibling
            p = table.getnext()

            if p is not None and p.tag == 'p':
                text = manipulate.get_stripped_text(p)

                if len(text) < 140 and u':' in text:
                    # likely this is a table identifier
                    split_title = text.split(':')

                    title = split_title[0]
                    caption = (''.join(split_title[1:])).strip()

                    self.debug.print_debug(self, u'Handling title and caption for "{0}"'.format(title))

                    title_element = None

                    # use an existing title element if one exists
                    try:
                        title_element = table.xpath('title')[0]
                    except:
                        title_element = etree.Element('title')
                        table.insert(0, title_element)

                    title_element.text = title

                    caption_element = etree.Element('caption')
                    caption_element.append(p)
                    table.insert(1, caption_element)

                    p.text = p.text.replace(': ', '')
                    p.text = p.text.replace(':', '')
                    p.text = p.text.replace(title, '')

                    if not 'id' in table.attrib:
                        table.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))

                    table_titles.append(title)
                    table_ids.append(table.attrib['id'])

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
    table_classifier_instance.run_tables()


if __name__ == '__main__':
    main()