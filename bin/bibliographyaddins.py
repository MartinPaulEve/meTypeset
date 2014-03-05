__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from debug import Debuggable
from teimanipulate import TeiManipulate


class ZoteroHandler(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        self.found_biblio = False
        Debuggable.__init__(self, 'Zotero Handler')

    def handle_bibliography(self, tei_manipulator):
        """
        Handle Zotero bibliographies
        @param tei_manipulator: a TEI Manipulator object to handle the XML
        """

        # remove the Zotero marker
        tei_manipulator.tag_bibliography('//tei:p[@rend="Bibliography"]/tei:ref',
                                         ' ADDIN ZOTERO_BIBL {"custom":[]} CSL_BIBLIOGRAPHY ',
                                         self)

        tei_manipulator.tag_bibliography('//tei:p[@rend="Bibliography"]/tei:ref',
                                         ' ADDIN ZOTERO_BIBL {"custom":[]} ', self)

        tei_manipulator.tag_bibliography_non_csl('//tei:p/tei:ref[@rend="ref"]', ' ADDIN EN.REFLIST ', self)

        # create a back/div[@type='bibliogr'] section
        self.found_biblio = tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]',
                                                                      'back', 'div', 'type', 'bibliogr')

        if not self.found_biblio:
            # create a back/div[@type='bibliogr'] section
            self.found_biblio = tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography 1"]',
                                                                          'back', 'div', 'type', 'bibliogr')

    def run(self):
        """
        Handle Zotero in-line reference items

        @return: a list of items handled
        """
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

    def handle_bibliography(self, tei_manipulator):
        """
        Process Mendeley bibliographies

        @param tei_manipulator: a TEI Manipulator object to handle the XML
        """
        tei_manipulator.tag_bibliography('//tei:cit/tei:quote/tei:p//tei:ref',
                                         'ADDIN Mendeley Bibliography CSL_BIBLIOGRAPHY ',
                                         self, u'{http://www.tei-c.org/ns/1.0}p', True)

        # create a back/div[@type='bibliogr'] section
        tei_manipulator.enclose_bibliography_tags('//tei:p[@rend="Bibliography"]',
                                                  'back', 'div', 'type', 'bibliogr')

    def run(self):
        """
        Handle Mendeley reference tags, replacing them with NLM-spec references

        @return: a list of processed tags
        """
        tei_manipulator = TeiManipulate(self.gv)
        object_list = tei_manipulator.get_object_list('//tei:ref[@rend="ref"]', 'ADDIN CSL_CITATION', u'zoterobiblio')

        tei_manipulator.drop_addin_json('//tei:ref', 'ADDIN CSL_CITATION',
                                        'hi', 'reference_to_link', self)

        self.handle_bibliography(tei_manipulator)

        if len(object_list) > 0:
            self.debug.print_debug(self, u'Stashed {0} references for bibliography parsing'.format(len(object_list)))

        return object_list


class OtherHandler(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        Debuggable.__init__(self, 'Other Addin Handler')

    def run(self):
        """
        Handle all unknown types of addin, stripping them from the output

        @return: a list of tags that were removed
        """
        tei_manipulator = TeiManipulate(self.gv)
        object_list = tei_manipulator.get_object_list('//*', ' ADDIN', u'addin')

        drop = self.gv.settings.get_setting('drop-unknown-addins', self)

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
        """
        Run the procedure to process different types of bibliography
        """
        if int(self.gv.settings.args['--aggression']) < int(self.gv.settings.get_setting('bibliographyaddins', self,
                                                                                         domain='aggression')):
            self.debug.print_debug(self, u'Aggression level less than 4: exiting module.')
            return

        self.zotero_items = self.zotero_handler.run()
        self.mendeley_items = self.mendeley_handler.run()
        self.other_items = self.other_handler.run()

        if len(self.zotero_items) > 0 or len(self.mendeley_items) > 0 or self.zotero_handler.found_biblio:
            return True
        else:
            return False