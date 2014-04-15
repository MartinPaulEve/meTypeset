__author__ = "Martin Paul Eve, Dulip Withnage"
__email__ = "martin@martineve.com"

from lxml import etree
import os
import docxtotei

class Settings:
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

    @staticmethod
    def clean_path(path):
        # TODO: cross-platform fix?
        path = ''.join(path.split())
        return path.replace('\n ', '').replace(" ", "").replace("//", "/")

    @staticmethod
    def concat_path(parent, child):
        return os.path.join(parent, child)

    def get_setting(self, tag_name, caller, domain=None):
        settings = self

        if domain is None:
            expr = "//*[local-name() = $name]"
        else:
            expr = "//mt:{0}/*[local-name() = $name]".format(domain, tag_name)

        tag = settings.tree.xpath(expr, name=tag_name, namespaces={'mt': 'https://github.com/MartinPaulEve/meTypeset'})

        return settings.clean_path(tag[0].text) if tag \
            else caller.debug.fatal_error(caller, '{0} is not defined in settings.xml'.format(tag_name))

    @staticmethod
    def check_settings_file_exists(caller, set_file):
        # noinspection PyBroadException
        try:
            os.path.isfile(set_file)
        except:
            caller.debug.fatal_error(caller, 'Settings file {0} does not exist'.format(set_file))

    @staticmethod
    def get_settings_file(caller, settings_file_path):

        # read  the home folder, either from the path or from the settings file
        # noinspection PyBroadException
        try:
            script_dir = os.environ['METYPESET']

        except:
            # noinspection PyBroadException
            try:
                mod_path = os.path.dirname(docxtotei.__file__)
                script_dir = os.path.abspath(os.path.join(mod_path, os.pardir))
                os.environ['METYPESET'] = script_dir

            except:
                caller.debug.fatal_error(caller, '$METYPESET path not variable is not set '
                                                 'and/or was unable to determine runtime path.')

                script_dir = "NONPATH"

        if settings_file_path == 'default' or settings_file_path is None:
            if script_dir != '':
                set_file = os.path.join(script_dir, 'bin', 'settings.xml')
                Settings.check_settings_file_exists(caller, set_file)
            else:
                    set_file = 'NOFILE'
                    pass
        else:
            set_file = settings_file_path
            Settings.check_settings_file_exists(caller, set_file)

        return set_file