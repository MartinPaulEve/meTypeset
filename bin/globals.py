#!/usr/bin/env python
# @Author Dulip Withanage


import os, sys, shutil
from debug import *

# class Global Variables
class GV:
   
    def __init__(self, settings):
            docx ='docx'
            common2='common2'
            nlm = 'nlm'
            
            self.settings                       = settings
            
            self.SCRIPT_DIR                     = os.environ['METYPESET']
            
            self.INPUT_FILE_PATH                = settings.args['<input_file>'].strip()
            self.INPUT_METADATA_FILE_PATH       = settings.args['<metadata_file>'] if settings.args['<metadata_file>'] else settings.script_dir+value_for_tag(settings,'default-metadata-file-path')

            filename_sep                        = self.INPUT_FILE_PATH.rsplit('/')
            self.OUTPUT_FOLDER_PATH             = os.path.expanduser(settings.args['<output_folder>'])

            self.debug                          = Debug(self)

            #general directory paths
            self.RUNTIME_FOLDER_PATH            = generate_path(settings,'runtime', settings.script_dir)
            self.COMMON2_LIB_PATH               = generate_path(settings,common2, settings.script_dir)
            self.BINARY_FOLDER_PATH             = generate_path(settings,'binaries', settings.script_dir)
            self.RUNTIME_CATALOG_PATH           = generate_path(settings,'runtime-catalog', settings.script_dir)
            self.COMMON2_TEMP_FOLDER_PATH       = generate_path(settings,common2, self.OUTPUT_FOLDER_PATH)
            
            
            # docx document paths
            self.DOCX_FOLDER_PATH               = generate_path(settings,docx ,settings.script_dir)
            self.DOCX_TEMP_FOLDER_PATH          = generate_path(settings, docx, self.OUTPUT_FOLDER_PATH)
            self.DOCX_WORD_TEMP_FOLDER_PATH     = clean_path(concat_path(self.DOCX_TEMP_FOLDER_PATH , value_for_tag(settings,'word')))
            self.WORD_DOCUMENT_XML              = clean_path(self.DOCX_TEMP_FOLDER_PATH+'/'+value_for_tag(settings,'word-document-xml'))
            self.DOCX_STYLE_SHEET_DIR           = concat_path(self.SCRIPT_DIR , value_for_tag(settings,'docs-style-sheet-path'))
            self.DOC_TO_TEI_STYLESHEET          = clean_path(self.DOCX_TEMP_FOLDER_PATH+'/'+value_for_tag(settings,'doc-to-tei-stylesheet'))
            self.DOCX_MEDIA_PATH                = clean_path(concat_path(self.DOCX_WORD_TEMP_FOLDER_PATH , value_for_tag(settings,'media')))
            self.OUTPUT_MEDIA_PATH              = clean_path(concat_path(self.OUTPUT_FOLDER_PATH , value_for_tag(settings,'outputmedia')))
            
            #OUTPUT FILE
            self.FILE_NAME                      = filename_sep[len(filename_sep)-1].replace('docx','xml').replace('doc','xml') if '/' in self.INPUT_FILE_PATH \
                                                    else self.INPUT_FILE_PATH.replace('docx','xml').replace('doc','xml')
            #TEI paths
            self.TEI_FOLDER_PATH                = clean_path(self.OUTPUT_FOLDER_PATH+'/'+value_for_tag(settings,'tei'))
            self.TEI_FILE_PATH                  = concat_path( self.TEI_FOLDER_PATH, self.FILE_NAME)
            self.TEI_TEMP_FILE_PATH             = clean_path(concat_path(self.TEI_FOLDER_PATH , "out.xml"))
            
            #NLM paths
            self.NLM_FOLDER_PATH                = generate_path(settings,nlm ,self.OUTPUT_FOLDER_PATH)
            self.NLM_FILE_PATH                  = clean_path(concat_path(self.NLM_FOLDER_PATH , self.FILE_NAME))
            self.NLM_TEMP_FILE_PATH             = clean_path(concat_path(self.NLM_FOLDER_PATH , "out.xml"))
            self.NLM_STYLE_SHEET_DIR            = clean_path(concat_path(settings.script_dir , value_for_tag(settings,'tei-to-nlm-stylesheet')))

            #Metadata paths
            self.METADATA_STYLE_SHEET_PATH       = clean_path(concat_path(settings.script_dir , value_for_tag(settings,'metadata-stylesheet')))

            #java classes for saxon
            self.JAVA_CLASS_PATH                = set_java_classpath(self)



def check_file_exists(file_path):
    if file_path is None:
        print_message_and_exit("file path "" is invalid")
    try:
        os.path.isfile(file_path)
    except:
        print_message_and_exit("ERROR: Unable to locate " + file_path)
            

def generate_path( settings, tag, path):
    return clean_path(concat_path(path, value_for_tag(settings,tag)))


# global functions for setting variables        
def value_for_tag(settings,tag_name):
    expr = "//*[local-name() = $name]"
    tag = settings.tree.xpath(expr, name=tag_name, namespaces={'mt':'https://github.com/MartinPaulEve/meTypeset'})
    return  clean_path(tag[0].text) if tag   else print_message_and_exit("ERROR: "+tag_name + "  is  not defined in settings.xml")


def print_message_and_exit(mess):
    print(mess)
    sys.exit(0)
    
    
def mk_dir( path):
        try :
            os.makedirs(path)
        except:
            print_message_and_exit(path +' exists')


def copy_folder(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = str(os.path.join(src, item))
        d = str(os.path.join(dst, item))
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            #print s ,d
            shutil.copy(s, d)


    
def concat_path(parent, child):
    return parent + os.sep + '/' +child

def clean_path(path):
    #TODO: cross-platform fix?
    path = ''.join(path.split())
    return path.replace('\n ','').replace(" ", "").replace("//","/")


def set_java_classpath(self):
    java_class_path = ''
    #runtime_dir = concat_path(script_dir,value_for_tag(settings,'runtime'))
    for  lib in value_for_tag(self.settings,'saxon-libs').strip().split(";"):
        check_file_exists(concat_path(self.RUNTIME_FOLDER_PATH,lib))
        java_class_path     += concat_path(self.RUNTIME_FOLDER_PATH, lib)
        java_class_path     += ":"
    return  '"'+java_class_path.rstrip(':')+'"'
