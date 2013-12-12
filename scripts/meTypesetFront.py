import re
import string
import sys
import operator
from django.utils.encoding import smart_str


def parse_authors(meTypesetOutfile):

	f = open(meTypesetOutfile, 'rb')
	filestring = smart_str(f.read(), encoding='ascii', error='ignore')

# this works for perception-monospace, equations tables, laddering, neoliberalism, snowball, valuechain, sodium
	name = re.findall(r'(\n|<p>|<bold>|<italic>)(([A-Za-z\-\.]+)\*?\s){2,5}(&|and|et|und)\s(([A-Za-z\-\.]+)\*?\s?){2,5}(</p>|</bold>|</italic>|\n)',filestring)

	if len(name) = 0:
# this works for racialprofiling, antiseptics, eeg_comicsans, leadership, systemsthinker
# this would work for science.doc but there are way too many authors and that affects the string
# would work for rating.doc but need to fix linebreak comments from output
		name2 = re.findall(r'(<p>|<bold>|<italic>)(([A-Za-z\-\.]+)(,?\s)){1,20}([A-Za-z\-\.]+)?(</p>|</bold>|</italic>)',filestring)
# this loops through strings and prefers those that occur earlier + have more periods/commas
		guess2score = {}
		guess2number = 0
		for guess2 in name2:
			periods = re.findall(r'\.',guess2)
			italics = re.findall(r'italic',guess2)
			guess2score[guess2] = len(periods)
			guess2score[guess2] += len(italics)
			guess2score[guess2] -= guess2number
			guess2number += 1
		name[0] = max(guess2score.iteritems(), key=operator.itemgetter(1))[0]

	striptags_name = re.sub(r'<.*>','',name[0])
	authorString = re.sub(r'[B|b][Y|y]\s','',striptags_name)

# this is the author string. could try sending to parscit to get individual author names.
	return authorString
# entrepreneurship needs fixing, will be tough, has authors in multiple XML elements


def parse_title(meTypesetOutfile):

	f = open(meTypesetOutfile, 'rb')
	filestring = smart_str(f.read(), encoding='ascii', error='ignore')

# need to anticipate which other special characters are allowable in titles
# first, check if a subtitle and title have wound up separated from one another
	title = re.findall(r'(\n|<p>|<bold>|<italic>)(([A-Za-z\-\.]+)(,?\s)){1,20}([A-Za-z\-\.]+)?:(</p>|</bold>|</italic>|\n)(.|\s)*?(\n|<p>|<bold>|<italic>)(([A-Za-z\-\.]+)((:|,)?\s)){1,20}([A-Za-z\-\.]+)?\??(</p>|</bold>|</italic>|\n)',filestring)

	if len(title) = 0:
# this works for antiseptics, eeg_comicsans, entrepreneurship, laddering, racialprofiling, snowball, sodium
		title2 = re.findall(r'(\n|<p>|<bold>|<italic>)(([A-Za-z\-\.]+)((:|,)?\s)){1,20}([A-Za-z\-\.]+)?\??(</p>|</bold>|</italic>|\n)',filestring)
		title = title2

	titleString = re.sub(r'<.*>','',title[0])

# this is the title string.
	return titleString