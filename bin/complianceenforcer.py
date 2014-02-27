__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from debug import Debuggable
from nlmmanipulate import *


class ComplianceEnforcer(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Compliance Enforcer')

    def run(self):
        manipulate = NlmManipulate(self.gv)

        self.debug.print_debug(self, u'Removing meTypeset specific attributes and tags')

        tree = manipulate.load_dom_tree()

        render_attributes = tree.xpath('//*[@meTypesetRender]')

        self.debug.print_debug(self, u'Removing {0} meTypesetRender attributes'.format(len(render_attributes)))

        for attribute in render_attributes:
            del attribute.attrib['meTypesetRender']

        manipulate.save_tree(tree)