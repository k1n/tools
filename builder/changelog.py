#!/usr/bin/python

import os
import sys
import time

TEMPLATE = '''%(app)s (%(major)s~%(minor)s) %(distro)s; urgency=low

%(changelog)s
 -- Tualatrix Chou <tualatrix@gmail.com>  %(timestamp)s

'''

def make_changelog_content(changelog):
    list = []
    for line in changelog.split('\n'):
        if line:
            line = '  * %s\n' % line
            list.append(line)

    return ''.join(list)

def make_timestamp():
    return time.strftime('%a, %d %b %Y %X +0800', time.localtime())

def make_daily_timestamp(revno, distro, suffix='1'):
    return '%s+%s~%s%s' % (time.strftime('%Y%m%d', time.localtime()),
                           revno, distro, suffix)

def make_changelog_section(app, major, minor, distro, changelog):
    global TEMPLATE
    return TEMPLATE % {
                'app': app,
                'major': major,
                'minor': minor,
                'distro': distro,
                'changelog': make_changelog_content(changelog),
                'timestamp': make_timestamp()
            }

def make_daily(app, version, revno, distro, file, suffix='1'):
    data = open(file).read()
    section = make_changelog_section(app, version + '-0',
                                     make_daily_timestamp(revno, distro, suffix),
                                     distro, 'daily build.\n')
    f = open(file, 'w')
    f.write(section + data)
    f.close()

def make_normal(app, version, distro, file):
    data = open(file).read()
    section = make_changelog_section(app, version + '-1', '%s1' % distro, distro, open('/home/tualatrix/Sources/tools/builder/changelog').read())
    f = open(file, 'w')
    f.write(section + data)
    f.close()

if __name__ == '__main__':
#    print make_changelog_section('ubuntu-tweak', '0.4.6-1', 'hardy1', 'hardy', 'fix a bug')
#    print make_daily('ubuntu-tweak', '0.4.7', 'jaunty', 'changelog')
    if sys.argv[5] == 'daily':
        make_daily(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        make_normal(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
