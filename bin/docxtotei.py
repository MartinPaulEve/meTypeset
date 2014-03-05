#!/usr/bin/env python

import distutils
import os
import errno
import shutil
import zipfile
import subprocess
import re
import globals as gv

__author__ = "Dulip Withanage"
__email__ = "dulip.withanage@gmail.com"

from debug import Debuggable
from teimanipulate import TeiManipulate
from lxml import etree

class DocxToTei(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = gv.debug
        Debuggable.__init__(self, 'DOCX to TEI')

    def saxon_doc_to_tei(self):
        """
        Creates the appropriate java command to run Saxon
        @return: a string to run on the command line
        """
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

    def saxon_omml_to_mml(self):
        """
        Creates the appropriate java command to run Saxon
        @return: a string to run on the command line
        """
        cmd = ["java", "-classpath", self.gv.java_class_path,
               "-Dxml.catalog.files="+self.gv.runtime_catalog_path,
               "net.sf.saxon.Transform",
               "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader",
               "-y", "org.apache.xml.resolver.tools.ResolvingXMLReader",
               "-r",  "org.apache.xml.resolver.tools.CatalogResolver",
               "-o", self.gv.word_document_xml,
               self.gv.word_document_xml,
               self.gv.proprietary_style_sheet
               ]
        return ' '.join(cmd)

    def handle_wmf(self):
        """
        Calls unoconv to convert wmf images into png format. This method has a hard limit of 30 images.

        @return: False if fails (more than 30 images), True otherwise
        """
        image_filenames = os.listdir(self.gv.output_media_path)

        if len(image_filenames) > 30:
            self.debug.print_debug(self, u'Abandoning image conversion as there are over thirty images (DoS mitigation)')
            return False

        for image in image_filenames:
            if re.match(r'.+?\.wmf', image) is not None:
                image_name = re.sub(r'\.wmf', '', image)
                imagemagick_command = '{3}*DELIMITER*-d*DELIMITER*graphics*DELIMITER*-f*DELIMITER*png*DELIMITER*-o' \
                                      '*DELIMITER*{0}/{1}.png*DELIMITER*' \
                                      '{0}/{2}'.format(self.gv.output_media_path, image_name, image,
                                                       self.gv.settings.value_for_tag('unoconv',
                                                                                      self))
                self.debug.print_debug(self, u'Calling: {0}'.format(imagemagick_command.replace('*DELIMITER*', ' ')))

                subprocess.call(imagemagick_command.split('*DELIMITER*'))
        return True

    def clean_proprietary(self):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

        tree = etree.parse(self.gv.word_document_xml, p)

        omml = tree.xpath('//m:oMath', namespaces={'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math'})

        for omml_paragraph in omml:
            omml_paragraph.tag = '{http://www.w3.org/1998/Math/MathML}math'

        etree.strip_tags(tree, '{http://schemas.openxmlformats.org/officeDocument/2006/math}oMathPara')

        omml = tree.xpath('//m:oMathParaPr',
                          namespaces={'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math'})

        for omml_paragraph in omml:
            omml_paragraph.getparent().remove(omml_paragraph)

        tree.write(self.gv.word_document_xml)

    def run(self, extract, run_proprietary):
        """
        This method converts from docx to TEI. It creates the necessary output folders, optionally extracts the file and
        runs the Saxon process necessary to conduct the transform
        @param extract: whether or not to extract a docx file. True to extract, False to work on a pre-extracted folder
        @param run_proprietary: whether or not to run proprietary math transforms
        """

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

        if extract:
            # decompress the docx
            self.debug.print_debug(self, u'Unzipping {0} to {1}'.format(self.gv.input_file_path,
                                                                       self.gv.docx_temp_folder_path))

            with zipfile.ZipFile(self.gv.input_file_path, "r") as z:
                z.extractall(self.gv.docx_temp_folder_path)
        else:
            self.gv.copy_folder(self.gv.input_file_path, self.gv.docx_temp_folder_path)

        self.debug.print_debug(self, u'Looking for presence of media directory {0}'.format(self.gv.docx_media_path))

        if os.path.isdir(self.gv.docx_media_path):
            self.debug.print_debug(self, u'Ripping out media directory')

            self.gv.mk_dir(self.gv.output_media_path)
            self.gv.copy_folder(self.gv.docx_media_path, self.gv.output_media_path, False, None)

            self.handle_wmf()

        # copy input file into the docx subfolder
        if extract:
            shutil.copy(self.gv.input_file_path, self.gv.docx_temp_folder_path)
        else:
            pass
            #self.gv.tei_file_path = self.gv.tei_file_path + 'tei.xml'

        if run_proprietary:
            # run a transform on the copied docx to generate a new version of the Word XML that includes MML
            java_command = self.saxon_omml_to_mml()
            self.debug.print_debug(self, u'Running saxon transform (DOCX->MML DOCX) [proprietary]')
            subprocess.call(java_command, stdin=None, shell=True)
            self.clean_proprietary()

        # saxon converter
        java_command = self.saxon_doc_to_tei()
        self.debug.print_debug(self, u'Running saxon transform (DOCX->TEI)')
        subprocess.call(java_command, stdin=None, shell=True)

        # delete temp folders
        if not self.gv.debug.debug:
            shutil.rmtree(self.gv.docx_temp_folder_path)
            shutil.rmtree(self.gv.common2_temp_folder_path)
