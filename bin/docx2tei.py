#!/usr/bin/env python
# @Author Dulip Withanage

import distutils, os, errno
import shutil, zipfile, subprocess
import globals  as gv

import os

class Docx2TEI :
    def __init__(self,gv):
        self.gv = gv

        
   
    def saxon_doc2tei(self ):
        cmd = ["java", "-classpath", self.gv.JAVA_CLASS_PATH, \
                    "-Dxml.catalog.files="+self.gv.RUNTIME_CATALOG,\
                    "net.sf.saxon.Transform", \
                    "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader", \
                    "-y" ,"org.apache.xml.resolver.tools.ResolvingXMLReader", \
                    "-r",  "org.apache.xml.resolver.tools.CatalogResolver", \
                    "-o", self.gv.TEI_FILE_PATH+'/'+self.gv.TEI_FILE_NAME ,\
                    self.gv.WORD_DOCUMENT_XML,\
                    self.gv.DOC_TO_TEI_STYLESHEET
            ]
        return ' '.join(cmd)


    def  run(self):
        
        # make output folders
        gv.mk_dir(self.gv.OUTPUT_FOLDER)
        gv.mk_dir(self.gv.DOCX_OUT)
        gv.mk_dir(self.gv.COMMON2_OUT)
        gv.mk_dir(self.gv.TEI_FILE_PATH)

        #copy folders
        gv.copy_folder(self.gv.COMMON2_PATH, self.gv.COMMON2_OUT, False, None)
        gv.copy_folder(self.gv.DOCX_PATH, self.gv.DOCX_OUT,False,None)

        # decompress the docx
        with zipfile.ZipFile(self.gv.INPUT_FILE_PATH, "r") as z:
            z.extractall(self.gv.DOCX_PATH)

        # copy  input file into the docx subfolder
        shutil.copy(self.gv.INPUT_FILE_PATH,self.gv.DOCX_PATH)

        # saxon converter
        java_command=self.saxon_doc2tei()
        print java_command
       
        subprocess.call(java_command, stdin=None, shell=True)
        
        #delete docx outfolder
        shutil.rmtree(self.gv.DOCX_OUT)
        
    



