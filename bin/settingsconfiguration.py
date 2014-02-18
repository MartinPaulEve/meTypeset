__author__ = "Martin Paul Eve, Dulip Withnage"
__email__ = "martin@martineve.com"

from lxml import etree
import os

class SettingsConfiguration:
    def __init__(self, set_file, args):
        tree = etree.parse(set_file)
        self.tree = tree
        self.script_dir = os.environ['METYPESET']
        self.args = args
        self.settings_file = set_file

    @staticmethod
    def setup_settings_file(args):
        if '--settings' in args:
            settings = args['--settings']
            if settings:
                return settings