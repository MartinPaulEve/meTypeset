#!/usr/bin/env python
#@Author Dulip Withanage
import subprocess
import shutil
from nlmmanipulate import NlmManipulate
from debug import Debuggable


class TEI2NLM (Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.module_name = "TEI to NLM"
        self.debug = gv.debug
        super(Debuggable, self).__init__()

    def saxon_tei2nlm(self):
            cmd = ["java", "-classpath", self.gv.java_class_path,
                   "-Dxml.catalog.files=" + self.gv.runtime_catalog_path,
                   "net.sf.saxon.Transform",
                   "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-y", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-r", "org.apache.xml.resolver.tools.CatalogResolver",
                   "-o", self.gv.nlm_temp_file_path,
                   self.gv.tei_file_path,
                   self.gv.nlm_style_sheet_dir,
                   'autoBlockQuote=true'
                   ]
            return ' '.join(cmd)

    def run_quirks(self):
        manipulate = NlmManipulate(self.gv)
        if self.gv.setting('linebreaks-as-comments') == 'False':
            # we need to convert every instance of <!--meTypeset:br--> to a new paragraph
            manipulate.close_and_open_tag('comment()[. = "meTypeset:br"]', 'p')

        # we will replace inside table cells and titles regardless because these are real JATS break tags
        manipulate.insert_break('comment()[. = "meTypeset:br"]', 'td')
        manipulate.insert_break('comment()[. = "meTypeset:br"]', 'title')

        manipulate.tag_inline_refs()
        manipulate.find_reference_list()
        manipulate.tag_bibliography_refs()

    def run_transform(self):
        self.gv.mk_dir(self.gv.nlm_folder_path)
        java_command = self.saxon_tei2nlm()
        self.debug.print_debug(self, 'Running saxon transform (TEI->NLM)')
        subprocess.call(java_command, stdin=None, shell=True)

        if self.gv.nlm_temp_file_path != self.gv.nlm_file_path:
            shutil.copy2(self.gv.nlm_temp_file_path, self.gv.nlm_file_path)

    def run(self):
        self.run_transform()
        self.run_quirks()
