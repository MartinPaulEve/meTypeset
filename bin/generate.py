#!/usr/bin/env python
# @Author Dulip Withanage
# main file which triggers document parsing

#---------------------------------------------------------------------------------------------------------
from StringIO import StringIO
import argparse, os, subprocess, sys
from docx2tei import *
import docx2tei
import os
import globals as g

    
# check whether lxml is installed
try:
    from lxml import etree
except ImportError:
    print("Failed to import lxml")



class SettingsConfiguration:
    def __init__(self, set_file, args):
        tree                    = etree.parse(set_file)
        self.tree               = tree
        self.script_dir         = os.environ['METYPESET']
        self.args               = args
        self.settings_file      = set_file
    
    

def read_commad_line():
    p = argparse.ArgumentParser(description='This program takes an input  word document and converts that into xml formats (NLM, TEI)')
    p.add_argument('input_file', nargs=1, help='Name of the docx file')
    p.add_argument("--output_folder","-o", nargs=1, help="outpout folder name",  required=True)
    p.add_argument("--type","-t", nargs=1, help="type of the result file, default is nlm")
    p.add_argument("--metadata_file","-m", nargs=1, help="optional metadata file")
    p.add_argument("--xslt_processor","-p", nargs=1, help="processing engine, default is saxon")
    return  p.parse_args()



def set_metadata_file(settings ):
    metadata_file_arg = settings.args.metadata_file
    if  metadata_file_arg:
        metadata_file = g.clean_path(g.concat_path(settings.script_dir,+metadata_file_arg[0]))
    else:
        metadata_file = g.clean_path(g.concat_path(settings.script_dir, g.value_for_tag(settings,'default-metadata-file-path')))
        print("WARNING: metadata file wasn't specified. Falling back to "+metadata_file+".")
    return metadata_file


def get_settings_file():
    # read  the home folder, either from the path or from the settings file
    try:
        script_dir = os.environ['METYPESET']
    except:
	try:
		path = os.path.dirname(docx2tei.__file__)
		script_dir = os.path.dirname(path + "/../")
		os.environ['METYPESET'] = script_dir
	except:
	        print_message_and_exit("$METYPESET path not variable is not set and/or was unable to determine runtime path.")
        
    set_file = script_dir+"/bin/settings.xml"
    try:
        os.path.isfile(set_file)
    except:
        print_message_and_exit(set_file + " does not exist")
        
    return set_file


def main():
    #Read  command line arguments
    args = read_commad_line()
    #read settings file #make settings object
    settings = SettingsConfiguration(get_settings_file(), args)
    
    # set global variables
    gv = g.GV(settings)
     
    #check for stylesheets
    
    g.check_file_exists(gv.DOCX_STYLE_SHEET_DIR)
    
    # metadata file
    metadata_file = set_metadata_file(settings)
    
    #get saxon lib class path
    java_class_path = g.set_java_classpath(gv)
    
    # rund docx to tei conversion
    docx2tei = Docx2TEI(gv)
    docx2tei.run()
    

    # rund tei to nlm conversion
    #tei2nlm = TEI2NLM(settings,args).run()

if __name__ == '__main__':
    main()
