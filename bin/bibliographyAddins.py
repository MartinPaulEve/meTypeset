__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from debug import Debuggable

class ZoteroHandler(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Zotero Handler')

