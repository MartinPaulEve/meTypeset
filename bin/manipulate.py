#!/usr/bin/env python
from lxml import etree
from lxml import objectify
from copy import deepcopy
import uuid
import globals as gv
import os
import subprocess
import shutil
import re

__author__ = "Dulip Withanage"
__email__ = "dulip.withanage@gmail.com"

class Manipulate():
	def __init__(self, gv):
		self.gv = gv

	def search_and_replace_dom(self, tree, search_section, search_element, surround_with):
		for p in tree.xpath(".//"+search_section):
			prgs = p.findall(".//"+search_element)
			i = 0
			for prg in prgs:
				i += 1
				new_elem = etree.Element(surround_with)
				new_elem.set("order",str(i))
				new_elem.set("uuid",str(uuid.uuid4()))
				if len(prg)>0:
					elem_copy = deepcopy (prg[0])
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


	def update_tmp_file(self,fr,to):
		shutil.copy2(fr,to)

	def get_file_text(self, filename):
		f = open(filename)
		text= f.read()
		f.close()
		return text

	def xml_start(self, tag):
		return '<'+tag+'>'

	def xml_end(self, tag):
		return '</'+tag+'>'
	#replaces a given tag with a list of replace tags
	def replace(self, text, tag ,*params):
		replace_start = ''
		replace_end = ''

		if len(params)>0:
			for i in params:
				replace_start += self.xml_start(i)
				replace_end	 += self.xml_end(i)

			text = text.replace(self.xml_start(tag),replace_start).replace(self.xml_end(tag),replace_end)

		else:
			print 'INFO: no parameters given'
		return text

	def replace_text_(self, xml_start, xml_end ,text):
		text = text.replace()
		return text
	

	def run_dom(self, f):
		tree = self.set_dom_tree(f)
		tree = self.search_and_replace_dom(tree,"sec", "p","title")
		self.write_out_put(tree)
		self.update_tmp_file()

	def write_output(self, f, text):
		out = open(f,'w')
		out.write(text)
		out.close()

	# Returns the value after a searching a list of regex or None if nothing found.
	def try_list_of_regex(self, filestring, *regex):
		if len(regex)>0:
			for i in regex:
				val = re.findall(filestring, i)
				if val:
					return val
			return None
		else:
			return None
	#replaces the 
	def replace_value_of_tag(self, text, new_value):
		 obj = objectify.fromstring(text)
		 obj.teiHeader.fileDesc.titleStmt.title._setText(new_value)
		 return etree.tostring(obj.getroottree())
		
	def tag_headings(self):
		# load the DOM
		self.update_tmp_file(self.gv.TEI_FILE_PATH,self.gv.TEI_TEMP_FILE_PATH)
		tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

		iterator = 0

		# search the tree and grab the parent
		for child in tree.xpath("//tei:head", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
			child.attrib['meTypesetHeadingID'] = str(iterator)
			iterator = iterator + 1

		tree.write(self.gv.TEI_FILE_PATH)
	

	# changes the parent element of the outer_xpath expression to the new_value	
	def change_outer(self, outer_xpath, new_value, size_attribute):
		# load the DOM
		self.update_tmp_file(self.gv.TEI_FILE_PATH,self.gv.TEI_TEMP_FILE_PATH)
		tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

		# search the tree and grab the parent
		for child in tree.xpath(outer_xpath + "/..", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
			child.tag = new_value
			child.attrib['meTypesetSize'] = size_attribute

		tree.write(self.gv.TEI_FILE_PATH)
	 
	def move_size_div(self, headingID, siblingID):
		# load the DOM
		self.update_tmp_file(self.gv.TEI_FILE_PATH,self.gv.TEI_TEMP_FILE_PATH)
		tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

		nodeToMove = tree.xpath("//tei:head[@meTypesetHeadingID='" + str(headingID) + "']/..", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
		nodeToMoveTo = tree.xpath("//tei:head[@meTypesetHeadingID='" + str(siblingID) + "']/..", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]

		nodeToMoveTo.addnext(nodeToMove)		

		tree.write(self.gv.TEI_FILE_PATH)

	def downsize_headings(self, rootSize, size):
		# load the DOM
		self.update_tmp_file(self.gv.TEI_FILE_PATH,self.gv.TEI_TEMP_FILE_PATH)
		tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

		nodesToDownsize = tree.xpath("//tei:head[@meTypesetSize='" + str(size) + "']", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
		for nodeToDownsize in nodesToDownsize:
			nodeToDownsize.attrib['meTypesetSize'] = rootSize

		tree.write(self.gv.TEI_FILE_PATH)
		

	def enclose(self, start_xpath, select_xpath):
		# load the DOM
		self.update_tmp_file(self.gv.TEI_FILE_PATH,self.gv.TEI_TEMP_FILE_PATH)
		tree = self.set_dom_tree(self.gv.TEI_TEMP_FILE_PATH)

		node = tree.xpath(start_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
		div = etree.Element('div')
		node.addprevious(div)

		if self.gv.debug:
			print "Grabbing: " + select_xpath


		# search the tree and grab the elements
		child = tree.xpath(select_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
		
		# move the elements
		for element in child:
			div.append(element)

		tree.write(self.gv.TEI_FILE_PATH)

	def run(self):
		self.update_tmp_file(self.gv.TEI_FILE_PATH,self.gv.TEI_TEMP_FILE_PATH)
		text = self.get_file_text(self.gv.TEI_TEMP_FILE_PATH)
		text = self.replace_value_of_tag(text,'ssssssssss')
		self.write_output(self.gv.TEI_FILE_PATH, text)
		os.remove(self.gv.TEI_TEMP_FILE_PATH)


		'''
		string replace example
		search_tag = 'p'
		replace_tag = ['div','sec']
		text = self.replace(text,search_tag,*replace_tag)
		'''

		'''
		Regex finding example
		regex_list = ["(<title>.+?</title>\s+)?(?=<disp-quote>)((.|\s)+?)(?=</sec>)',r'\1<ref-list>\2</ref-list>", "<p>\s+?(<bold>|<title>)([A-Za-z\s]+)(</bold>|</title>)\s+?</p>\s+<list.+?>((.|\s)+?)(</list>)"]
		print self.try_list_of_regex(text, *regex_list)
		self.write_output(self.gv.TEI_FILE_PATH, text)
		'''
		
		
	
