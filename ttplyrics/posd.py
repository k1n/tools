#!/usr/bin/python
# coding: utf-8

import sys
import gtk
import cairo
import pango
import gobject

index = 0

songs = [
    'Hello World!', 
    'I\'m TualatriX!',
    'How are you?',
    '我也會顯示中文喔！',
    'GNU/Linux is my favourite!',
]

class PangoOsd(object):
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_POPUP)

        # Initialize window
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.set_app_paintable(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_events(gtk.gdk.ALL_EVENTS_MASK)
       
        # Initialize colors, alpha transparency
        self.screen = self.window.get_screen()
        w, h = self.screen.get_width(), self.screen.get_height()
#                self.window.set_default_size(w, 100)
#                self.window.move(800, 600)
        colormap = self.screen.get_rgba_colormap()
        if colormap == None:
                colormap = self.screen.get_rgb_colormap()
        gtk.widget_set_default_colormap(colormap)
        if not self.window.is_composited():
                self.supports_alpha = False
        else:
                self.supports_alpha = True

        self.w, self.h = self.window.get_size()
        pixmap = gtk.gdk.Pixmap(None, self.w, self.h, 1)
        self.window.input_shape_combine_mask(pixmap, 0, 0)

        self.window.connect('expose_event', self.on_expose_event)
        self.window.connect('destroy', gtk.main_quit)

        self.layout = None
        gobject.timeout_add(2000, self.on_timeout)

    def on_timeout(self):
        global index, songs
        if index < len(songs):
            self.draw_text(songs[index])
            index += 1
            return True
        else:
            gtk.main_quit()

    def on_expose_event(self, widget, event):
        screen = self.window.get_screen()
        self.width, self.height = screen.get_width(), screen.get_height()

        self.ctx = self.window.window.cairo_create()
        self.ptx = self.window.get_pango_context()

        # set a clip region for the expose event, XShape stuff
        self.window.window.move_resize(700, 750, self.width, 130)
        self.window.window.stick()
        ctx = self.window.window.cairo_create()
        ptx = self.window.get_pango_context()

        ctx.save()
        ctx.set_source_rgba(0.3, 0.0, 0.0, 0)
        ctx.set_operator (cairo.OPERATOR_SOURCE)
        ctx.paint()
        ctx.restore()

    def draw_text(self, text = 'Hello'):
        self.window.window.move_resize(0, 700, 1280, 112)
        ctx = self.window.window.cairo_create()
        ptx = self.window.get_pango_context()

        ctx.save()
        ctx.set_source_rgba(0.3, 0.3, 0.3, 0.3)
        ctx.set_operator (cairo.OPERATOR_SOURCE)
        ctx.paint()
        ctx.restore()

        font = pango.FontDescription()

        font.set_family("sans")
        font.set_size(64 * pango.SCALE)

        if not self.layout:
            layout = self.window.create_pango_layout(text)
            layout.set_font_description(font) 
            layout.set_text(text)
            self.layout = layout

        self.layout.set_text(text)

        ctx.move_to(*self.center_word(*self.layout.get_pixel_size()))

        ctx.set_source_rgba(0.8, 1, 0, 0.8)
        ctx.set_operator (cairo.OPERATOR_SOURCE)
        ctx.show_layout(self.layout)

    def center_word(self, width, height):
        return ((self.width - width)/2, 0)

    def hide(self):
        self.window.hide()

    def draw_image(self,ctx,x,y, pix):
        """Draws a picture from specified path with a certain width and height"""
        ctx.save()
        ctx.translate(x, y)
        pixbuf = gtk.gdk.pixbuf_new_from_file(pix)
        format = cairo.FORMAT_RGB24
        if pixbuf.get_has_alpha():
                format = cairo.FORMAT_ARGB32
        #if Images.flip != None:
        # pixbuf = pixbuf.flip(Images.flip)

        iw = pixbuf.get_width()
        ih = pixbuf.get_height()
        image = cairo.ImageSurface(format, iw, ih)
        image = ctx.set_source_pixbuf(pixbuf, 0, 0)
       
        ctx.paint()
        puxbuf = None
        image = None
        ctx.restore()
        ctx.clip()

    def get_number_lines(self):
        return 1

    def display(self, song, line = 1):
        self.window.show_all()
        print 'displaying', song
        self.draw_text(song)

    def show_window(self):
        self.window.show_all()
        while gtk.events_pending():
                gtk.main_iteration()
        self.window.present()
        self.window.grab_focus()
        self.p = 1

if __name__ == "__main__":
    m = PangoOsd()
    m.show_window()
    gtk.main()
