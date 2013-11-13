#!/usr/bin/env python
# @Author Dulip Withanage
# main file which triggers document parsing

#---------------------------------------------------------------------------------------------------------
from StringIO import StringIO
import argparse, os, subprocess, sys
from docx2tei import *


    
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
       


def clean_path(path):
     return path.replace('\n ','').replace(" ", "").replace("//","/")
 


def value_for_tag(settings,tag_name):
    expr = "//*[local-name() = $name]"
    tag = settings.tree.xpath(expr, name=tag_name, namespaces={'mt':'https://github.com/MartinPaulEve/meTypeset'})
    return  tag[0].text if tag   else print_message_and_exit("ERROR: "+tag_name + "  is  not define in settings")
    


def concat_path(parent, child):
    #print parent, child
    return parent + '/' +child


def check_file_exists(file_path):
    if file_path is None:
        print_message_and_exit("file path "" is invalid")
    try:
        os.path.isfile(file_path)
    except:
        print_message_and_exit("ERROR: Unable to locate " + file_path)
            
 
def print_message_and_exit(mess):
    print(mess)
    sys.exit(0)
    
    
    

def read_commad_line():
    p = argparse.ArgumentParser(description='This program takes an input  word document and converts that into xml formats (NLM, TEI)')
    p.add_argument('input_file', nargs=1, help='Name of the docx file')
    p.add_argument("--output_folder","-o", nargs=1, help="outpout folder name",  required=True)
    p.add_argument("--type","-t", nargs=1, help="type of the result file, default is nlm")
    p.add_argument("--metadata_file","-m", nargs=1, help="optional metadata file")
    p.add_argument("--xslt_processor","-p", nargs=1, help="processing engine, default is saxon")
    return  p.parse_args()



def set_metadata_file(args, script_dir, settings ):
    metadata_file_arg = args.metadata_file
    if  metadata_file_arg:
        metadata_file=concat_path(script_dir,+metadata_file_arg[0])
    else:
        metadata_file =  concat_path(script_dir,value_for_tag(settings,'default-metadata-file-path'))
        print("WARNING: metadata file wasn't specified. Falling back to "+metadata_file+".")
    return metadata_file


def get_settings_file():
    # read  the home folder, either from the path or from the settings file
    try:
        script_dir = os.environ['METYPESET']
    except:
        print_message_and_exit("$METYPESET path not variable is not set")
        
    set_file = script_dir+"/bin/settings.xml"
    try:
        os.path.isfile(set_file)
    except:
        print_message_and_exit(set_file + " does not exist")
        
    return set_file
def set_java_classpath(settings, script_dir):
    java_class_path = ''
    runtime_dir = concat_path(script_dir,value_for_tag(settings,'runtime'))
    for  lib in value_for_tag(settings,'saxon-libs').strip().split(";"):
        check_file_exists(concat_path(runtime_dir,lib))
        java_class_path     += concat_path(runtime_dir, lib)
        java_class_path     += ":"
    return  '"'+java_class_path.rstrip(':')+'"'

        

def main():
    #Read  command line arguments
    args = read_commad_line()
    
    #read settings file
    script_dir= get_settings_file()
    
    #make settings object
    settings = SettingsConfiguration (script_dir, args)
        
    #check for stylesheets
    docx_style_sheet_dir = concat_path(script_dir, value_for_tag(settings,'docs-style-sheet-path'))
    check_file_exists(docx_style_sheet_dir)
     
    
    # metadata file
    metadata_file = set_metadata_file(args, script_dir, settings )
    
    #get saxon lib class path
    java_class_path =set_java_classpath(settings, script_dir)
    
        
    # rund docx to tei conversion
    docx2tei = Docx2TEI(settings,args).run()
    

    # rund tei to nlm conversion
    #tei2nlm = TEI2NLM(settings,args).run()

if __name__ == '__main__':
    main()
