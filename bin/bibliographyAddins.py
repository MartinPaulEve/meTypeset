__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from debug import Debuggable
from teimanipulate import TeiManipulate


class ZoteroHandler(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Zotero Handler')

    def run(self):
        self.debug.print_debug(self, "Running Zotero handler")
        tei_manipulator = TeiManipulate(self.gv)
        tei_manipulator.drop_addin('//tei:ref[@rend="ref"]')


class BibliographyAddins(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Bibliography Handler')

    def run(self):
        ZoteroHandler(self.gv).run()