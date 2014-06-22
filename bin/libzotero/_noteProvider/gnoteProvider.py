#-*- coding:utf-8 -*-

"""
This file is part of Gnotero.

Gnotero is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Gnotero is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Gnotero.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import os.path
import re
import subprocess
try:
	import Levenshtein
except:
	print "libzotero._noteProvider.gnoteProvider: failed to import Levenshtein"

class GnoteProvider(object):

	"""
	libgnote provides an interface to Gnote and is a replacement
	for the deprecated gnote.py module
	"""

	def __init__(self, qnotero):

		if os.name != "posix":
			self.path = None
			return

		home_folder = os.environ["HOME"]

		# Determine the location of the gnote notes
		if os.path.exists(os.path.join(home_folder, ".local/share/gnote")):
			self.path = os.path.join(home_folder, ".local/share/gnote")
			print "libgnote.__init__(): gnote path is %s" % self.path

		elif os.path.exists(os.path.join(home_folder, ".gnote")):
			self.path = os.path.join(home_folder, ".gnote")
			print "libgnote.__init__(): gnote path is %s" % self.path

		else:
			print "libgnote.__init__(): failed to locate Gnote"
			self.path = None

	def search(self, item):

		"""
		Search gnote for a note matching an author and a year
		"""

		if self.path == None:
			return None

		# Compile some regexps to search for the note,
		# extract the note and remove xml tags
		p = re.compile(r"<bold>%s.*\(%s\)" % (item.authors[0], item.date), re.IGNORECASE)
		get_note = re.compile(r"<bold>%s.*?\(%s\).*?<bold>" % (item.authors[0], item.date), re.IGNORECASE and re.DOTALL)
		strip_p = re.compile('<.*?>')
		matches = []

		# Walk through all notes
		for fnote in os.listdir(self.path):

			if os.path.splitext(fnote)[1] == ".note":

				note_path = os.path.join(self.path, fnote)

				# Read the contents of the note
				f = open(note_path, "r")
				s = f.read()

				# Search the note according to the regular expression
				m = p.search(s)

				# If a contains a match
				if m != None:

					# Extract the matching content
					s = s[m.span()[0]:]
					m = get_note.search(s[:s.find("</note-content>")])
					if m != None:
						start, end = m.span()
					else:
						start = 0
						end = len(s)
					pango = s[start:end]

					# Remove tags, strip whitespaces and highlight the
					# search terms
					pango = strip_p.sub("", pango)[:1024].strip()
					for s in (item.authors[0], item.date):
						try:
							pango = pango.replace("%s" % s, "<b>%s</b>" % s)
						except:
							pass

					# Add this result to the list
					matches.append(GnoteNote(pango, "gnote --open-note=%s" % note_path))

		if len(matches) == 0:
			return None

		elif len(matches) == 1:
			print "libgnote.search(): 1 note found matching %s (%s)" % (item.authors[0], item.date)

		else:

			# If there are multiple matches, try to figure out which note is most likely
			# the actual note

			print "libgnote.search(): %d matches found, sorting by relevance" % len(matches)
			matches.sort(key=lambda m: m.matchScore(item))

		return matches[0]

class GnoteNote:

	"""
	A class containing a note
	"""

	def __init__(self, preview, cmd):

		self.preview = preview
		self.cmd = cmd

	def matchScore(self, item):

		"""
		Determines the best match
		"""

		first_line = self.preview.split("\n")[0].replace("&amp;", "&")
		match = item.simple_format() + " " + item.format_publication()
		score = Levenshtein.distance(first_line, match)

		return score

	def open(self):

		"""Open the note in Gnote"""

		subprocess.call(self.cmd.split())

