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
            cmd = ["java", "-classpath", self.gv.JAVA_CLASS_PATH,
                   "-Dxml.catalog.files="+self.gv.RUNTIME_CATALOG_PATH,
                   "net.sf.saxon.Transform",
                   "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-y", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-r",  "org.apache.xml.resolver.tools.CatalogResolver",
                   "-o", self.gv.TEI_FILE_PATH,
                   self.gv.WORD_DOCUMENT_XML,
                   self.gv.DOC_TO_TEI_STYLESHEET
                   ]
            return ' '.join(cmd)

    def run(self):
        # make output folders
        gv.mk_dir(self.gv.OUTPUT_FOLDER_PATH)
        gv.mk_dir(self.gv.DOCX_TEMP_FOLDER_PATH)
        gv.mk_dir(self.gv.COMMON2_TEMP_FOLDER_PATH)
        gv.mk_dir(self.gv.TEI_FOLDER_PATH)

        #copy folders
        gv.copy_folder(self.gv.COMMON2_LIB_PATH,
                       self.gv.COMMON2_TEMP_FOLDER_PATH, False, None)
        gv.copy_folder(self.gv.DOCX_FOLDER_PATH,
                       self.gv.DOCX_TEMP_FOLDER_PATH, False, None)

        # decompress the docx
        if self.gv.debug:
           print "Unzipping " + self.gv.INPUT_FILE_PATH + " to " + self.gv.DOCX_TEMP_FOLDER_PATH

        with zipfile.ZipFile(self.gv.INPUT_FILE_PATH, "r") as z:
            z.extractall(self.gv.DOCX_TEMP_FOLDER_PATH)

        if self.gv.debug:
           print "Looking for presence of " + self.gv.DOCX_MEDIA_PATH

        if os.path.isdir(self.gv.DOCX_MEDIA_PATH):
           if self.gv.debug:
              print "Ripping out media directory"

           gv.mk_dir(self.gv.OUTPUT_MEDIA_PATH)
           gv.copy_folder(self.gv.DOCX_MEDIA_PATH, self.gv.OUTPUT_MEDIA_PATH, False, None)

        # copy  input file into the docx subfolder
        shutil.copy(self.gv.INPUT_FILE_PATH, self.gv.DOCX_TEMP_FOLDER_PATH)

        # saxon converter
        java_command = self.saxon_doc2tei()
        print "INFO: Running saxon transform (DOCX->TEI)"
        subprocess.call(java_command, stdin=None, shell=True)

        #delete temp folders
        if not(self.gv.debug):
	        shutil.rmtree(self.gv.DOCX_TEMP_FOLDER_PATH)
	        shutil.rmtree(self.gv.COMMON2_TEMP_FOLDER_PATH)
