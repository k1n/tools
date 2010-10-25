#!/usr/bin/python

import os
import sys
import glob

map = {
    'Professional': 'STND',
    'People': 'PEPL',
    'Planner': 'PLNR',
} 

for name in ['STND', 'PEPL', 'PLNR']:
    deb = glob.glob('/home/tualatrix/Sources/pagico/%s/*.deb' % name)[0]
    new_deb = deb.replace('karmic1', name)
    os.system('mv %s %s' % (deb, new_deb))
    os.system('scp %s %s' % (new_deb, sys.argv[1]))
