#!/usr/bin/python

import gtk, gobject
import urllib, urllib2, json, re

w = gtk.Window()
w.connect("destroy", gtk.main_quit)

def on_insert_text(entry, text, tlen, pos):
  if re.match("^https?://[^ ]+", text) and tlen > 20:
    apiurl = "http://is.gd/api.php?" + urllib.urlencode(dict(longurl=text))
    shorturl = urllib2.urlopen(apiurl).read()
    entry.insert_text(shorturl, entry.get_position())
    gobject.idle_add(entry.set_position, entry.get_position() + len(shorturl))
    entry.stop_emission("insert-text")

e = gtk.Entry()
e.connect("insert-text", on_insert_text)

w.add(e)
w.show_all()

gtk.main()
