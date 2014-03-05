#!/usr/bin/env python
"""bibliographyclassfier.py: a tool to manipulate reference lists

Usage:
    bibliographyclassifier.py confirm <input> [options]

Options:
    -d, --debug                                     Enable debug output
    --interactive                                   Prompt the user to assist in interactive tagging
    -h, --help                                      Show this screen.
    -v, --version                                   Show version.
"""

from teimanipulate import *
from nlmmanipulate import *
from docopt import docopt
from bare_globals import GV
from interactive import Interactive

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that assists with bibliography classification.
"""

from debug import Debuggable


class BibliographyClassifier(Debuggable):

    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Bibliography Classifier')

    def linguistic_cues(self, manipulate, tree):
        language_list = self.gv.settings.get_setting('reference-languages', self).split(',')

        for language in language_list:
            with open ('{0}/language/ref_marker_{1}.txt'.format(self.gv.script_dir, language), 'r') as lang_file:
                lines = lang_file.read().split('\n')

                for line in lines:
                    manipulate.find_references_from_cue(line, tree)

    def run(self):
        if int(self.gv.settings.args['--aggression']) < int(self.gv.settings.get_setting('bibliographyclassifier', self,
                                                                                         domain='aggression')):
            self.debug.print_debug(self, u'Aggression level less than 4: exiting module.')
            return

        tei_manipulator = TeiManipulate(self.gv)

        tree = tei_manipulator.load_dom_tree()

        found = tei_manipulator.find_reference_list_in_word_list(tree)

        if not found:
            self.linguistic_cues(tei_manipulator, tree)

        tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]', 'back', 'div', 'type', 'bibliogr')

    def unconfirm(self, p, tree):
        # find a potential reference point

        old_reference_points = tree.xpath('//*[@meTypesetRender]')
        parent = False

        old_reference_point = None

        if len(old_reference_points) > 0:
            old_reference_point = old_reference_points[0]
            # determine if ref-list-before or ref-list-parent

            if old_reference_point.attrib['meTypesetRender'] == 'ref-list-parent':
                parent = True
        else:
            # get parent (ref-list)'s parent (back)'s previous sibling (sec)
            old_reference_point = tree.xpath('//sec[last()]')[0]
            parent = True

        if old_reference_point is not None:
            p.tag = 'p'
            if parent:
                Manipulate.append_safe(old_reference_point, p, self)
            else:
                old_reference_point.addnext(p)


    def handle_input(self, manipulate, opts, p, prompt, sel, tree, text):
        if sel == 'a':
            prompt.print_(u"Leaving interactive mode on user command")
            return "abort"
        elif sel == 'c':
            # confirm
            pass
        elif sel == 'o':
            # confirm all
            return "confirmall"
        elif sel == 'u':
            # delete the surrounding xref
            self.debug.print_debug(self, u'Unconfirming reference {0}'.format(text))
            self.unconfirm(p, tree)
            pass
        elif sel == 'n':
            # delete all
            self.debug.print_debug(self, u'Unconfirming reference {0}'.format(text))
            self.unconfirm(p, tree)
            return "delall"

    def run_prompt(self, interactive):
        if not interactive:
            self.debug.fatal_error(self, 'Cannot enter confirmation mode without interactive flag')

        prompt = Interactive(self.gv)

        opts = ('Confirm', 'Unconfirm', 'cOnfirm all', 'uNconfirm all', 'Abort')

        manipulate = NlmManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        ref_items = tree.xpath('//back/ref-list/ref')

        # note that we don't want to exit even if there are no references to link because the user may want to delete
        # some

        delete_all = False
        confirm_all = False

        for p in tree.xpath('//ref'):

            text = manipulate.get_stripped_text(p)

            sel = ''

            if delete_all:
                sel = 'u'
            elif confirm_all:
                sel = 'c'
            else:
                prompt.print_(u"Please confirm whether the following is a bibliographic reference: {0}".format(text))
                sel = prompt.input_options(opts)

            result = self.handle_input(manipulate, opts, p, prompt, sel, tree, text)

            if result == 'abort':
                return
            elif result == 'delall':
                delete_all = True
            elif result == 'confirmall':
                confirm_all = True

        manipulate.save_tree(tree)


def main():
    args = docopt(__doc__, version='meTypeset 0.1')
    bare_gv = GV(args)

    if args['--debug']:
        bare_gv.debug.enable_debug()

    bc_instance = BibliographyClassifier(bare_gv)

    if args['confirm']:
        bc_instance.run_prompt(args['--interactive'])

if __name__ == '__main__':
    main()