#!/usr/bin/python

import gtk
import vte

win = gtk.Window()
vt = vte.Terminal()
vt.fork_command()
win.add(vt)

win.show_all()
gtk.main()
