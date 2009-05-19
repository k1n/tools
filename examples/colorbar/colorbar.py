#!/usr/bin/python

import gtk
import vte
from ubiquity import segmented_bar

win = gtk.Window()
win.set_default_size(640, 200)
win.connect('destroy', gtk.main_quit)
win.set_title('Ubuntu Tweak Color Bar')
win.set_border_width(10)

vbox = gtk.VBox()
win.add(vbox)

bar = segmented_bar.SegmentedBar()
bar.add_segment_rgb('Gentoo', 20, '60da11')
bar.add_segment_rgb('Fedora', 30, '3911d9')
bar.add_segment_rgb('Ubuntu', 50, 'd911d9')
vbox.pack_start(bar)

win.show_all()
gtk.main()
