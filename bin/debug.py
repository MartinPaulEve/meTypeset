from __future__ import print_function

__author__ = 'Martin Paul Eve'
__email__ = "martin@martineve.com"

import sys
import os
from git import *

class Debug(object):
    def __init__(self):
        """
        Initialise this debug instance
        @param gv: a reference to an instance of the meTypeset global configuration class
        """
        self.debug = False
        self.has_run = False
        self.prompt = None

        self.git_objects = []

    def enable_debug(self):
        self.debug = True

    def enable_prompt(self, prompt):
        self.prompt = prompt

    def print_(self, module, message):
        if self.prompt is None:
            print(u'[{0}] {1}'.format(module.get_module_name(), unicode(message)))
        else:
            self.prompt.print_(u'[{0}] {1}'.format(self.prompt.colorize('red', module.get_module_name()),
                                                   unicode(message)))

    def get_module_name(self):
        return 'Debugger'

    def mkdir(self, path):
        try:
            os.makedirs(path)
            
            if self.debug:
                self.print_(self, u'Initializing git repo at {0}'.format(path))
                repo = Git(path)
                repo.init()
                self.git_objects.append(repo)
        except:
            self.fatal_error(self, 'Output directory {0} already exists'.format(path))

    def print_debug(self, module, message):
        """
        This method prints debug information to stdout when the global debug flag is set
        @param module: the calling module
        @param message: the debug message to print
        """
        if self.debug:

            if not isinstance(message, unicode):
                self.fatal_error(self, u'A non unicode string was passed to the debugger')

            self.print_(module, message)

            # optionally, if the calling module has a "gv" object within it, we will try to take a git snapshot
            for repo in self.git_objects:
                repo.add('.', with_exceptions=False)

                # remove all characters above 128 as the git module does not handle unicode commits well
                repo.commit(u'-m', u'{0}'.format("".join(i for i in message if ord(i)<128)), with_exceptions=False)

    def write_error(self, module, message, error_number):
        """
        This method writes parsing information to the error log
        @param module: the calling module
        @param message: the error message to print
        """

        if not self.has_run:
            module.gv.mk_dir(module.gv.error_folder_path)
            self.has_run = True

        error_file = open(module.gv.error_file_path, 'w')
        print(u'[{0}] {1}\n'.format(error_number, message), file=error_file)
        error_file.close()

    @staticmethod
    def fatal_error(module, message):
        print(u'[FATAL ERROR] [{0}] {1}'.format(module.get_module_name(), message))
        sys.exit(1)


class Debuggable(object):
    def __init__(self, module_name):
        self.module_name = module_name

    def get_module_name(self):
        return unicode(self.module_name, 'utf-8')