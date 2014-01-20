#!/usr/bin/env python

import globals  as gv
import os
import subprocess, shutil

__author__ = "Dulip Withanage"
__email__ = "dulip.withanage@gmail.com"


class Metadata():
    def __init__(self, gv):
        self.gv = gv


    def attach_metadata(self):
        cmd = ["java", "-classpath", self.gv.JAVA_CLASS_PATH,
               "-Dxml.catalog.files=" + self.gv.RUNTIME_CATALOG_PATH,
               "net.sf.saxon.Transform",
               "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader",
               "-y", "org.apache.xml.resolver.tools.ResolvingXMLReader",
               "-r", "org.apache.xml.resolver.tools.CatalogResolver",
               "-o", self.gv.NLM_FILE_PATH,
               self.gv.NLM_TEMP_FILE_PATH,
               self.gv.METADATA_STYLE_SHEET_PATH,
               'metadataFile=' + self.gv.metadata_file
        ]
        return ' '.join(cmd)

    def run(self):
        java_command = self.attach_metadata()
        subprocess.call(java_command, stdin=None, shell=True)

