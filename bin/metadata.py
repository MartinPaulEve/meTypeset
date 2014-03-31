#!/usr/bin/env python

import subprocess
from manipulate import Manipulate
from teimanipulate import TeiManipulate

__author__ = "Martin Paul Eve, Dulip Withanage"
__email__ = "martin@martineve.com"


class Metadata(Manipulate):
    def __init__(self, gv):
        self.gv = gv
        self.metadata_items = {}
        self.metadata = []
        self.authors = []
        self.debug = self.gv.debug
        self.dom_to_load = self.gv.input_metadata_file_path
        self.dom_temp_file = self.gv.input_metadata_file_path
        self.mod_name = 'Metadata'
        Manipulate.__init__(self, gv)

    def attach_metadata(self):
        cmd = ["java", "-classpath", self.gv.java_class_path,
               "-Dxml.catalog.files=" + self.gv.runtime_catalog_path,
               "net.sf.saxon.Transform",
               "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader",
               "-y", "org.apache.xml.resolver.tools.ResolvingXMLReader",
               "-r", "org.apache.xml.resolver.tools.CatalogResolver",
               "-o", self.gv.nlm_file_path,
               self.gv.nlm_temp_file_path,
               self.gv.metadata_style_sheet_path,
               'metadataFile=' + self.gv.input_metadata_file_path
        ]
        return ' '.join(cmd)

    def run(self):
        java_command = self.attach_metadata()
        subprocess.call(java_command, stdin=None, shell=True)

        # copy back to the temp file for debug purposes
        Manipulate.update_tmp_file(self.gv.nlm_file_path, self.gv.nlm_temp_file_path)

    def extract_metadata_fields(self):
        # load the metadata file for reading
        tree = self.load_dom_read()

        metadata = []

        # attempt to find identifiers
        count = 0
        ids = tree.xpath('//article-id | //tei:article-id', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        for id in ids:
            text = self.get_stripped_text(id).strip()
            self.metadata_items['ID{0}'.format(count)] = text
            self.metadata.append(text)
            count += 1

            self.debug.print_debug(self, u'Extracted an article ID: "{0}" from metadata'.format(text))
        self.metadata_items['IDs_count'] = count

        # attempt to find article titles
        count = 0
        titles = tree.xpath('//article-title | //tei:article-title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        for title in titles:
            text = self.get_stripped_text(title).strip()
            self.metadata_items['title{0}'.format(count)] = text
            self.metadata.append(text)
            count += 1

            self.debug.print_debug(self, u'Extracted an article title: "{0}" from metadata'.format(text))
        self.metadata_items['titles_count'] = count

        # attempt to find journal titles
        count = 0
        titles = tree.xpath('//journal-title | //tei:journal-title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        for title in titles:
            text = self.get_stripped_text(title).strip()
            self.metadata_items['journal_title{0}'.format(count)] = text
            self.metadata.append(text)
            count += 1

            self.debug.print_debug(self, u'Extracted a journal title: "{0}" from metadata'.format(text))
        self.metadata_items['journal_titles_count'] = count

        # attempt to find authors
        count = 0
        titles = tree.xpath('//contrib/name | //tei:contrib/tei:name',
                            namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        authors = []

        for title in titles:
            components = []
            for component in title:
                text = self.get_stripped_text(component).strip()
                self.debug.print_debug(self, u'Extracted a name component: "{0}" from metadata'.format(text))
                components.append(text)

            self.metadata_items['contrib_name{0}'.format(count)] = components
            self.authors.append(components)
            count += 1

            self.metadata_items['contrib_names_count'] = count


        # attempt to find affiliations
        count = 0
        titles = tree.xpath('//aff | //tei:aff', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        for title in titles:
            text = self.get_stripped_text(title).strip()
            self.metadata_items['aff{0}'.format(count)] = text
            self.metadata.append(text)
            count += 1

            self.debug.print_debug(self, u'Extracted an affiliation: "{0}" from metadata'.format(text))
        self.metadata_items['affs_count'] = count

    def pre_clean(self):
        self.extract_metadata_fields()

        manipulate = TeiManipulate(self.gv)

        tree = manipulate.load_dom_tree()

        # get all elements in the body
        section = tree.xpath('//tei:body//*', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        items_to_match = ['{http://www.tei-c.org/ns/1.0}head', '{http://www.tei-c.org/ns/1.0}p',
                          '{http://www.tei-c.org/ns/1.0}cit']

        count = 0

        matched_authors = []

        for item in section:
            if count > 2:
                break

            if item.tag in items_to_match:
                count += 1
                text = self.get_stripped_text(item)

                processed = False

                for author in self.authors:
                    if not author in matched_authors:
                        has_all = True
                        for component in author:
                            if not component in text:
                                has_all = False
                                break

                        if has_all:
                            # found a metadata line
                            matched_authors.append(author)
                            count -= 1
                            item.getparent().remove(item)
                            self.debug.print_debug(self, u'Removed line "{0}" '
                                                         u'because it appears to be author metadata'.format(text))
                            processed = True
                            break

                if not processed:
                    for metadata in self.metadata:
                        if metadata in text:
                            # found a metadata line
                            count -= 1
                            item.getparent().remove(item)
                            self.debug.print_debug(self, u'Removed line "{0}" '
                                                         u'because it appears to be duplicated metadata'.format(text))

        manipulate.save_tree(tree)

