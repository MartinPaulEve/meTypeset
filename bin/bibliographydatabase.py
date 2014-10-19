#!/usr/bin/env python
# coding=utf-8
"""bibliographydatabase: a tool to match plaintext values inside NLM ref tags against a known database

Usage:
    bibliographydatabase.py <input> [options]
    bibliographydatabase.py zotero <query> [options]

Options:
    -d, --debug                                     Enable debug output.
    -h, --help                                      Show this screen.
    -v, --version                                   Show version.
    -z, --zotero                                    Enable Zotero integration for references.
"""

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that scans for, stores and retrieves NLM citations

"""
from debug import Debuggable
import tempfile
from nlmmanipulate import NlmManipulate
import os
import re
from lxml import etree
from docopt import docopt
from bare_globals import GV
from interactive import Interactive


class Person():
    def __init__(self, firstname='', lastname=''):
        self.firstname = firstname
        self.lastname = lastname

    def get_citation(self):
        return u'<name>' \
                    u'<surname>{0}</surname>' \
                    u'<given-names>{1}</given-names>' \
                u'</name>'.format(self.lastname, self.firstname)


class Website():
    def __init__(self, authors=None, title='', website_title='', year='', url=''):
        if authors is None:
            self.authors = []
        else:
            self.authors = authors

        self.website_title = website_title
        self.title = title
        self.book_title = website_title
        self.year = year
        self.url = url

    @staticmethod
    def object_type():
        return "website"

    def get_citation(self):

        author_block = ''
        for author in self.authors:
            author_block += author.get_citation()

        ret = u'<ref>'
        ret += u'<element-citation publication-type="journal">'

        if author_block != '':
            ret += u'<person-group person-group-type="author">{0}</person-group>'.format(author_block)

        if self.title != '':
            ret += u'<article-title>{0}</article-title>'.format(self.title)

        if self.book_title != '':
            ret += u'<source>{0}</source>'.format(self.website_title)

        ret += u'<date><year>{0}</year></date>'.format(self.year)

        if self.url != '' and self.url is not None:
            ret += u'<uri>{0}</uri>'.format(self.url)


        ret += u'</element-citation>'
        ret += u'</ref>'

        ret = ret.replace('&', '&amp;')
        ret = ret.replace('<i>', '<italic>')
        ret = ret.replace('</i>', '</italic>')

        return ret


class BookChapter():
    def __init__(self, authors=None, title='', book_title='', publisher='', place='', year='', fpage='', lpage='',
                 editors=None, translators=None, doi=''):
        if authors is None:
            self.authors = []
        else:
            self.authors = authors

        if editors is None:
            self.editors = []
        else:
            self.editors = editors

        if translators is None:
            self.translators = []
        else:
            self.translators = translators

        self.title = title
        self.book_title = book_title
        self.year = year
        self.publisher = publisher
        self.place = place
        self.fpage = fpage
        self.lpage = lpage
        self.doi = doi

    @staticmethod
    def object_type():
        return "book chapter"

    def get_citation(self):

        author_block = ''
        for author in self.authors:
            author_block += author.get_citation()

        translator_block = ''
        for translator in self.translators:
            translator_block += translator.get_citation()

        editor_block = ''
        for editor in self.editors:
            editor_block += editor.get_citation()

        ret = u'<ref>'
        ret += u'<element-citation publication-type="bookchapter">'

        if author_block != '':
            ret += u'<person-group person-group-type="author">{0}</person-group>'.format(author_block)

        if self.title != '':
            ret += u'<article-title>{0}</article-title>'.format(self.title)

        if self.book_title != '':
            ret += u'<source>{0}</source>'.format(self.book_title)

        ret += u'<date><year>{0}</year></date>'.format(self.year)

        if editor_block != '':
            ret += u'<person-group person-group-type="editor">{0}</person-group>'.format(editor_block)

        if translator_block != '':
            ret += u'<person-group person-group-type="translator">{0}</person-group>'.format(translator_block)

        ret += u'<publisher-loc>{0}</publisher-loc>'.format(self.place)

        ret += u'<publisher-name>{0}</publisher-name>'.format(self.publisher)

        if self.fpage != '' and self.fpage is not None:
            ret += u'<fpage>{0}</fpage>'.format(self.fpage)

        if self.lpage != '' and self.lpage is not None:
            ret += u'<lpage>{0}</lpage>'.format(self.lpage)

        if self.doi != '' and self.doi is not None:
            ret += u'<pub-id pub-id-type="doi">{0}</pub-id>'.format(self.doi)


        ret += u'</element-citation>'
        ret += u'</ref>'

        ret = ret.replace('&', '&amp;')
        ret = ret.replace('<i>', '<italic>')
        ret = ret.replace('</i>', '</italic>')

        return ret


class Book():
    def __init__(self, authors=None, title='', publisher='', place='', year='', editors=None, doi='', translators=None):
        if authors is None:
            self.authors = []
        else:
            self.authors = authors

        if editors is None:
            self.editors = []
        else:
            self.editors = editors

        if translators is None:
            self.translators = []
        else:
            self.translators = translators

        self.title = title
        self.year = year
        self.publisher = publisher
        self.place = place

        self.doi = doi

    @staticmethod
    def object_type():
        return "book"

    def get_citation(self):

        author_block = ''
        for author in self.authors:
            author_block += author.get_citation()

        translator_block = ''
        for translator in self.translators:
            translator_block += translator.get_citation()

        editor_block = ''
        for editor in self.editors:
            editor_block += editor.get_citation()

        ret = u'<ref>'
        ret += u'<element-citation publication-type="book">'

        if author_block != '':
            ret += u'<person-group person-group-type="author">{0}</person-group>'.format(author_block)

        if self.title != '':
            ret += u'<source>{0}</source>'.format(self.title)

        ret += u'<date><year>{0}</year></date>'.format(self.year)

        if editor_block != '':
            ret += u'<person-group person-group-type="editor">{0}</person-group>'.format(editor_block)

        if translator_block != '':
            ret += u'<person-group person-group-type="translator">{0}</person-group>'.format(translator_block)

        ret += u'<publisher-loc>{0}</publisher-loc>'.format(self.place)

        ret += u'<publisher-name>{0}</publisher-name>'.format(self.publisher)

        if self.doi != '' and self.doi is not None:
            ret += u'<pub-id pub-id-type="doi">{0}</pub-id>'.format(self.doi)


        ret += u'</element-citation>'
        ret += u'</ref>'

        ret = ret.replace('&', '&amp;')
        ret = ret.replace('<i>', '<italic>')
        ret = ret.replace('</i>', '</italic>')

        return ret


class JournalArticle():
    def __init__(self, authors=None, title='', journal='', issue='', volume='', fpage='', lpage='', year='', doi='',
                 translators=None):
        if authors is None:
            self.authors = []
        else:
            self.authors = authors

        if translators is None:
            self.translators = []
        else:
            self.translators = translators

        self.title = title
        self.journal = journal
        self.issue = issue
        self.volume = volume
        self.fpage = fpage
        self.lpage = lpage
        self.year = year
        self.doi = doi

    @staticmethod
    def object_type():
        return "journal article"

    def get_citation(self):

        author_block = ''
        for author in self.authors:
            author_block += author.get_citation()

        translator_block = ''
        for translator in self.translators:
            translator_block += translator.get_citation()

        ret = u'<ref>'
        ret += u'<element-citation publication-type="journal">'

        if author_block != '':
            ret += u'<person-group person-group-type="author">{0}</person-group>'.format(author_block)

        if self.title != '':
            ret += u'<article-title>{0}</article-title>'.format(self.title)

        if self.journal != '':
            ret += u'<source>{0}</source>'.format(self.journal)

        if translator_block != '':
            ret += u'<person-group person-group-type="translator">{0}</person-group>'.format(translator_block)

        ret += u'<date><year>{0}</year></date>'.format(self.year)

        if self.volume != '' and self.volume is not None:
            ret += u'<volume>{0}</volume>'.format(self.volume)

        if self.issue != '' and self.volume is not None:
            ret += u'<issue>{0}</issue>'.format(self.issue)

        if self.fpage != '' and self.fpage is not None:
            ret += u'<fpage>{0}</fpage>'.format(self.fpage)

        if self.lpage != '' and self.lpage is not None:
            ret += u'<lpage>{0}</lpage>'.format(self.lpage)

        if self.doi != '' and self.doi is not None:
            ret += u'<pub-id pub-id-type="doi">{0}</pub-id>'.format(self.doi)


        ret += u'</element-citation>'
        ret += u'</ref>'

        ret = ret.replace('&', '&amp;')
        ret = ret.replace('<i>', '<italic>')
        ret = ret.replace('</i>', '</italic>')

        return ret

class BibliographyDatabase(Debuggable):
    def __init__(self, global_variables):
        Debuggable.__init__(self, 'Bibliography Database')
        self.gv = global_variables
        self.debug = self.gv.debug
        self.size_cutoff = 16
        self.aggression = 8

    def process_zotero(self):
        from zotero import libzotero
        zotero = libzotero.LibZotero(unicode(self.gv.settings.get_setting(u'zotero', self)), self.gv)

        manipulate = NlmManipulate(self.gv)
        master_tree = manipulate.load_dom_tree()
        tree = master_tree.xpath('//back/ref-list/ref')

        for element in tree:
            original_term = manipulate.get_stripped_text(element)
            term = original_term

            #term = re.sub(r'(.+?)(\(.+?\))(.*)', r'\1\3', term)
            term = re.sub(r'(?<![0-9])[1-9][0-9]{0,2}(?![0-9])', r'', term)
            term = re.sub(r'[\-,\.\<\>\(\)\;\:\@\'\#\~\}\{\[\]\"\!\\/]', '', term)
            term = re.sub(u'[^\s]+?\s[Ee]dition', u' ', term)
            term = re.sub(u'\s.\s', u' ', term)
            term = re.sub(u'(?<=[A-Z])\.', u' ', term)
            term = term.replace(u'“', u'')
            term = term.replace(u'\'s', u'')
            term = term.replace(u'’s', u'')
            term = term.replace(u'’', u'')
            term = term.replace(u' Ed. ', u' ')
            term = term.replace(u' Ed ', u' ')
            term = term.replace(u' Trans. ', u' ')
            term = term.replace(u' Trans ', u' ')
            term = term.replace(u' trans ', u' ')
            term = term.replace(u' trans. ', u' ')
            term = term.replace(u' by. ', u' ')
            term = term.replace(u' by ', u' ')
            term = term.replace(u' ed. ', u' ')
            term = term.replace(u' ed ', u' ')
            term = term.replace(u' In ', u' ')
            term = term.replace(u' in ', u' ')
            term = term.replace(u' print ', u' ')
            term = term.replace(u' Print ', u' ')
            term = term.replace(u' and ', u' ')
            term = term.replace(u'”', u'')
            term = re.sub(r'[Aa]ccessed', '', term)
            term = re.sub(r'meTypesetbr', '', term)
            term = re.sub(r'\s+', ' ', term)

            results = zotero.search(term.strip())

            while len(results) == 0 and len(term.strip().split(' ')) > 2:
                # no results found.
                # begin iterating backwards
                term = ' '.join(term.strip().split(' ')[:-1])
                results = zotero.search(term.strip())

            if len(results) == 1:
                res = results[0].JATS_format()

                if res is not None:
                    ref = etree.fromstring(res)
                    if 'id' in element.attrib:
                        ref.attrib['id'] = element.attrib['id']

                    element.addnext(ref)

                    original_term = re.sub(u'--', u'', original_term)

                    comment = etree.Comment(original_term)
                    ref.addnext(comment)

                    element.tag = 'REMOVE'

        etree.strip_elements(master_tree, 'REMOVE')

        manipulate.save_tree(master_tree)

    def run(self):
        if self.gv.use_zotero:
            self.process_zotero()


def main():
    args = docopt(__doc__, version='meTypeset 0.1')

    bare_gv = GV(args)

    if args['--debug']:
        bare_gv.debug.enable_debug(True)
        bare_gv.debug.enable_prompt(Interactive(bare_gv))

    if args['zotero']:
        from zotero import libzotero
        zotero = libzotero.LibZotero(unicode(bare_gv.settings.get_setting(u'zotero', bare_gv)), bare_gv)

        term = args['<query>']

        term = re.sub(r'[\-,\.\<\>\(\)\;\:\@\'\#\~\}\{\[\]\"\!\\/]', ' ', term)
        term = term.replace(u'“', u'')
        term = re.sub(u'[^\s]+?\s[Ee]dition', u' ', term)
        term = term.replace(u'\'s', u'')
        term = term.replace(u'’s', u'')
        term = term.replace(u'’', u'')
        term = term.replace(u'”', u'')
        term = re.sub(r'[Aa]ccessed', '', term)
        term = re.sub(r'meTypesetbr', '', term)
        term = re.sub(r'\s+', ' ', term)

        results = zotero.search(term.strip())

        bare_gv.debug.print_debug(bare_gv, "%d results for %s" % (len(results), term))

        for item in results:
            interactive = Interactive(bare_gv)
            interactive.print_(item.JATS_format())

        return

    bibliography_database_instance = BibliographyDatabase(bare_gv)
    bibliography_database_instance.run()


if __name__ == '__main__':
    main()