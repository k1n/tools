#!/usr/bin/python  
# -*- coding: utf-8 -*-  
# url: http://www.minilinux.net/node/27
  
import sys  
reload(sys)
sys.setdefaultencoding('utf8')
import httplib  
import urllib  
import urllib2  
import traceback  
import simplejson
import re  
import random  
import time  
  
  
proxies = [  
     "proxy1:port",  
     "proxy2:port",  
     None,  
    ]  

def get_splits(text, length=4500):
    '''
    Translate Api has a limit on length of text(4500 characters) that can be translated at once
    '''
    return (text[index:index+length] for index in xrange(0,len(text),length))
  
def translate(text):
    from_lang = "en"
    to_lang = "zh-CN"
    langpair = '%s|%s' % (from_lang, to_lang)

    # OK, dirty hack, but works. ^_^
    text = 'OMG!'.join(text.split('\n'))

    base_url = 'http://ajax.googleapis.com/ajax/services/language/translate?'
    params = {'v': 1.0,
            'ie': 'UTF8',
            'q': text,
            'langpair': langpair}

    new_text = ''
    for splite in get_splits(text):
        params['q'] = splite
        data = urllib.urlencode(params)
        resp = simplejson.load(urllib.urlopen('%s' % (base_url), data=data))

        try:
            translated = resp['responseData']['translatedText']
            translated = translated.replace('％', '%')
            translated = re.sub("&#(\d+);", lambda s: chr(int(s.group(1))),   translated)
            translated = re.sub("&([a-z]+);", lambda s: {"lt":"<", "gt":">", "amp":"&"}[s.group(1)], translated)
            new_text += translated
        except:
            pass

    # recover the word
    return '\n'.join(new_text.split('OMG!'))
  
def translate_fixed(text):  
#    signature = random.randrange(1E20, 1E21)  
    notrans = []  
    def replace(match):  
        notrans.append(match.group(0))  
        return " 0.%d68065175210" % (len(notrans) - 1)  
    text = re.sub("\${[\w_]+}|\$[\w_]+", replace, text)  
    text = re.sub("\\\\\"|\\\\$|\\\\\\\\n|\\\\t", replace, text)  
    text = re.sub("\\\\", replace, text)  
    text = re.sub("[A-Z]{2,100}", replace, text)  
    text = re.sub("<\w+>|</\w+>", replace, text)  
    text = re.sub("puppy(?i)", replace, text)  
  
    trans = translate(text)  
  
    for i in range(len(notrans)):  
#        print "re.sub",  
#        print "%dx" % (signature + i), notrans[i], trans  
        trans = re.sub("0 ?.%d68065175210" % i, lambda x: notrans[i], trans)  
  
    return trans  
  
  
random.seed()  
  
if len(sys.argv) != 2:  
    print "Usage: " + sys.argv[0] + " filename.pot"  
    sys.exit(1)  
  
if sys.argv[1] == "-":  
    f = sys.stdin  
else:  
    f = open(sys.argv[1])  
  
  
print """# ä¸­æPuppy Linuxå¼åèä¹å®¶. 
# This file is distributed under GPL. 
#"""  
  
print """#, fuzzy 
msgid "" 
msgstr "" 
"Project-Id-Version: %(program)s\\n" 
"Report-Msgid-Bugs-To: %(reportbug)s\\n" 
"POT-Creation-Date: %(date)s\\n" 
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n" 
"Last-Translator: Google Translate\\n" 
"Language-Team: Chinese\\n" 
"MIME-Version: 1.0\\n" 
"Content-Type: text/plain; charset=utf-8\\n" 
"Content-Transfer-Encoding: 8bit\\n" 
""" % {"program": sys.argv[1],  
       "reportbug": "laborer@126.com",  
       "date": time.strftime("%Y-%m-%d %H:%M%z")}  
  
  
for line in f:  
    if not line.rstrip():  
        break;  
  
trans = []  
buf = ""  
skip = False  
for line in f:  
    line = line.rstrip()  
    if skip:  
        skip = line;  
        continue  
  
    if line.startswith("#,"):  
        print line + ", fuzzy"  
    elif line.startswith("#"):  
        print line  
    elif line.startswith("msgid "):  
        print "msgid",  
        line = line[6:]  
    elif line.startswith("msgstr "):  
        print "msgstr",  
        if buf:  
            trans.append(translate_fixed(buf))  
            buf = ""  
        for s in trans:  
            print "\"%s\"" % s  
        print  
        trans = []  
        skip = True  
  
    if line.startswith("\""):  
        print line  
        buf += line[1:-1]  
        if buf.endswith("\\n"):  
            trans.append(translate_fixed(buf[:-2])+"\\n")  
            buf = ""  
