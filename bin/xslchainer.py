#!/usr/bin/env python
__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"
import subprocess
import shutil
from nlmmanipulate import NlmManipulate
from debug import Debuggable


class XslChain (Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.module_name = "XSL Post-Chainer"
        self.debug = gv.debug
        super(Debuggable, self).__init__()

    def saxon_arbitrary_xsl(self):
            cmd = ["java", "-classpath", self.gv.java_class_path,
                   "-Dxml.catalog.files=" + self.gv.runtime_catalog_path,
                   "net.sf.saxon.Transform",
                   "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-y", "org.apache.xml.resolver.tools.ResolvingXMLReader",
                   "-r", "org.apache.xml.resolver.tools.CatalogResolver",
                   "-o", self.gv.xsl_file_path,
                   self.gv.nlm_file_path,
                   self.gv.settings.args['--chain'],
                   'autoBlockQuote=true'
                   ]
            return ' '.join(cmd)

    def run_transform(self):
        self.gv.mk_dir(self.gv.xsl_folder_path)
        java_command = self.saxon_arbitrary_xsl()
        print(java_command)
        self.debug.print_debug(self, u'Running saxon transform (XSL CHAIN)')
        subprocess.call(java_command, stdin=None, shell=True)

    def run(self):
        self.run_transform()
