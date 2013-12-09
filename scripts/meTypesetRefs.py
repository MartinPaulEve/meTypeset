import re
import string
import sys

f = open(sys.argv[1], 'rb')

filestring = f.read()

# changes ref wrapper to <ref-list> (couple different approaches)
filestring = re.sub(r'(<title>.+?</title>\s+)?(?=<disp-quote>)((.|\s)+?)(?=</sec>)',r'\1<ref-list>\2</ref-list>',filestring)
filestring = re.sub(r'<p>\s+?(<bold>|<title>)([A-Za-z\s]+)(</bold>|</title>)\s+?</p>\s+<list.+?>((.|\s)+?)(</list>)',r'<title>\2</title>\n<ref-list>\4</ref-list>',filestring)
# changes <disp-quote> or <list-item> to <ref>
filestring = re.sub(r'(<disp-quote>|<list-item>)\s+<p>\s*?.*?([0-9]+)\.\s+?(?=[A-Z])',r'<ref rid="R\2">',filestring)
filestring = re.sub(r'</p>\s+(</disp-quote>|</list-item>)',r'</ref>',filestring)

# match inline numeric citations
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
		print ""

g = open(sys.argv[2], 'wb')
g.write(filestring)