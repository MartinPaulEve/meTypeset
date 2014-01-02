import re
import string
import sys
import operator
from django.utils.encoding import smart_str

f = open(sys.argv[1], 'rb')

filestring = smart_str(f.read(), encoding='ascii', errors='ignore')

# remove abstract and surname stub -- this gets in the way
filestring = re.sub(r'<p>This is a sample abstract that forms part of the metadataSample.xml file in meTypeset.</p>','',filestring)
filestring = re.sub(r'<surname>Eve</surname>','',filestring)

# insert guessed-at linebreaks -- this breaks opening and closing of markup tags currently (e.g. </p> before </b>). probably needs to be fixed in meTypeset by classifier rather than in post.
#filestring = re.sub(r'<!--There should be a line-break here.-->',r'</p><p>',filestring)

# remove Endnote junk (this currently drops Endnote marked-up citations entirely -- should be reasonably easy to preserve them as desired from the Endnote XML, just haven't gotten around to it yet):
filestring = re.sub(r'\(.*ADDIN EN.CITE.*?\)','',filestring)

# REFERENCE PARSING

# changes ref wrapper to <ref-list> (couple different approaches)
try:
	filestring = re.sub(r'(<title>.+?</title>\s+)?(<(disp-quote|list).*?>)((.|\s)+?)(?=</sec>)',r'\1<ref-list>\4</ref-list>',filestring)
except:
	pass
try:
	filestring = re.sub(r'<p>\s+?(<bold>|<title>)([A-Za-z\s]+)(</bold>|</title>)\s+?</p>\s+<list.+?>((.|\s)+?)(</list>)',r'<title>\2</title>\n<ref-list>\4</ref-list>',filestring)
except:
	pass
filestring = re.sub(r'</list>\s*?</ref-list>','</ref-list>',filestring)
# changes <disp-quote> or <list-item> to <ref>
try:
	filestring = re.sub(r'(<disp-quote>|<list-item>)\s+<p>\s*?.*?([0-9]+)\.\s+?(?=[A-Z])',r'<ref rid="R\2">',filestring)
except:
	pass
filestring = re.sub(r'(<disp-quote>|<list-item>)\s+<p>',r'<ref>',filestring)
filestring = re.sub(r'</p>\s+(</disp-quote>|</list-item>)',r'</ref>',filestring)
# if references weren't numbered, number them
# this isn't quite working yet
orderedRefs = re.findall(r'(<ref>((.|\s)*?)</ref>)',filestring)
refNumber = 1
for r in orderedRefs:
	#refString = re.match(r'(?<=<ref>)(\s|.)*?(?=</ref>)',r[0])
	#print refString
	#fullRef = '<ref rid="R'+str(refNumber)+'">'+refString.group(0)+'</ref>'
	fullRef = '<ref rid="R'+str(refNumber)+'">'+r[1]+'</ref>'
	re.sub(r[0],fullRef,filestring)
	refNumber += 1

# match inline numeric citations
# may need to strip <sup> tags surrounding these in some cases
filestring = re.sub(r'(,|\[)([0-9]{1,3})(,|\])',r'\[<xref id="\2" ref-type="bibr">\2</xref>\]',filestring)

# match inline authorname citations
refs = re.findall(r'<ref.*?>[\s]*.*[\s]*</ref>',filestring)
firstauthormatch = re.compile(r'[A-Za-z]{3,}')
for r in refs:
#	authors = re.findall(r'[A-Za-z -]+,?\s([A-Z]{1,3}(\.|,)){1,3}',r)
# the above is more specific but doesn't seem to work with re.findall()
	try:
		authors = re.findall(r'[A-Za-z -]+,?\s[A-Z]\.|,',r)
		firstauthor = firstauthormatch.match(authors[0])
		namestring = r'(\(.*?'+firstauthor.group(0)+r'.*?[^amp](;|\)))'
		filestring = re.sub(namestring,r'<xref id="'+(r+1)+r'" ref-type="bibr">\1</xref>',filestring)
	except:
		pass

# AUTHOR PARSING

name = re.findall(r'((\n|<p>|<bold>|<italic>)(([A-Za-z\.]+)\*?(\-|\s)){2,5}(&|and|et|und)\s(([A-Za-z\.]+)\*?(\-|\s)){2,5}(</p>|</bold>|</italic>|\n))',filestring)

if len(name) == 0:
	name = []
	name2 = re.findall(r'((<p>|<bold>|<italic>)(([A-Za-z\-\.]+)(,?\s)){1,20}([A-Za-z\-\.]+)?(</p>|</bold>|</italic>))',filestring)
	guess2score = {}
	guess2number = 0
	for guess2 in name2:
		guess2 = guess2[0]
		periods = re.findall(r'\.',guess2)
		commas = re.findall(r'\.',guess2)
		italics = re.findall(r'italic',guess2)
		guess2score[guess2] = len(periods)
		guess2score[guess2] = len(commas)
		guess2score[guess2] += len(italics)
		guess2score[guess2] -= guess2number
		guess2number += 1
	name.append(max(guess2score.iteritems(), key=operator.itemgetter(1))[0])
else:
	name = name[0]
striptags_name = re.sub(r'<.*?>','',name[0])
authorString = re.sub(r'(?<![A-Za-z])[B|b][Y|y]\s','',striptags_name)
taggedAuthorString = '<given-names>'+authorString+'</given-names>'

# this is the author string. could try sending to parscit to get individual author names.
filestring = re.sub(r'<given-names>(.*)</given-names>',taggedAuthorString,filestring)

# TITLE PARSING

# first, check if a subtitle and title have wound up separated from one another
title = re.findall(r'((\n|<p>|<bold>|<italic>)(([A-Za-z\-\.]+)(,?\s)){1,20}([A-Za-z\-\.]+)?:(</p>|</bold>|</italic>|\n).*?(\n|<p>|<bold>|<italic>)(([A-Za-z\-\.]+)((:|,)?\s)){1,20}([A-Za-z\-\.]+)?\??(</p>|</bold>|</italic>|\n))',filestring)

if len(title) == 0:
	title2 = re.findall(r'((\n|<p>|<bold>|<italic>)(([A-Za-z\-\.]+)((:|,)?\s)){1,20}([A-Za-z\-\.]+)?\??(</p>|</bold>|</italic>|\n))',filestring)
	title = title2[0]
else:
	title = title[0]

titleString = re.sub(r'<.*?>','',title[0])
taggedTitleString = '<article-title>'+titleString+'</article-title>'

# this is the title string.
filestring = re.sub(r'<article-title>(.*)</article-title>',taggedTitleString,filestring)

g = open(sys.argv[2], 'wb')
g.write(filestring)