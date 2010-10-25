#!/usr/bin/python

import os
import glob

map = {
    'Professional': 'STND',
    'People': 'PEPL',
    'Planner': 'PLNR',
} 

for suffix, name in map.items():
    path = glob.glob('*%s*.zip' % suffix)[0]
    os.system('rm -r CodeX')
    os.system('unzip %s' % path)
    os.system('cd /home/tualatrix/Sources/pagico/codex && git rm -r CodeX_%s/*' % name)
    os.system('mkdir /home/tualatrix/Sources/pagico/codex/CodeX_%s' % name)
    os.system('cp -r CodeX/* /home/tualatrix/Sources/pagico/codex/CodeX_%s/' % name)
    os.system('cd /home/tualatrix/Sources/pagico/codex && git add CodeX_%s/*' % name)
