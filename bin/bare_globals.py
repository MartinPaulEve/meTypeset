__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A pared down globals class for non-transform launches

"""

from debug import *
from lxml import *
import os
import docopt
from meTypeset import MeTypeset


class SettingsConfiguration:
    def __init__(self, set_file, args):
        tree = etree.parse(set_file)
        self.tree = tree
        self.script_dir = os.environ['METYPESET']
        self.args = args
        self.settings_file = set_file


class GV (Debuggable):
    def __init__(self):
        # read  command line arguments
        self.args = MeTypeset.read_command_line()

        # absolute first priority is to initialize debugger so that anything triggered here can be logged
        self.debug = Debug()
        Debuggable.__init__(self, 'Globals')

        # read the configuaration
        self.settings_file_path = 'default'
        self.tei_file_path = None
        #SettingsConfiguration.setup_settings_file(self.args)
        #self.settings = SettingsConfiguration(self.get_settings_file(), self.args)

