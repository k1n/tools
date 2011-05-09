#!/usr/bin/python

import gtk
import webkit


class Window(gtk.Window):
    TARGET = [
            ('STRING', 0, 0),
            ('text/plain', 0, 0),
            ]

    def __init__(self):
        gtk.Window.__init__(self)

        self.set_size_request(800, 600)
        self.connect('destroy', gtk.main_quit)

        self.webview = webkit.WebView()
        self.webview.drag_dest_set(gtk.DEST_DEFAULT_ALL, self.TARGET[:-1],
                gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_LINK)
        self.webview.connect('drag-data-received', self.on_drag_data_received)

        self.add(self.webview)

        self.webview.load_uri('http://www.baidu.com')

    def on_drag_data_received(self, widget, drag_context, x, y, selection_data, info, timestamp):
        print drag_context, selection_data, info, timestamp


if __name__ == '__main__':
    win = Window()
    win.show_all()

    gtk.main()
