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
        elements = ['abbrev', 'abstract', 'ack', 'address', 'aff', 'alt-text', 'app', 'app-group', 'array',
                    'article-title', 'attrib', 'author-comment', 'author-notes', 'award-group', 'bio', 'boxed-text',
                    'caption', 'chem-struct', 'chem-struct-wrap', 'col', 'colgroup', 'collab', 'compound-kwd',
                    'contrib', 'contrib-group', 'corresp', 'custom-meta', 'def', 'def-item', 'def-list', 'disp-formula',
                    'disp-formula-group', 'disp-quote', 'element-citation', 'ext-link', 'fig', 'fig-group', 'fn',
                    'fn-group', 'funding-source', 'glossary', 'glyph-data', 'graphic', 'inline-formula',
                    'inline-graphic', 'inline-supplementary-material', 'institution', 'kwd', 'kwd-group', 'list',
                    'list-item', 'long-desc', 'media', 'milestone-end', 'milestone-start', 'mixed-citation',
                    'named-content', 'nlm-citation', 'note', 'notes', 'p', 'person-group', 'preformat',
                    'product', 'ref', 'ref-list', 'related-article', 'related-object', 'response', 'sec', 'sig',
                    'sig-block', 'source', 'speech', 'statement', 'sub-article', 'supplementary-material', 'table',
                    'table-wrap', 'table-wrap-group', 'tbody', 'td', 'term', 'tex-math', 'tfoot', 'th', 'thead',
                    'title', 'tr', 'trans-abstract', 'trans-source', 'trans-title', 'trans-title-group', 'verse-group',
                    'xref']

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