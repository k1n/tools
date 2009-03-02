import time

TEMPLATE = '''%(app)s (%(major)s~%(minor)s) %(distro)s; urgency=low

%(changelog)s

 -- TualatriX <tualatrix@gmail.com>  %(timestamp)s

'''

def make_changelog_content(changelog):
    list = []
    for line in changelog.split('\n'):
        line = '  * ' + line
        list.append(line)

    return ''.join(list)

def make_timestamp():
    return time.strftime('%a, %d %b %Y %X +0800', time.localtime())

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

if __name__ == '__main__':
    print make_changelog_section('ubuntu-tweak', '0.4.6-1', 'hardy1', 'hardy', 'fix a bug')
