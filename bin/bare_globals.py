__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A pared down globals class for non-transform launches

"""

from debug import *
from lxml import *
import os
import docopt
from settingsconfiguration import SettingsConfiguration


class GV (Debuggable):
    def __init__(self, args):
        # read  command line arguments
        self.args = args

        # absolute first priority is to initialize debugger so that anything triggered here can be logged
        self.debug = Debug()
        Debuggable.__init__(self, 'Globals')

        # read the configuration
        self.settings_file_path = 'default'
        self.tei_file_path = None
        SettingsConfiguration.setup_settings_file(self.args)
        self.settings = SettingsConfiguration(SettingsConfiguration.get_settings_file(self, self.settings_file_path),
                                              self.args)

        self.input_file_path = self.settings.args['<input>'].strip()

        self.nlm_file_path = self.input_file_path
        self.nlm_temp_file_path = self.input_file_path + '.tmp'

        self.settings.args['--aggression'] = 11

        self.database_file_path = \
            self.settings.clean_path(self.settings.concat_path(os.path.join(self.settings.script_dir,
                                                                            'database'),
                                                               self.settings.value_for_tag(self.settings,
                                                                                           'databasefile',
                                                                                           self)))
