#!/usr/bin/python

from gi.repository import Gtk

def on_activate(widget, image):
    image.set_from_icon_name(widget.get_text(), Gtk.IconSize.DIALOG)

win = Gtk.Window()
win.set_position(Gtk.WindowPosition.CENTER)
win.set_border_width(6)
win.connect('destroy', lambda *w: Gtk.main_quit())
vbox = Gtk.HBox(spacing=12)
win.add(vbox)

image = Gtk.Image.new_from_icon_name('gnome', Gtk.IconSize.DIALOG)
vbox.pack_start(image, False, False, 0)

entry = Gtk.Entry()
entry.connect('activate', on_activate, image)
vbox.pack_start(entry, False, False, 0)

win.show_all()

Gtk.main()
