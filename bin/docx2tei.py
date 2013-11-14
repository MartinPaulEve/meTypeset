#!/usr/bin/env python
# @Author Dulip Withanage

import distutils, os, errno
import shutil, zipfile, subprocess
import generate as g
import os

class Docx2TEI :
    def __init__(self, settings,args):
        self.settings = settings
        self.args = args
        self.script_dir = os.environ['METYPESET']

    def mk_dir(self, path):
        try :
            os.makedirs(path)
        except:
            g.print_message_and_exit(path +' exists')

    def copy_folder(self, src, dst, symlinks=False, ignore=None):

        for item in os.listdir(src):
            s = str(os.path.join(src, item))
            d = str(os.path.join(dst, item))


            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                #print s ,d
                shutil.copy(s, d)

    def generate_input_path(self, setting, tag):
        return g.clean_path(g.concat_path(self.script_dir, g.value_for_tag(self.settings,tag)))

    def generate_output_path(self, setting, tag, output_folder):
        return g.clean_path(g.concat_path(output_folder, g.value_for_tag(self.settings,tag)))

   
    def saxon_doc2tei(self, java_class_path,runtime_catalog ,output_path,word_document_xml,doc_to_tei_stylesheet):
        cmd = ["java", "-classpath", java_class_path, \
                    "-Dxml.catalog.files="+runtime_catalog,\
                    "net.sf.saxon.Transform", \
                    "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader", \
                    "-y" ,"org.apache.xml.resolver.tools.ResolvingXMLReader", \
                    "-r",  "org.apache.xml.resolver.tools.CatalogResolver", \
                    "-o", output_path ,\
                    word_document_xml,\
                    doc_to_tei_stylesheet
            ]
        return ' '.join(cmd)


    def  run(self):

        docx ='docx'
        common2='common2'

        #input folders
        runtime_dir           = self.generate_input_path(self.settings,'runtime')
        input_file_path       = self.args.input_file[0].strip()
        common2_path          = self.generate_input_path(self.settings,common2)
        binary_dir            = self.generate_input_path(self.settings,'binaries')
        docx_path             = self.generate_input_path(self.settings,docx)
        runtime_catalog       = self.generate_input_path(self.settings,'runtime-catalog')

        #output folders
        output_folder           = os.path.expanduser(self.args.output_folder[0])
        docx_out                = self.generate_output_path(self.settings, docx, output_folder)
        common2_out             = self.generate_output_path(self.settings,common2, output_folder)
        word_document_xml       = g.clean_path(docx_out+'/'+g.value_for_tag(self.settings,'word-document-xml'))
        doc_to_tei_stylesheet   = g.clean_path(docx_out+'/'+g.value_for_tag(self.settings,'doc-to-tei-stylesheet'))
        tei_file_path           = g.clean_path(output_folder+'/'+g.value_for_tag(self.settings,'tei'))

        #tei_file_name
        sep=input_file_path.rsplit('/')

        tei_file_name =   sep[len(sep)-1].replace('docx','xml').replace('doc','xml') if '/' in input_file_path  else input_file_path.replace('docx','xml').replace('doc','xml')

       
        # make output folders
        self.mk_dir(output_folder)
        self.mk_dir(docx_out)
        self.mk_dir(common2_out)
        self.mk_dir(tei_file_path)

        #copy folders
        self.copy_folder(common2_path, common2_out, False, None)
        self.copy_folder(docx_path, docx_out,False,None)

        # decompress the docx
        with zipfile.ZipFile(input_file_path, "r") as z:
            z.extractall(docx_path)


        # copy  input file into the docx subfolder
        shutil.copy(input_file_path,docx_path)

        # saxon converter
        java_command=self.saxon_doc2tei(g.set_java_classpath(self.settings, self.script_dir),runtime_catalog , tei_file_path+'/'+tei_file_name,word_document_xml,doc_to_tei_stylesheet)
       
        subprocess.call(java_command, stdin=None, shell=True)
        
        #delete docx outfolder
        shutil.rmtree(docx_out)
        
    



