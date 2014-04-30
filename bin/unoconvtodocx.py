#!/usr/bin/env python

import distutils
import os
import errno
import shutil
import zipfile
import subprocess
import re
import globals as gv

__author__ = "Martin Eve, Dulip Withanage"
__email__ = "martin@martineve.com"

from debug import Debuggable
from teimanipulate import TeiManipulate
from lxml import etree

class DocToDocx(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = gv.debug
        Debuggable.__init__(self, 'DOC to DOCX')

    def doc_to_docx(self):
        """
        Creates the appropriate java command to run Saxon
        @return: a string to run on the command line
        """
        cmd = ["unoconv", "-f", "docx",
               "-o", os.path.join(self.gv.doc_folder_path, 'new.docx'),
               self.gv.input_file_path
               ]
        return ' '.join(cmd)

    def run(self):
        """
        This method converts from docx to TEI. It creates the necessary output folders, optionally extracts the file and
        runs the Saxon process necessary to conduct the transform
        @param extract: whether or not to extract a docx file. True to extract, False to work on a pre-extracted folder
        @param run_proprietary: whether or not to run proprietary math transforms
        """

        # make output folders
        self.gv.mk_dir(self.gv.doc_folder_path)

        unoconv_command = self.doc_to_docx()

        self.debug.print_debug(self, u'Running unoconv transform (DOC->DOCX)')
        subprocess.call(unoconv_command, stdin=None, shell=True)

        self.gv.input_file_path = os.path.join(self.gv.doc_folder_path, 'new.docx')

        # delete temp folders
        if not self.gv.debug.debug:
            shutil.rmtree(self.gv.doc_folder_path)
