__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that scans for, stores and retrieves NLM citations

"""
import shelve
from debug import Debuggable
import tempfile
from nlmmanipulate import NlmManipulate
import os
from lxml import etree


class Person():
    def __init__(self, firstname='', lastname=''):
        self.firstname = firstname
        self.lastname = lastname

    def get_citation(self):
        return u'<name>' \
                    u'<surname>{0}</surname>' \
                    u'<given-names>{1}</given-names>' \
                u'</name>'.format(self.lastname, self.firstname)

class Book():
    def __init__(self, authors=None, title='', publisher = '', place = '', year=''):
        if authors is None:
            self.authors = []
        self.title = title
        self.year = year
        self.publisher = publisher
        self.place = place

    def get_citation(self):

        author_block = ''
        for author in self.authors:
            author_block += author.get_citation()

        return u'<ref>'  \
                    u'<element-citation publication-type="book">' \
                        u'<person-group person-group-type="author">' \
                            u'{0}' \
                            u'</person-group>' \
                            u'<source>{1}</source>' \
                            u'<date>' \
                                u'<year>{2}</year>' \
                            u'</date>' \
                            u'<publisher-loc>{3}</publisher-loc>' \
                            u'<publisher-name>{4}</publisher-name>' \
                        u'</element-citation>' \
                u'</ref>'.format(author_block, self.title, self.year, self.place, self.publisher)


class JournalArticle():
    def __init__(self, authors=None, title='', journal='', issue='', volume='', fpage='', lpage='', year='', doi=''):
        if authors is None:
            self.authors = []
        self.title = title
        self.journal = journal
        self.issue = issue
        self.volume = volume
        self.fpage = fpage
        self.lpage = lpage
        self.year = year
        self.doi = doi

    def get_citation(self):

        author_block = ''
        for author in self.authors:
            author_block += author.get_citation()

        return u'<ref>'  \
                    u'<element-citation publication-type="journal">' \
                        u'<person-group person-group-type="author">' \
                            u'{0}' \
                            u'</person-group>' \
                            u'<article-title>{1}</article-title>' \
                            u'<source>{2}</source>' \
                            u'<date>' \
                                u'<year>{3}</year>' \
                            u'</date>' \
                            u'<volume>{4}</volume>' \
                            u'<issue>{5}</issue>' \
                            u'<fpage>{6}</fpage>' \
                            u'<lpage>{7}</lpage>' \
                            u'<pub-id pub-id-type="doi">{8}</pub-id>' \
                        u'</element-citation>' \
                u'</ref>'.format(author_block, self.title, self.journal, self.year, self.volume, self.issue, self.fpage,
                                self.lpage, self.doi)


class BibliographyDatabase(Debuggable):
    def __init__(self, global_variables):
        self.gv = global_variables
        self.debug = self.gv.debug
        self.size_cutoff = 16
        Debuggable.__init__(self, 'Bibliography Database')

    def parse_journal_item(self, item):
        journal_entry = JournalArticle()

        for sub_item in item:
            if sub_item.tag == 'person-group' and 'person-group-type' in sub_item.attrib:
                if sub_item.attrib['person-group-type'] == 'author':
                    authors = []
                    for author_item in sub_item:
                        author = Person()
                        for names in author_item:
                            if names.tag == 'surname':
                                author.lastname = names.text
                            elif names.tag == 'given-names':
                                author.firstname = names.text
                        authors.append(author)
                    journal_entry.authors += authors

            elif sub_item.tag == 'article-title':
                journal_entry.title = sub_item.text

            elif sub_item.tag == 'source':
                journal_entry.journal = sub_item.text

            elif sub_item.tag == 'date':
                for date_sub in sub_item:
                    if date_sub.tag == 'year':
                        journal_entry.year = date_sub.text

            elif sub_item.tag == 'volume':
                journal_entry.volume = sub_item.text

            elif sub_item.tag == 'issue':
                journal_entry.issue = sub_item.text

            elif sub_item.tag == 'fpage':
                journal_entry.fpage = sub_item.text

            elif sub_item.tag == 'lpage':
                journal_entry.lpage = sub_item.text

            elif sub_item.tag == 'pub-id' and 'pub-id-type' in sub_item.attrib:
                if sub_item.attrib['pub-id-type'] == 'doi':
                    journal_entry.doi = sub_item.text

        return journal_entry


    def parse_book_item(self, item):
        book_entry = Book()

        for sub_item in item:
            if sub_item.tag == 'person-group' and 'person-group-type' in sub_item.attrib:
                if sub_item.attrib['person-group-type'] == 'author':
                    authors = []
                    for author_item in sub_item:
                        author = Person()
                        for names in author_item:
                            if names.tag == 'surname':
                                author.lastname = names.text
                            elif names.tag == 'given-names':
                                author.firstname = names.text
                        authors.append(author)
                    book_entry.authors += authors

            elif sub_item.tag == 'source':
                book_entry.title = sub_item.text

            elif sub_item.tag == 'year':
                book_entry.year = sub_item.text

            elif sub_item.tag == 'date':
                for date_sub in sub_item:
                    if date_sub.tag == 'year':
                        book_entry.year = date_sub.text

            elif sub_item.tag == 'publisher-loc':
                book_entry.place = sub_item.text

            elif sub_item.tag == 'publisher-name':
                book_entry.publisher = sub_item.text

        return book_entry

    def store_key(self, db, item, key):
        self.debug.print_debug(self, 'Storing {0}'.format(key))
        db[key] = item

    def store_journal_item(self, db, tree):
        for item in tree:
            journal_item = self.parse_journal_item(item)

            if len(journal_item.authors) > 0:
                key = journal_item.year + journal_item.authors[0].lastname + journal_item.journal
            else:
                key = journal_item.year + journal_item.title + journal_item.journal

            self.store_key(db, journal_item, key)

    def store_book(self, db, tree):
        for item in tree:
            book = self.parse_book_item(item)

            if len(book.authors) > 0:
                key = book.year + book.authors[0].lastname + book.title
            else:
                key = book.year + book.title

            self.store_key(db, book, key)

    def scan(self):
        self.gv.nlm_file_path = self.gv.settings.args['<input>']
        handle, self.gv.nlm_temp_path = tempfile.mkstemp()
        os.close(handle)

        manipulate = NlmManipulate(self.gv)

        # open the database
        self.debug.print_debug(self, 'Opening database: {0}'.format(self.gv.database_file_path))
        db = shelve.open(self.gv.database_file_path)

        # we /could/ use objectify, which would be cleaner, but it doesn't allow such rigidity of parsing

        # scan for journal items
        tree = manipulate.return_elements('//element-citation[@publication-type="journal"]')
        self.store_journal_item(db, tree)

        tree = manipulate.return_elements('//element-citation[@publication-type="book"]')
        self.store_book(db, tree)

        db.close()

    def retrieve(self, author, title, year):
        raise NotImplementedError()