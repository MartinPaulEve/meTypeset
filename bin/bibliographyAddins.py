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
        object_list = tei_manipulator.get_object_list('//tei:ref[@rend="ref"]', ' ADDIN EN.CITE', u'zoterobiblio')
        object_list += tei_manipulator.get_object_list('//tei:ref', ' ADDIN ZOTERO_ITEM CSL_CITATION', u'zoterobiblio')
        tei_manipulator.drop_addin('//tei:ref[@rend="ref"]', ' ADDIN EN.CITE', 'EndNote',
                                   'hi', 'reference_to_link', self, u'zoterobiblio', True)

        tei_manipulator.drop_addin_json('//tei:ref', ' ADDIN ZOTERO_ITEM CSL_CITATION',
                                        'hi', 'reference_to_link', self)

        if len(object_list) > 0:
            self.debug.print_debug(self, u'Stashed {0} references for bibliography parsing'.format(len(object_list)))

        return object_list

class OtherHandler(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Other Addin Handler')

    def run(self):
        tei_manipulator = TeiManipulate(self.gv)
        object_list = tei_manipulator.get_object_list('//*', ' ADDIN', u'addin')
        tei_manipulator.drop_addin('//*', ' ADDIN', 'EndNote',
                                   'hi', 'unknown_addin_text', self, u'addin', True)

        if len(object_list) > 0:
            self.debug.print_debug(self, u'Dropped {0} unknown addin tags'.format(len(object_list)))

        return object_list


class BibliographyAddins(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        self.zotero_items = []
        self.zotero_handler = ZoteroHandler(self.gv)
        self.other_handler = OtherHandler(self.gv)
        Debuggable.__init__(self, 'Bibliography Handler')

    def run(self):
        self.zotero_items = self.zotero_handler.run()
        self.other_items = self.other_handler.run()