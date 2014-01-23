__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from debug import Debuggable
from teimanipulate import TeiManipulate


class ZoteroHandler(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Zotero Handler')

    def handle_bibliography(self, tei_manipulator):
        # remove the Zotero crap marker
        tei_manipulator.tag_bibliography('//tei:p[@rend="Bibliography"]/tei:ref',
                                         ' ADDIN ZOTERO_BIBL {"custom":[]} CSL_BIBLIOGRAPHY ',
                                         self)

        # create a back/div[@type='bibliogr'] section
        tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]',
                                                  'back', 'div', 'type', 'bibliogr')


    def run(self):
        tei_manipulator = TeiManipulate(self.gv)
        object_list = tei_manipulator.get_object_list('//tei:ref[@rend="ref"]', ' ADDIN EN.CITE', u'zoterobiblio')
        object_list += tei_manipulator.get_object_list('//tei:ref', ' ADDIN ZOTERO_ITEM CSL_CITATION', u'zoterobiblio')
        tei_manipulator.drop_addin('//tei:ref[@rend="ref"]', ' ADDIN EN.CITE', 'EndNote',
                                   'hi', 'reference_to_link', self, u'zoterobiblio', True)

        tei_manipulator.drop_addin_json('//tei:ref', ' ADDIN ZOTERO_ITEM CSL_CITATION',
                                        'hi', 'reference_to_link', self)

        # handle bibliography
        self.handle_bibliography(tei_manipulator)

        if len(object_list) > 0:
            self.debug.print_debug(self, u'Stashed {0} references for bibliography parsing'.format(len(object_list)))

        return object_list


class MendeleyHandler(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Mendeley Handler')

    def run(self):
        tei_manipulator = TeiManipulate(self.gv)
        object_list = tei_manipulator.get_object_list('//tei:ref[@rend="ref"]', 'ADDIN CSL_CITATION', u'zoterobiblio')

        tei_manipulator.drop_addin_json('//tei:ref', 'ADDIN CSL_CITATION',
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

        drop = self.gv.setting('drop-unknown-addins')

        tei_manipulator.drop_addin('//*', ' ADDIN', 'EndNote',
                                   'hi', 'unknown_addin_text', self, u'addin',
                                   drop == 'True')

        if len(object_list) > 0:
            self.debug.print_debug(self, u'Handled {0} unknown addin tags'.format(len(object_list)))

        return object_list


class BibliographyAddins(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        self.zotero_items = []
        self.mendeley_items = []
        self.other_items = []
        self.zotero_handler = ZoteroHandler(self.gv)
        self.mendeley_handler = MendeleyHandler(self.gv)
        self.other_handler = OtherHandler(self.gv)
        Debuggable.__init__(self, 'Bibliography Handler')

    def run(self):
        self.zotero_items = self.zotero_handler.run()
        self.mendeley_items = self.mendeley_handler.run()
        self.other_items = self.other_handler.run()