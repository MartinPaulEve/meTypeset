#!/usr/bin/env python

import subprocess

__author__ = "Dulip Withanage"
__email__ = "dulip.withanage@gmail.com"


class Metadata():
    def __init__(self, gv):
        self.gv = gv

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
               'metadataFile=' + self.gv.metadata_file
        ]
        return ' '.join(cmd)

    def run(self):
        java_command = self.attach_metadata()
        subprocess.call(java_command, stdin=None, shell=True)