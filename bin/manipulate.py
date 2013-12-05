#!/usr/bin/env python
from lxml import etree
from copy import deepcopy
import uuid
import globals  as gv
import os
import subprocess, shutil

__author__ = "Dulip Withanage"
__email__ = "dulip.withanage@gmail.com"

class Manipulate():
    def __init__(self, gv):
        self.gv = gv

    def search_and_replace_dom(self, tree, search_section, search_element, surround_with):
        for p  in tree.xpath(".//"+search_section):
            prgs = p.findall(".//"+search_element)
            i = 0
            for  prg in prgs:
                i += 1
                new_elem = etree.Element(surround_with)
                new_elem.set("order",str(i))
                new_elem.set("uuid",str(uuid.uuid4()))
                if len(prg)>0:
                    elem_copy  = deepcopy (prg[0])
                    prg.clear()
                    new_elem.append(elem_copy)
                    prg.append(new_elem)
                else:
                    new_elem.text = prg.text
                    prg.clear()
                    prg.append(new_elem)
        return tree

    def set_dom_tree(self, filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
        return etree.parse(filename, p)

    def write_out_put(self, tree):
        tree.write(self.gv.NLM_FILE_PATH, xml_declaration=True, encoding='utf-16')

    def update_tmp_file(self):
        shutil.copy2(self.gv.NLM_FILE_PATH,self.gv.NLM_TEMP_FILE_PATH)

    def  get_file_text(self, filename):
        f = open(filename)
        text= f.read()
        f.close()
        return text

    def xml_start(self, tag):
        return '<'+tag+'>'

    def xml_end(self, tag):
        return '</'+tag+'>'
    #replaces a  given tag with a list of replace tags
    def replace(self, text, tag ,*params):
        replace_start = ''
        replace_end = ''

        if len(params)>0:
            for i in params:
                replace_start   +=  self.xml_start(i)
                replace_end     +=  self.xml_end(i)

            text = text.replace(self.xml_start(tag),replace_start).replace(self.xml_end(tag),replace_end)

        else:
            print 'INFO: no parameters given'
        return text


    def run_dom(self):
        tree = self.set_dom_tree(self.gv.NLM_TEMP_FILE_PATH)
        tree = self.search_and_replace_dom(tree,"sec", "p","title")
        self.write_out_put(tree)
        self.update_tmp_file()

    def write_output(self, text):
        out = open(self.gv.NLM_FILE_PATH,'w')
        out.write(text)
        out.close()

    def run(self):
        text = self.get_file_text(self.gv.NLM_TEMP_FILE_PATH)

        search_tag = 'p'
        replace_tag = ['div','sec']
        text = self.replace(text,search_tag,*replace_tag)


        self.write_output(text)
        self.update_tmp_file()
