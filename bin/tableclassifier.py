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


class TableClassifier(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Table Classifier')

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