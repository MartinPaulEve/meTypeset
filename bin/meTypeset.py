#!/usr/bin/env python
# @Author Dulip Withanage
# main file which triggers document parsing

"""meTypset: text parsing library to convert word documents to xml formats NLM, TEI

Usage:
    meTypeset.py [(-d | --debug)]   <input_file>  (-o | --output) <output_folder> [(-m | --metadata) (<metadata_file>)] [(-t | --test)]
    meTypeset.py (-h | --help)
    meTypeset.py (-t | --test)
    meTypeset.py --version

Options:

    -h --help  Show this screen.
    -t --test  Run the test suite.
    --version  Show version.
    -m --metadata  Metadata file
    -o --output   Output Folder

"""

from StringIO import StringIO
import argparse, os, subprocess, sys
from docx2tei import *
from tei2nlm import *
import os
from docopt import docopt
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
    


def set_metadata_file(settings ):
    metadata_file_arg = settings.args['<metadata_file>']
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
    global debug
    global test
    #Read  command line arguments
    args = docopt(__doc__, version='meTypset 0.1')
    
    debug = args['--debug']
    test = args['--test']
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
    
    # run tei to nlm conversion
    tei2nlm = TEI2NLM(gv)
    tei2nlm.run()

if __name__ == '__main__':
    main()
