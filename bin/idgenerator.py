#!/usr/bin/env python
"""idgenerator: a tool to append an ID to all elements in an NLM XML file

Usage:
    idgenerator.py <input> [options]

Options:
    -d, --debug                                     Enable debug output
    -h, --help                                      Show this screen.
    -v, --version                                   Show version.

"""

from debug import Debuggable
from nlmmanipulate import NlmManipulate
import uuid
from bare_globals import GV
from docopt import docopt

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

class IdGenerator(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'ID Generator')

    def run(self):
        elements = ['p', 'title', 'sec', 'disp-quote', 'ref', 'ref-list', 'fn', 'table', 'xref', 'graphic', 'caption']

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        for element in elements:
            self.debug.print_debug(self, u'Assigning ID to all {0} elements'.format(element))
            for item in tree.xpath(u'//{0}'.format(element)):
                if not 'id' in item.attrib:
                    item.attrib['id'] = u'ID{0}'.format(unicode(uuid.uuid4()))

        tree.write(self.gv.nlm_file_path)
        tree.write(self.gv.nlm_temp_file_path)

def main():
    args = docopt(__doc__, version='meTypeset 0.1')
    bare_gv = GV(args)

    if args['--debug']:
        bare_gv.debug.enable_debug()

    id_gen_instance = IdGenerator(bare_gv)
    id_gen_instance.run()


if __name__ == '__main__':
    main()