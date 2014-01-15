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
        tei_manipulator = TeiManipulate(self.gv)
        object_list = tei_manipulator.get_object_list('//tei:ref[@rend="ref"]', ' ADDIN EN.CITE')
        object_list += tei_manipulator.get_object_list('//tei:ref', ' ADDIN ZOTERO_ITEM CSL_CITATION')
        tei_manipulator.drop_addin('//tei:ref[@rend="ref"]', ' ADDIN EN.CITE', 'EndNote',
                                   'hi', 'reference_to_link', self)

        tei_manipulator.drop_addin_json('//tei:ref', ' ADDIN ZOTERO_ITEM CSL_CITATION',
                                        'hi', 'reference_to_link', self)

        if len(object_list) > 0:
            self.debug.print_debug(self, u'Zotero Handler stashed {0} references for '
                                         u'bibliography parsing'.format(len(object_list)))

        return object_list


class BibliographyAddins(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        self.zotero_items = []
        self.zotero_handler = ZoteroHandler(self.gv)
        Debuggable.__init__(self, 'Bibliography Handler')

    def run(self):
        self.zotero_items = self.zotero_handler.run()