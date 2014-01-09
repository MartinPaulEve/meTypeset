#!/usr/bin/env python

import distutils
import os
import errno
import shutil
import zipfile
import subprocess
import globals as gv

__author__ = "Dulip Withanage"
__email__ = "dulip.withanage@gmail.com"


class Docx2TEI:
    def __init__(self, gv):
        self.gv = gv

    def saxon_doc2tei(self):
            cmd = ["java", "-classpath", self.gv.java_class_path,
                   "-Dxml.catalog.files="+self.gv.runtime_catalog_path,
                   "net.sf.saxon.Transform",
                   "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-y", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-r",  "org.apache.xml.resolver.tools.CatalogResolver",
                   "-o", self.gv.tei_file_path,
                   self.gv.word_document_xml,
                   self.gv.docx_to_tei_stylesheet
                   ]
            return ' '.join(cmd)

    def run(self):
        # make output folders
        self.gv.mk_dir(self.gv.output_folder_path)
        self.gv.mk_dir(self.gv.docx_temp_folder_path)
        self.gv.mk_dir(self.gv.common2_temp_folder_path)
        self.gv.mk_dir(self.gv.tei_folder_path)

        #copy folders
        self.gv.copy_folder(self.gv.common2_lib_path,
                       self.gv.common2_temp_folder_path, False, None)
        self.gv.copy_folder(self.gv.docx_folder_path,
                       self.gv.docx_temp_folder_path, False, None)

        # decompress the docx
        if self.gv.debug:
           print "Unzipping " + self.gv.input_file_path + " to " + self.gv.docx_temp_folder_path

        with zipfile.ZipFile(self.gv.input_file_path, "r") as z:
            z.extractall(self.gv.docx_temp_folder_path)

        if self.gv.debug:
           print "Looking for presence of " + self.gv.docx_media_path

        if os.path.isdir(self.gv.docx_media_path):
           if self.gv.debug:
              print "Ripping out media directory"

           self.gv.mk_dir(self.gv.output_media_path)
           self.gv.copy_folder(self.gv.docx_media_path, self.gv.output_media_path, False, None)

        # copy  input file into the docx subfolder
        shutil.copy(self.gv.input_file_path, self.gv.docx_folder_path)

        # saxon converter
        java_command = self.saxon_doc2tei()
        print "INFO: Running saxon transform (DOCX->TEI)"
        subprocess.call(java_command, stdin=None, shell=True)

        #delete temp folders
        if not(self.gv.debug):
            shutil.rmtree(self.gv.docx_temp_folder_path)
            shutil.rmtree(self.gv.common2_temp_folder_path)
