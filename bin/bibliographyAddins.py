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
        object_list = tei_manipulator.get_object_list('//tei:ref[@rend="ref"]')
        tei_manipulator.drop_addin('//tei:ref[@rend="ref"]', ' ADDIN EN.CITE', 'EndNote',
                                   'hi', 'reference_to_link', self)

        return object_list


class BibliographyAddins(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        self.zotero_items = []
        Debuggable.__init__(self, 'Bibliography Handler')

    def run(self):
        self.zotero_items = ZoteroHandler(self.gv).run()