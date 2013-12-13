#!/usr/bin/env python
#@Author Dulip Withanage
import globals as gv
import subprocess
import shutil


class TEI2NLM:
    def __init__(self, gv):
        self.gv = gv

    def saxon_tei2nlm(self):
            cmd = ["java", "-classpath", self.gv.JAVA_CLASS_PATH,
                   "-Dxml.catalog.files=" + self.gv.RUNTIME_CATALOG_PATH,
                   "net.sf.saxon.Transform",
                   "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-y", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-r", "org.apache.xml.resolver.tools.CatalogResolver",
                   "-o", self.gv.NLM_TEMP_FILE_PATH,
                   self.gv.TEI_FILE_PATH,
                   self.gv.NLM_STYLE_SHEET_DIR,
                   'autoBlockQuote=true'
                   ]
            return ' '.join(cmd)

    def run(self):
        #assumes ouput path exists after tei conversion
        gv.mk_dir(self.gv.NLM_FOLDER_PATH)
        java_command = self.saxon_tei2nlm()
        print "INFO: Running saxon transform (TEI->NLM)"
        subprocess.call(java_command, stdin=None, shell=True)
        shutil.copy2(self.gv.NLM_TEMP_FILE_PATH,self.gv.NLM_FILE_PATH )
