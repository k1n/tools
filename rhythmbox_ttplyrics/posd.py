#!/usr/bin/python
# coding: utf-8

import sys
import gtk
import cairo
import pango
import gobject
from gtk import gdk

exposed = False
index = 0

songs = [
    'Hello World!',
    'This is TualatriX\'s posd',
    'It is amazing!',
    'Ubuntu: Linux操作系统',
]

class PangoOsd(object):
        def __init__(self):
                self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
               
                self.window.set_decorated(False)
                self.window.set_keep_above(True)
                self.window.set_skip_taskbar_hint(True)
                self.window.set_skip_pager_hint(True)

                self.window.set_events(gtk.gdk.ALL_EVENTS_MASK)
               
                # Initialize colors, alpha transparency
                self.window.set_app_paintable(True)
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

                self.w,self.h = self.window.get_size()
                pixmap = gtk.gdk.Pixmap(None, self.w, self.h, 1)
                self.window.input_shape_combine_mask(pixmap, 0, 0)

#                self.vbox = gtk.VBox()
#                self.vbox.set_app_paintable(True)
                self.object = gtk.Label()
                self.window.add(self.object)
                self.object.input_shape_combine_mask(pixmap, 0, 0)
               
                self.window.connect("expose_event", self.expose)
                self.window.connect("destroy", gtk.main_quit)

                self.layout = None
#                self.window.show_all()
                gobject.timeout_add(2000, self.on_timeout)

        def on_timeout(self):
            global index, songs
            print 'time out'
            self.draw_text(songs[index])
            index += 1

#            self.ctx.update_layout(self.layout)
#            self.ctx.show_layout(self.layout)
            return True

        def expose (self, widget, event):
            global exposed
            self.ctx = self.window.window.cairo_create()
            self.ptx = self.window.get_pango_context()
            # set a clip region for the expose event, XShape stuff
            self.ctx.save()
            if self.supports_alpha == False:
                    self.ctx.set_source_rgb(1, 1, 1)
            else:
                    self.ctx.set_source_rgba(0.3, 0.5, 0.4,0)
            self.ctx.set_operator (cairo.OPERATOR_SOURCE)
            self.ctx.paint()
            self.ctx.restore()
            self.ctx.rectangle(event.area.x, event.area.y,
                            event.area.width, event.area.height)
            self.ctx.clip()
            #self.draw_image(self.ctx,0,0,'base.png')
#                if not exposed:
#                    self.draw_text(self.ctx, self.ptx)
#                    print self.ctx, self.ptx
#                    exposed = True

        def draw_text(self, text = 'Hello'):
            self.window.window.move_resize(700, 750, 1280, 80)
            ctx = self.window.window.cairo_create()
            ptx = self.window.get_pango_context()

            ctx.save()
            ctx.set_source_rgba(0.3, 0.0, 0.0, 0.3)
            ctx.set_operator(cairo.OPERATOR_SOURCE)
            ctx.paint()
            ctx.restore()

            font = pango.FontDescription()

            font.set_family("sans")
            font.set_size(32 * pango.SCALE)

            ctx.move_to(400, 0)
            if not self.layout:
#                layout = pango.Layout(ptx)
#                layout = ctx.create_layout()
#                layout = self.object.get_layout()
                layout = self.object.create_pango_layout(text)
                layout.set_font_description(font) 
                layout.set_text(text)
                attrs = pango.AttrList()
                attr = pango.AttrForeground(65535, 0, 0, 0, -1)
                attrs.insert(attr)
                layout.set_attributes(attrs)
                self.layout = layout

                ctx.show_layout(layout)

            layout = self.layout
            layout.set_alignment(pango.ALIGN_RIGHT)
            print layout.get_alignment()
            print layout.get_pixel_size()

            layout.set_text(text)

            ctx.set_source_rgba(1, 0, 0, 0.5)
            ctx.fill()
            ctx.show_layout(layout)

        def hide(self):
            self.window.hide()

        def draw_image(self,ctx,x,y, pix):
                """Draws a picture from specified path with a certain width and
height"""

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
