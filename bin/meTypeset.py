#!/usr/bin/env python
# @Author Dulip Withanage
# main file which triggers document parsing

"""meTypeset: text parsing library to convert word documents to xml formats NLM, TEI

Usage:
    meTypeset.py [(-d | --debug)] <input_file>  (-o | --output) <output_folder> [(-s | --settings) (<settings_file>)] [(-m | --metadata) (<metadata_file>)] [(-t | --test)]
    meTypeset.py (-h | --help)
    meTypeset.py (-t | --test)
    meTypeset.py --version

Options:

    -h --help  Show this screen.
    -t --test  Run the test suite.
    --version  Show version.
    -m --metadata  Metadata file
    -o --output   Output Folder

"""

import docx2tei
from docx2tei import *
from tei2nlm import *
from SizeClassifier import *
from FrontMatterParser import *
from docopt import docopt
from globals import *


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


class MeTypeset:
    def __init__(self):
        # read  command line arguments
        self.args = docopt(__doc__, version='meTypeset 0.1')
        # read settings file
        self.settings_file_path = 'default'
        self.setup_settings_file()
        self.settings = SettingsConfiguration(self.get_settings_file(), self.args)
        self.gv = GV(self.settings)
        self.debug = self.gv.debug
        self.module_name = "Main"

    def get_module_name(self):
        return self.module_name

    def set_metadata_file(self):
        metadata_file_arg = self.settings.args['<metadata_file>']
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

    def setup_debug(self):
        debug = self.args['--debug'] | self.args['-d']
        if debug:
            self.gv.debug.enable_debug()

        return debug

    def setup_settings_file(self):
        if '--settings' in self.args or '--s' in self.args:
            settings = self.args['--settings'] | self.args['-s']
            if settings:
                self.settings_file_path = self.args['<settings_file>']

    def run_modules(self):
        # check for stylesheets
        self.gv.check_file_exists(self.gv.docx_style_sheet_dir)
        # metadata file
        gv.metadata_file = self.set_metadata_file()
        # run docx to tei conversion
        Docx2TEI(self.gv).run()
        # run size classifier
        SizeClassifier(self.gv).run()
        # tei
        TeiManipulate(self.gv).run()
        # run tei to nlm conversion
        TEI2NLM(self.gv).run()

    def run(self):
        global test

        test = self.args['--test']
        debug = self.setup_debug()

        self.run_modules()

        if not debug:
            os.remove(self.gv.nlm_temp_file_path)


def main():
    me_typeset_instance = MeTypeset()
    me_typeset_instance.run()


if __name__ == '__main__':
    main()
