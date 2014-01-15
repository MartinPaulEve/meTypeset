__author__ = 'Martin Paul Eve'
__email__ = "martin@martineve.com"

import sys

class Debug(object):
    def __init__(self):
        """
        Initialise this debug instance
        @param gv: a reference to an instance of the meTypeset global configuration class
        """
        self.debug = False

    def enable_debug(self):
        self.debug = True

    def print_debug(self, module, message):
        """
        This method prints debug information to stdout when the global debug flag is set
        @param module: the calling module
        @param message: the debug message to print
        """
        if self.debug:
            print(u'[{0}] {1}'.format(module.get_module_name(), message))

    def fatal_error(self, module, message):
        print(u'[FATAL ERROR] [{0}] {1}'.format(module.get_module_name(), message))
        sys.exit(1)


class Debuggable(object):
    def __init__(self, module_name):
        self.module_name = module_name

    def get_module_name(self):
        return self.module_name.encode('utf-8')