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
    def __init__(self):
        # read  command line arguments
        self.args = SettingsConfiguration.read_command_line()

        # absolute first priority is to initialize debugger so that anything triggered here can be logged
        self.debug = Debug()
        Debuggable.__init__(self, 'Globals')

        # read the configuaration
        self.settings_file_path = 'default'
        self.tei_file_path = None
        #SettingsConfiguration.setup_settings_file(self.args)
        #self.settings = SettingsConfiguration(self.get_settings_file(), self.args)

