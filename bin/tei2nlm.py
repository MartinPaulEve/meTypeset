#!/usr/bin/env python
# @Author Dulip Withanage

import generate as g
import docx2tei as d2t

class TEI2NLM :
    def __init__(self, settings,args):
        self.settings = settings
        self.args = args
        self.script_dir = os.environ['METYPESET']
    
    
    def saxon_tei2nlm(self, java_class_path,runtime_catalog ,output_path,input_path,tei_to_nlm_stylesheet):
        cmd = ["java", "-classpath", java_class_path, \
                    "-Dxml.catalog.files="+runtime_catalog,\
                    "net.sf.saxon.Transform", \
                    "-x", "org.apache.xml.resolver.tools.ResolvingXMLReader", \
                    "-y" ,"org.apache.xml.resolver.tools.ResolvingXMLReader", \
                    "-r",  "org.apache.xml.resolver.tools.CatalogResolver", \
                    "-o", output_path ,\
                    input_path,\
                    tei_to_nlm_stylesheet,\
                    "autoBlockQuote=true"
            ]
        return ' '.join(cmd)



    def run():
       runtime_catalog =  self.settings.runtime_catalog 
       java_command=self.saxon_tei2nlm(g.set_java_classpath(self.settings, self.script_dir),runtime_catalog, output_path, input_path, tei_to_nlm_stylesheet)
       subprocess.call(java_command, stdin=None, shell=True)
        
    


