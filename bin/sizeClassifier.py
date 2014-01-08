#!/usr/bin/env python
from lxml import etree
from lxml import objectify
from copy import deepcopy
import uuid
import globals as gv
import os
from manipulate import *
import subprocess
import shutil
import re
import operator

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

'''
A class that scans for meTypeset size fields in a TEI file.

1.) Identifies a list of sizes
2.) Ascertains the density and likelihood of the size being a heading
3.) Returns a manipulator ready to implement all the changes to the TEI file to incorporate this information as nested title tags

'''
class sizeClassifier():
	size_cutoff = 16

	def __init__(self, gv):
		self.gv = gv

	def get_values(self, tree, search_attribute):
		# this function searches the DOM tree for TEI "hi" elements with the specified search_attribute
		sizes = {}
		sizesOrdered = []
		for child in tree.xpath("//tei:hi[@" + search_attribute + "=not('')]", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
			if child.get(search_attribute) in sizes:
				sizes[child.get(search_attribute)] = sizes[child.get(search_attribute)] + 1
			else:
				sizes[child.get(search_attribute)] = 1

			sizesOrdered.append(child.get(search_attribute))

		return sizes, sizesOrdered

	def set_dom_tree(self, filename):
			p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

			return etree.parse(filename, p)	
	   
	def run(self):
			# load the DOM
		  	tree = self.set_dom_tree(self.gv.TEI_FILE_PATH)

			# get a numerical list of explicit size values inside meTypesetSize attributes
			sizes, sizesOrdered = self.get_values(tree, "meTypesetSize")
	
			if self.gv.debug:
				print "Explicitly specified size variations and their frequency of occurrence:"
				print sizes

			# depending on the length of the array we will parse differently

			iteration = 0

			if len(sizes) == 1:
				for size in sizes:
					# loop should only execute once but because dictionaries are non-ordered in python, this is the easiest way
					if size >= self.size_cutoff:
						# if the size is greater than or equal to 16, treat it as a heading
						if self.gv.debug:
							print "Found single explicitly specified size greater than or equal to " + str(self.size_cutoff) + ". Treating as a heading."

						# instruct the manipulator to change the parent tag of every tag it finds containing 
						# a "hi" tag with meTypesetSize set to the value found to "title"
						# so, for example <p><hi meTypesetSize="18">some text</hi></p>
						# will be transformed to
						# <title><hi meTypesetSize="18">some text</hi></title>
						manipulate = Manipulate(self.gv)
						manipulate.change_outer("//tei:hi[@meTypesetSize='" + size + "']", "head", size)

						# todo: wrap section tags (single section with multiple headings)

			elif len(sizes) > 1:
				# first, we want a sorted representation (of tuples) of the frequency dictionary

				for size in sizes:
					# disregard sizes below the cut-off
					if size >= self.size_cutoff:
						manipulate = Manipulate(self.gv)
						manipulate.change_outer("//tei:hi[@meTypesetSize='" + size + "']", "head", size)
						iteration = iteration + 1

				# todo: wrap section tags
				# the way we need to do this is to iterate over each tag, looking for the next title
				# if the next title is within size_cutoff and the same size as the preceding, then close section, open section, and insert the title (no stack change)
				# if the next title is within size_cutoff and a smaller size than the preceding, then open section and write title (then push)
				# if the next title is within size_cutoff and a bigger size than the preceding, then close section (then pop)

				# this should be implemented in three stages:
				# 1.) a dry-run trying to parse this as a formal stack with push and pops for each level
				# 2.) if the stack works, then use that to deal with headings
				# 3.) if the stack doesn't work (ie the user has created a document that isn't logially structured), then do our best manually

				sectionCount = {}
				iteration = 0
				firstHeading = 0
				sectionStack = []

				manipulate.tag_headings()

				for size in sizesOrdered:
					if not size in sectionCount:
						sectionCount[size] = 0

					if len(sectionStack) == 0:
						# this section should span the entire document and enclose the first title
						# manipulate.enclose("//tei:head[@meTypesetSize='" + size + "']", sectionCount[size], "(//*)[last()]")

						# done automatically?
						firstHeading = size
					else:
						# this block is triggered when we reach any heading but the first

						# ascertain the next size
						if iteration < (len(sizesOrdered) - 1):
							nextSize = sizesOrdered[iteration + 1]

							if size == nextSize:
								# if same size, select and enclose "//tei:head[@meTypesetHeadingID='ID'] | //*[preceding-sibling::tei:head[@meTypesetHeadingID='ID'] and following-sibling::tei:head[@meTypesetHeadingID='ID+1']]"
								manipulate.enclose("//tei:head[@meTypesetHeadingID='" + str(iteration) + "']", "//tei:head[@meTypesetHeadingID='" + str(iteration) + "'] | //*[preceding-sibling::tei:head[@meTypesetHeadingID='" + str(iteration) + "'] and following-sibling::tei:head[@meTypesetHeadingID='" + str(iteration + 1) + "']]")

							# if smaller and others of same size, select and enclose "//tei:head[@meTypesetHeadingID='ID'] | //*[preceding-sibling::tei:head[@meTypesetHeadingID='ID'] and following-sibling::tei:head[@meTypesetHeadingID='__THEIDOFSIBLINGWITHSAMESIZE__']]"/>

							# if smaller and no others of same size, select and enclose "//tei:head[@meTypesetHeadingID='ID'] | //*[preceding-sibling::tei:head[@meTypesetHeadingID='ID'] and following-sibling::END_OF_PRECEDING_DIV]"/>
							if size > nextSize:
								manipulate.enclose("//tei:head[@meTypesetHeadingID='" + str(iteration) + "']", "//tei:head[@meTypesetHeadingID='" + str(iteration) + "'] | //*[preceding-sibling::tei:head[@meTypesetHeadingID='" + str(iteration) + "']]")

							# if bigger then skip iteration and just move to continue searching for next??

						else:
							# this is the last heading so there is no future comparator
							manipulate.enclose("//tei:head[@meTypesetHeadingID='" + str(iteration) + "']", "//tei:head[@meTypesetHeadingID='" + str(iteration) + "'] | //*[preceding-sibling::tei:head[@meTypesetHeadingID='" + str(iteration) + "']]")

					sectionCount[size] = sectionCount[size] + 1

					sectionStack.append(size)

					iteration = iteration + 1
