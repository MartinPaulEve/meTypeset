__author__ = 'Martin Paul Eve'
__email__ = "martin@martineve.com"

class Debug():
    def __init__(self, gv):
        """
        Initialise this debug instance
        @param gv: a reference to an instance of the meTypeset global configuration class
        """
        self.gv = gv
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
            print("[" + module.get_module_name() + "] " + message + ".")
