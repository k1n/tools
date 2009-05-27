#!/usr/bin/python

import gtk

class Demo(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        self.set_title('Gtk Demo')
        self.set_size_request(400, 320)
        self.set_border_width(10)
        self.connect('destroy', gtk.main_quit)

        vbox = gtk.VBox(False, 10)
        self.add(vbox)

        label = gtk.Label("It's Label")
        vbox.pack_start(label, False, False, 0)

        button = gtk.Button("It's Button")
        vbox.pack_start(button, False, False, 0)

        checkbutton = gtk.CheckButton("It's CheckButton")
        vbox.pack_start(checkbutton, False, False, 0)

        entry = gtk.Entry()
        vbox.pack_start(entry, False, False, 0)

        self.show_all()

def main():
    gtk.main()

if __name__ == '__main__':
    app = Demo()
    main()
