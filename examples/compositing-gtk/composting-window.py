#!/usr/bin/python
import sys
import gobject
import pango
import pygtk
import gtk
from gtk import gdk
import cairo
# import Images
import gobject

class pngtranswin:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
           
        self.window.set_decorated(True)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_keep_above(True)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
           
        self.window.set_events(gtk.gdk.ALL_EVENTS_MASK)
           
        # Initialize colors, alpha transparency
        self.window.set_app_paintable(True)
        self.gtk_screen = self.window.get_screen()
        colormap = self.gtk_screen.get_rgba_colormap()
        if colormap == None:
            colormap = self.gtk_screen.get_rgb_colormap()
        gtk.widget_set_default_colormap(colormap)
        if not self.window.is_composited():
            self.supports_alpha = False
        else:
            self.supports_alpha = True
           
        self.w,self.h = self.window.get_size()
           
        self.window.connect("expose_event", self.expose)
        self.window.connect("destroy", gtk.main_quit)

    def expose (self, widget, event):
        self.ctx = self.window.window.cairo_create()
        self.p_context = self.window.get_pango_context()
        # set a clip region for the expose event, XShape stuff
        self.ctx.save()
        if self.supports_alpha == False:
            self.ctx.set_source_rgb(1, 1, 1)
        else:
            self.ctx.set_source_rgba(1, 1, 1,0)
        self.ctx.set_operator (cairo.OPERATOR_SOURCE)
        self.ctx.paint()
        self.ctx.restore()
        self.ctx.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        self.ctx.clip()
        #self.draw_image(self.ctx,0,0,'base.png')
        self.draw_text(self.ctx, self.p_context)
        print self.ctx, self.p_context

    def draw_text(self,ctx, ptx):
        font = pango.FontDescription()

        font.set_family("sans")
        font.set_size(32 * pango.SCALE)

        layout = pango.Layout(ptx)
        layout.set_font_description(font) 
        layout.set_text('Hello World')

        ctx.show_layout(layout)

    def setup(self):
        # Set menu background image
        self.background =  gtk.Image()
        self.frame = gtk.Fixed()
        self.window.add (self.frame)
           
        # Set window shape from alpha mask of background image
        w,h = self.window.get_size()
        if w==0: w = 800
        if h==0: h = 650
        self.w = w
        self.h = h
        self.pixmap = gtk.gdk.Pixmap (None, w, h, 1)
        ctx = self.pixmap.cairo_create()
        # todo: modify picture source
        #self.bgpb = gtk.gdk.pixbuf_new_from_file('base.png')
        ctx.save()
        ctx.set_source_rgba(1, 1, 1,0)
        ctx.set_operator (cairo.OPERATOR_SOURCE)
        ctx.paint()
        ctx.restore()
        self.draw_image(ctx,0,0,'base.png')
           
        if self.window.is_composited():
            ctx.rectangle(0,0,w,h)
            ctx.fill()
            self.window.input_shape_combine_mask(self.pixmap,0,0)
        else:
            self.window.shape_combine_mask(self.pixmap, 0, 0)

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

    def show_window(self):
        self.window.show_all()
        while gtk.events_pending():
            gtk.main_iteration()
        self.window.present()
        self.window.grab_focus()
        self.p = 1

if __name__ == "__main__":
    m = pngtranswin()
#    m.setup()
    m.show_window()
    gtk.main()
