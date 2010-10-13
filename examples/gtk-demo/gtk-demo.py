#!/usr/bin/python

import gtk
import gobject

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
        entry.connect('changed', self.on_entry_changed, button)
        vbox.pack_start(entry, False, False, 0)

        self.show_all()
        gobject.timeout_add(1000, self.on_timeout, entry)

    def on_entry_changed(self, widget, button):
        keyk = widget.get_text()

        if len(keyk) >= 8 and len(keyk) <= 64:
            if len(keyk) == 64:
                for ch in keyk:
                    if (ch>='0' and ch<='9') or (ch>='a' and ch<='f') or (ch>='A' and ch<='F') :
                        ValidKey = True
                    else:
                        ValidKey = False
                        break
            else:
                ValidKey = True
        else:
            ValidKey = False

        button.set_sensitive(ValidKey)

    def on_timeout(self, entry):
#         print gtk.SelectionData().get_text()
        print entry.get_clipboard(gtk.gdk.atom_intern('PRIMARY')).wait_for_text()# request_text
        return True

def main():
    gtk.main()

if __name__ == '__main__':
    app = Demo()
    main()
