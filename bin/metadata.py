#!/usr/bin/env python

import subprocess
from manipulate import Manipulate

__author__ = "Martin Paul Eve, Dulip Withanage"
__email__ = "martin@martineve.com"


class Metadata(Manipulate):
    def __init__(self, gv):
        self.gv = gv
        self.metadata_items = {}
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

    def pre_clean(self):
        # load the metadata file for reading
        tree = self.load_dom_read()

        # attempt to find identifiers
        count = 0
        ids = tree.xpath('//article-id | //tei:article-id', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        for id in ids:
            self.metadata_items['ID{0}'.format(count)] = self.get_stripped_text(id)
            count += 1

        self.metadata_items['IDs_count'] = count

        # attempt to find article titles
        count = 0
        titles = tree.xpath('//article-title | //tei:article-title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        for title in titles:
            self.metadata_items['title{0}'.format(count)] = self.get_stripped_text(title)
            count += 1

        self.metadata_items['titles_count'] = count
