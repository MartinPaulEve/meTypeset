#!/usr/bin/env python
"""meTypeset: text parsing library to convert word documents to the JATS XML format

Usage:
    meTypeset.py docx <input> <output_folder> [options]
    meTypeset.py docxextracted <input> <output_folder> [options]
    meTypeset.py bibscan <input> [options]

Options:
    -a, --aggression <aggression_level>             Parser aggression level 0-10 [default: 10]
    --chain <xslt>                                  Specify a subsequent XSL transform to pass the NLM to
    -c, --clean                                     Produce final XML, not intermediate markup with additional metadata
    -d, --debug                                     Enable debug output
    -i, --identifiers                               Generate unique identifiers for all supported NLM elements
    --interactive                                   Enable step-by-step interactive mode
    -h, --help                                      Show this screen.
    -m, --metadata <metadata_file>                  Metadata file
    --purenlm                                       Die after performing NLM XSLT step
    --puretei                                       Die after performing TEI XSLT step
    --prettytei                                     Indent and format intermediary TEI
    -p, --proprietary                               Enables proprietary math parsing. Requires omml2mml.xsl
    -s, --settings <settings_file>                  Settings file
    -v, --version                                   Show version.

"""

__author__ = "Martin Paul Eve, Dulip Withnage"
__email__ = "martin@martineve.com"

import docxtotei
from docxtotei import *
from teitonlm import *
from sizeclassifier import *
from frontmatterparser import *
from docopt import docopt
from teimanipulate import TeiManipulate
from globals import *
from debug import Debuggable
from bibliographyaddins import BibliographyAddins
from bibliographydatabase import BibliographyDatabase
from bibliographyclassifier import BibliographyClassifier
from listclassifier import ListClassifier
from metadata import Metadata
from referencelinker import ReferenceLinker
from xslchainer import XslChain
from settingsconfiguration import Settings
from idgenerator import IdGenerator
from captionclassifier import CaptionClassifier
from complianceenforcer import ComplianceEnforcer
from interactive import Interactive


# check whether lxml is installed
try:
    # noinspection PyUnresolvedReferences
    from lxml import etree
except ImportError:
    print("Failed to import lxml")


class MeTypeset (Debuggable):
    def __init__(self):
        # read  command line arguments
        self.args = self.read_command_line()

        # absolute first priority is to initialize debugger so that anything triggered here can be logged
        self.debug = Debug()

        Debuggable.__init__(self, 'Main')

        if self.args['--debug']:
            self.debug.enable_debug()

        # read settings file
        self.settings_file_path = 'default'
        self.tei_file_path = None
        self.settings_file_path = Settings.setup_settings_file(self.args)
        self.settings = Settings(Settings.get_settings_file(self, self.settings_file_path),
                                              self.args)
        self.gv = GV(self.settings, self.debug)

        self.debug.enable_prompt(Interactive(self.gv))

    @staticmethod
    def read_command_line():
        return docopt(__doc__, version='meTypeset 0.1')

    def set_metadata_file(self):
        metadata_file_arg = self.settings.args['--metadata']
        if metadata_file_arg:
            metadata_file = self.gv.settings.clean_path(self.gv.concat_path(self.settings.script_dir,
                                                                            metadata_file_arg[0]))
        else:
            metadata_file = \
                self.gv.settings.clean_path(
                    self.gv.settings.concat_path(self.settings.script_dir,
                                                 self.gv.settings.get_setting('default-metadata-file-path',
                                                                                self)))

            self.debug.print_debug(self, u'Metadata file wasn\'t specified. '
                                         'Falling back to {0}'.format(metadata_file))

        return metadata_file

    def run_modules(self):
        ag = int(self.gv.settings.args['--aggression'])
        self.debug.print_debug(self,
                               u'Running at aggression level {0} {1}'.format(ag,
                                                                             "[grrr!]" if ag == 10 else ""))

        if ag > 10:
            self.debug.print_debug(self, "WARNING: safety bail-out features are disabled at aggression level 11")

        if self.args['bibscan']:

            BibliographyDatabase(self.gv).scan()
        else:
            # check for stylesheets
            self.gv.check_file_exists(self.gv.docx_style_sheet_dir)
            # metadata file
            gv.metadata_file = self.set_metadata_file()

            if self.args['docx']:
                # run docx to tei conversion
                # includes hooks for proprietary transforms if enabled
                DocxToTei(self.gv).run(True, self.args['--proprietary'])
            else:
                self.debug.print_debug(self, u'Skipping docx extraction')
                DocxToTei(self.gv).run(False, self.args['--proprietary'])

            if self.args['--puretei']:
                self.debug.print_debug(self, u'Exiting as TEI transform complete')
                return

            metadata = Metadata(self.gv)
            metadata.pre_clean()

            # run bibliographic addins handler
            # aggression 4
            found_bibliography = BibliographyAddins(self.gv).run()

            # run list classifier
            # aggression 4
            ListClassifier(self.gv).run()

            bibliography_classifier = BibliographyClassifier(self.gv)

            if not found_bibliography:
                # run bibliographic classifier
                # aggression 4
                bibliography_classifier.run()

            # tei
            # aggression 3
            TeiManipulate(self.gv).run()

            # run size classifier
            # aggression 5
            SizeClassifier(self.gv).run()

            # run tei to nlm conversion
            TeiToNlm(self.gv).run(not found_bibliography)

            if self.gv.settings.args['--purenlm']:
                self.debug.print_debug(self, u'Exiting as NLM transform complete')
                return

            manipulate = NlmManipulate(self.gv)

            if not self.gv.used_list_method:
                manipulate.fuse_references()

            # run reference linker
            rl = ReferenceLinker(self.gv)
            rl.run(self.args['--interactive'])
            rl.cleanup()

            # run table classifier
            cc = CaptionClassifier(self.gv)
            if int(self.args['--aggression']) > int(self.gv.settings.get_setting('tablecaptions',
                                                                                 self, domain='aggression')):
                cc.run_tables()

            if int(self.args['--aggression']) > int(self.gv.settings.get_setting('graphiccaptions',
                                                                                 self, domain='aggression')):
                cc.run_graphics()

            # run metadata merge
            metadata.run()

            if self.args['--interactive']:
                bibliography_classifier.run_prompt(True)

            # process any bibliography entries that are possible
            BibliographyDatabase(self.gv).run()

            # remove stranded titles and cleanup
            manipulate.final_clean()

            if self.args['--identifiers']:
                IdGenerator(self.gv).run()

            if self.args['--chain']:
                # construct and run an XSLT chainer
                XslChain(self.gv).run()

            if self.args['--clean']:
                ComplianceEnforcer(self.gv).run()

    def run(self):
        self.run_modules()

        if not self.debug:
            os.remove(self.gv.nlm_temp_file_path)


def main():
    me_typeset_instance = MeTypeset()
    me_typeset_instance.run()


if __name__ == '__main__':
    main()
