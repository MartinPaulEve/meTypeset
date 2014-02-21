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


class TableClassifier(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Table Classifier')

    def replace_in_text(self, id, element):
        before_after = element.text.split(self.replace_text, 1)
        element.text = before_after[0]

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = unicode(id)
        new_element.attrib['ref-type'] = 'table'
        new_element.text = self.replace_text
        new_element.tail = ''.join(before_after[1:])

        element.append(new_element)

    def replace_in_tail(self, id, element):

        before_after = element.tail.split(self.replace_text, 1)

        new_element = etree.Element('xref')
        new_element.attrib['rid'] = unicode(id)
        new_element.attrib['ref-type'] = 'table'
        new_element.text = self.replace_text
        new_element.tail = ''.join(before_after[1:])

        element.getparent().insert(element.getparent().index(element) + 1, new_element)

        element.tail = before_after[0]

        return new_element

    def link(self, table_id, replace_texts, paragraphs):
        # this procedure is more complex than desirable because the content can appear between tags (like italic)
        # otherwise it would be a straight replace

        for paragraph in paragraphs:
            for replace_text in replace_texts:
                if replace_text in paragraph.text:
                    self.replace_in_text(table_id, paragraph)

                    self.debug.print_debug(self, u'Successfully linked {0} to {1}'.format(replace_text, table_id))
                    return

                for sub_element in paragraph:
                    if sub_element.tag != 'xref':
                        if replace_text in sub_element.text:
                            self.replace_in_text(table_id, sub_element)

                            self.debug.print_debug(self,
                                                   u'Successfully linked {0} to '
                                                   u'{1} from sub-element'.format(replace_text, table_id))
                            return

                    if sub_element.tail is not None and replace_text in sub_element.tail:
                        new_element = self.replace_in_tail(table_id, sub_element)

                        self.debug.print_debug(self,
                                               u'Successfully linked {0} to {1} from sub-tail'.format(replace_text,
                                                                                                      table_id))

                        return

    def run(self):
        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        tables = tree.xpath('//table-wrap')

        for table in tables:
            # get the next sibling
            p = table.getnext()

            if p.tag == 'p':
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
                        table.attrib = u'ID{0}'.format(unicode(uuid.uuid4()))

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)


def main():
    args = docopt(__doc__, version='meTypeset 0.1')
    bare_gv = GV(args)

    if args['--debug']:
        bare_gv.debug.enable_debug()

    table_classifier_instance = TableClassifier(bare_gv)
    table_classifier_instance.run()


if __name__ == '__main__':
    main()