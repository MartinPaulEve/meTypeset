__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that scans for, stores and retrieves NLM citations

"""
from CodernityDB.database import Database
from debug import Debuggable
import tempfile
from nlmmanipulate import NlmManipulate
import os


class Person():
    def __init__(self, firstname='', lastname=''):
        self.firstname = firstname
        self.lastname = lastname

    def get_citation(self):
        return u'<name>' \
                    u'<surname>{0}</surname>' \
                    u'<given-names>{1}</given-names>' \
                u'</name>'.format(self.lastname, self.firstname)

class JournalArticle():
    def __init__(self, authors=[], title='', journal='', issue='', volume='', fpage='', lpage='', year='', doi=''):
        self.authors = authors
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

    def scan(self):
        self.gv.nlm_file_path = self.gv.settings.args['<input>']
        handle, self.gv.nlm_temp_path = tempfile.mkstemp()
        os.close(handle)

        manipulate = NlmManipulate(self.gv)

        # we /could/ use objectify, which would be cleaner, but it doesn't allow such rigidity of parsing

        # scan for journal items
        tree = manipulate.return_elements('//element-citation[@publication-type="journal"]')

        for item in tree:
            journal_item = JournalArticle()

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
                        journal_item.authors += authors

                elif sub_item.tag == 'article-title':
                    journal_item.title = sub_item.text

                elif sub_item.tag == 'source':
                    journal_item.journal = sub_item.text

                elif sub_item.tag == 'date':
                    for date_sub in sub_item:
                        if date_sub.tag == 'year':
                            journal_item.year = sub_item.text

                elif sub_item.tag == 'volume':
                    journal_item.volume = sub_item.text

                elif sub_item.tag == 'issue':
                    journal_item.issue = sub_item.text

                elif sub_item.tag == 'fpage':
                    journal_item.fpage = sub_item.text

                elif sub_item.tag == 'lpage':
                    journal_item.lpage = sub_item.text

                elif sub_item.tag == 'pub-id-type' and 'pub-id-type' in sub_item.attrib:
                    if sub_item.attrib['pub-id-type'] == 'doi':
                        journal_item.doi = sub_item.text

            print journal_item.get_citation()

    def retrieve(self, author, title, year):
        raise NotImplementedError()