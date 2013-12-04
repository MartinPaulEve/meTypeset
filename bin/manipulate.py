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

    def search_and_replace(self, tree, search_section, search_element, surround_with):
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

    def run(self):
        #create element tree
        tree = etree.parse(self.gv.NLM_TEMP_FILE_PATH)
        #tree = self.search_and_replace(tree,"sec","p","title")

        tree.write(self.gv.NLM_FILE_PATH, xml_declaration=True, encoding='utf-16')
