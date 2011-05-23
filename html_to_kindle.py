#!/usr/bin/python

import sys
import pdb

from BeautifulSoup import BeautifulSoup

if len(sys.argv) != 2:
    print("Please enter the path to html")
    sys.exit(1)

soup = BeautifulSoup(open(sys.argv[1]).read())
# 0 and 2 is the title, the 1 is content
td = soup.findAll('table')[1].find('td')

f = open('output/%s' % sys.argv[1], 'w')
f.write('<html><head></head><body>%s</body></html>' % td.renderContents())
f.close()

#pdb.set_trace()
