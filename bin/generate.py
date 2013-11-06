#!/usr/bin/env python
# @Author Dulip Withanage
# main file which triggers document parsing


#---------------------------------------------------------------------------------------------------------
from StringIO import StringIO
import optparse, os

# check whether lxml is installed
try:
    from lxml import etree
except ImportError:
    print("Failed to import lxml")

# Settings are  saved to a python Object
class SettingsConfiguration:
    def __init__(self, set_file):
        tree = etree.parse(set_file)
        self.tree = tree

    def value_for_tag(self,settings,tag_name):
        expr = "//*[local-name() = $name]"
        return settings.tree.xpath(expr, name=tag_name, namespaces={'mt':'https://github.com/MartinPaulEve/meTypeset'})[0].text

def main():
    set_file = "settings.xml"
    if  not os.path.isfile(set_file):
        raise Exception(set_file + " does not exist")
    settings = SettingsConfiguration (set_file)
    root = settings.tree.getroot()
    
    usage = 'usage: generate.py [<options>] inputfile\n \
            options = [-t|--type <type>] [-f|--metadata-file  <output folder>] \
            [-m|--metadata-file <metadatafile> ] [ -p|--xslt-processor <xslt-processor> '
    
    p = optparse.OptionParser()
    #read command line options
    p.add_option('--type', '-t', default="NLM", help='')
    p.add_option('--metadata-file', '-m', default="")
    p.add_option('--xslt-processor', '-p', default="saxon")
    p.add_option('--folder', '-f', default="")
    
    
    
    #set command line options
    options, arguments = p.parse_args()
    
    

    output_folder = settings.value_for_tag(settings,'default-output-folder')
    docx_folder = settings.value_for_tag(settings,'docx-folder')
    tei_folder = settings.value_for_tag(settings,'tei-folder')
    nlm_folder = settings.value_for_tag(settings,'nlm-folder')
    multimedia_folder = settings.value_for_tag(settings,'multimedia-folder')




if __name__ == '__main__':
    main()
