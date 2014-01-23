#!/usr/bin/env python
"""meTypeset: text parsing library to convert word documents to the JATS XML format

Usage:
    meTypeset.py docx <input> <output_folder> [options]
    meTypeset.py docxextracted <input> <output_folder> [options]
    meTypeset.py bibscan <input> [options]

Options:
    -d, --debug                                     Enable debug output
    -h, --help                                      Show this screen.
    -m <metadata_file>, --metadata <metadata_file>  Metadata file
    -s <settings_file>, --settings <settings_file>  Settings file
    -v, --version                                   Show version.

"""

__author__ = "Martin Paul Eve, Dulip Withnage"
__email__ = "martin@martineve.com"

import docx2tei
from docx2tei import *
from tei2nlm import *
from SizeClassifier import *
from FrontMatterParser import *
from docopt import docopt
from teimanipulate import TeiManipulate
from globals import *
from debug import Debuggable
from bibliographyAddins import BibliographyAddins
from bibliographydatabase import BibliographyDatabase
from listclassifier import ListClassifier
from metadata import Metadata


# check whether lxml is installed
try:
    # noinspection PyUnresolvedReferences
    from lxml import etree
except ImportError:
    print("Failed to import lxml")


class SettingsConfiguration:
    def __init__(self, set_file, args):
        tree = etree.parse(set_file)
        self.tree = tree
        self.script_dir = os.environ['METYPESET']
        self.args = args
        self.settings_file = set_file


class MeTypeset (Debuggable):
    def __init__(self):
        # read  command line arguments
        self.args = docopt(__doc__, version='meTypeset 0.1')

        # absolute first priority is to initialize debugger so that anything triggered here can be logged
        self.debug = Debug()

        if self.args['--debug']:
            self.debug.enable_debug()

        # read settings file
        self.settings_file_path = 'default'
        self.tei_file_path = None
        self.setup_settings_file()
        self.settings = SettingsConfiguration(self.get_settings_file(), self.args)
        self.gv = GV(self.settings, self.debug)
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Main')

    def set_metadata_file(self):
        metadata_file_arg = self.settings.args['--metadata']
        if metadata_file_arg:
            metadata_file = self.gv.clean_path(self.gv.concat_path(self.settings.script_dir, metadata_file_arg[0]))
        else:
            metadata_file = self.gv.clean_path(self.gv.concat_path(self.settings.script_dir,
                                                                   self.gv.value_for_tag(self.settings,
                                                                                         'default-metadata-file-path')))

            self.debug.print_debug(self, 'Metadata file wasn\'t specified. '
                                         'Falling back to {0}'.format(metadata_file))

        return metadata_file

    def check_settings_file_exists(self, set_file):
        # noinspection PyBroadException
        try:
            os.path.isfile(set_file)
        except:
            self.debug.fatal_error(self, 'Settings file {0} does not exist'.format(set_file))

    def get_settings_file(self):

        # read  the home folder, either from the path or from the settings file
        # noinspection PyBroadException
        try:
            script_dir = os.environ['METYPESET']

        except:
            # noinspection PyBroadException
            try:
                mod_path = os.path.dirname(docx2tei.__file__)
                script_dir = os.path.dirname(mod_path + '/../')
                os.environ['METYPESET'] = script_dir

            except:
                self.debug.fatal_error(self, '$METYPESET path not variable is not set '
                                             'and/or was unable to determine runtime path.')

                script_dir = "NONPATH"

        if self.settings_file_path == 'default':
            if script_dir != '':
                set_file = '{0}/bin/settings.xml'.format(script_dir)
                self.check_settings_file_exists(set_file)
            else:
                    set_file = 'NOFILE'
                    pass
        else:
            set_file = self.settings_file_path
            self.check_settings_file_exists(set_file)

        return set_file

    def setup_settings_file(self):
        if '--settings' in self.args:
            settings = self.args['--settings']
            if settings:
                self.settings_file_path = self.args['--settings']

    def run_modules(self):
        if self.args['bibscan']:

            BibliographyDatabase(self.gv).scan()
        else:
            # check for stylesheets
            self.gv.check_file_exists(self.gv.docx_style_sheet_dir)
            # metadata file
            gv.metadata_file = self.set_metadata_file()

            if self.args['docx']:
                # run docx to tei conversion
                Docx2TEI(self.gv).run(True)
            else:
                self.debug.print_debug(self, 'Skipping docx extraction')
                Docx2TEI(self.gv).run(False)

            # run size classifier
            SizeClassifier(self.gv).run()

            # run list classifier
            ListClassifier(self.gv).run()

            # run bibliographic addins handler
            BibliographyAddins(self.gv).run()

            # tei
            TeiManipulate(self.gv).run()

            # run tei to nlm conversion
            TEI2NLM(self.gv).run()

            # run metadata merge
            Metadata(self.gv).run()

    def run(self):
        self.run_modules()

        if not self.debug:
            os.remove(self.gv.nlm_temp_file_path)


def main():
    me_typeset_instance = MeTypeset()
    me_typeset_instance.run()


if __name__ == '__main__':
    main()
