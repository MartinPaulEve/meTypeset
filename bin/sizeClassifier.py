#!/usr/bin/env python
from lxml import etree
from lxml import objectify
from copy import deepcopy
import uuid
import globals  as gv
import os
from manipulate import *
import subprocess
import shutil
import re

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

'''
A class that scans for meTypeset size fields in a TEI file.

1.) Identifies a list of sizes
2.) Ascertains the density and likelihood of the size being a heading
3.) Returns a manipulator ready to implement all the changes to the TEI file to incorporate this information as nested title tags

'''
class sizeClassifier():
    def __init__(self, gv):
        self.gv = gv

    def addToList(self, list_to_add_to, str_to_add):
    	if str_to_add not in list_to_add_to:
    	    list_to_add_to.append(str_to_add)

    def get_values(self, tree, search_attribute):
		# this function searches the DOM tree for TEI "hi" elements with the specified search_attribute
		sizes = []
		for child in tree.xpath("//tei:hi[@" + search_attribute + "=not('')]", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
			self.addToList(sizes, child.get(search_attribute))

		return sizes

    def set_dom_tree(self, filename):
			p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

			return etree.parse(filename, p)    
       
    def run(self):
			# load the DOM
		  	tree = self.set_dom_tree(self.gv.TEI_FILE_PATH)

			# get a numerical list of explicit size values inside meTypesetSize attributes
			sizes = self.get_values(tree, "meTypesetSize")
	
			if self.gv.debug:
				print "Explicitly specified size variations:"
				print sizes

			# depending on the length of the array we will feed parse differently

			if len(sizes) == 1:
				if self.gv.debug:
					print "Found single case heading"
		
			if len(sizes) > 0:
				manipulate = Manipulate(self.gv)

				# instruct the manipulator to change the parent tag of every tag it finds containing 
				# a "hi" tag with meTypesetSize set to the value found to "title"
				# so, for example <p><hi meTypesetSize="18">some text</hi></p>
				# will be transformed to
				# <title><hi meTypesetSize="18">some text</hi></title>
				manipulate.change_outer("//tei:hi[@meTypesetSize='" + sizes[0] + "']", "head")
	


