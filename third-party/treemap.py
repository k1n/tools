#!/usr/bin/env python
#
# Copyright (c) 2008 Christian Hergert <chris@dronelabs.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import cairo
import gobject
import gtk
import pango
import pangocairo
import random

############################################################################
#  Cairo Helpers ported from Banshee (MIT/X11 by Aaron Bockover in C#)
############################################################################

def hsb_from_rgb(red, grn, blu):
    hue = 0
    sat = 0
    brt = 0
    _max = 0
    _min = 0
    if red > grn:
        _max = max(red, blu)
        _min = min(grn, blu)
    else:
        _max = max(grn, blu)
        _min = min(red, blu)
    brt = (_max + _min) / 2
    if abs(_max - _min) < 0.0001:
        hue = 0
        sat = 0
    else:
        if brt <= 0.5:
            sat = float(_max - _min) / float(_max + _min)
        else:
            sat = float(_max - _min) / float(2 - _max - _min)
        delta = float(_max - _min)
        if red == _max:
            hue = (grn - blu) / delta
        elif grn == _max:
            hue = 2 + (blu - red) / delta
        elif blu == _max:
            hue = 4 + (red - grn) / delta
        hue *= 60
        if hue < 0:
            hue += 360
    return hue, sat, brt

def rgb_from_hsb(h, s, b):
    def mod(n,d):
        return (n % d) + (n - int(n))
    if b <= 0.5:
        m2 = (b * (1 + s))
    else:
        m2 = b + s - b * s
    m1 = 2 * b - m2
    h_shift = (h + 120, h, h - 120)
    c_shift = [b, b, b]
    i = s == 0 and 3 or 0
    for i in range(i, 3):
        m3 = h_shift[i]
        if m3 > 360:
            m3 = mod(m3, 360)
        elif m3 < 0:
            m3 = 360 - mod(abs(m3), 360)
        if m3 < 60:
            c_shift[i] = m1 + (m2 - m1) * m3 / 60
        elif m3 < 180:
            c_shift[i] = m2
        elif m3 < 240:
            c_shift[i] = m1 + (m2 - m1) * (240 - m3) / 60
        else:
            c_shift[i] = m1
    return tuple(c_shift)

def color_shade(r, g, b, ratio):
    h, s, b = hsb_from_rgb(r, g, b)
    b = max(min(b * ratio, 1), 0)
    s = max(min(s * ratio, 1), 0)
    return rgb_from_hsb(h, s, b)

def random_shade_of(r, g, b):
    """
    Generates a random shade of the hue providedin @base.
    """
    ratio = random.random()
    while ratio < .2:
        ratio = random.random()
    return color_shade(r, g, b, ratio)

class TreeMap(gtk.DrawingArea):
    """
    A reusable TreeMap widget for gtk.
    """
    __gtype_name__ = 'GtkTreeMap'
    __gproperties__ = {
        'model': (gobject.GObject, 'Model', 'The data model', gobject.PARAM_READWRITE),
        'bg-color': (gtk.gdk.Color, 'Background', 'The background color', gobject.PARAM_WRITABLE),
    }

    # the gtk.TreeModel and signal handlers
    _model = None
    _model_handlers = None

    # our default background
    _bg_set = False
    _bg = None

    # the treepath for our current root
    _root = None

    # the text column
    _text_column = -1

    # how we get the row weight
    _weight_column = -1
    _weight_func = None
    _weight_args = None
    _weight_kwargs = None

    # title and it's sliding animation
    _title = 'Welcome to my treemap widget'
    _show_title = True
    _title_offset = 0
    _title_height = 36
    _animated = 0

    # layout cache of where items are (for click/hover)
    _item_cache = None
    _cursor = (-1, -1)
    _button_pressed = False

    def __init__(self):
        """Create a new TreeMap."""
        gtk.DrawingArea.__init__(self)
        self._cells = []
        self._attrs = {}
        self._cell_sizes = {}
        self._model_handlers = []
        self._weight_args = []
        self._weight_kwargs = {}
        self._item_cache = []
        self._last_cursor_match = None
        def setCursor(x,y):
            self._cursor = x,y
            self.queue_draw()
        def setButton(e):
            if not e:
                self._button_pressed = False
                self.queue_draw()
            else:
                if e.button == 1:
                    self._button_pressed = True
                    self.queue_draw()
        self.set_events(gtk.gdk.POINTER_MOTION_MASK      |
                        gtk.gdk.LEAVE_NOTIFY_MASK        |
                        gtk.gdk.POINTER_MOTION_HINT_MASK |
                        gtk.gdk.BUTTON_PRESS_MASK        |
                        gtk.gdk.BUTTON_RELEASE_MASK)
        self.connect('leave-notify-event', lambda *_: setCursor(-1, -1))
        self.connect('motion-notify-event', lambda _,e: setCursor(e.x, e.y))
        self.connect('button-press-event', lambda _,e: setButton(e))
        self.connect('button-release-event', lambda *_: setButton(None))

    def set_model(self, model):
        """Set the data gtk.TreeModel."""
        # disconnect old handlers
        if self._model:
            for handler_id in self._model_handlers:
                self._model.handler_disconnect(handler_id)
        self._model = model

        # connect handlers to regenerate image surface on change
        self._model_handlers = [
            self._model.connect('row-changed', lambda *_: self.cache_layout()),
            self._model.connect('row-deleted', lambda *_: self.cache_layout()),
            self._model.connect('row-inserted', lambda *_: self.cache_layout()),
            self._model.connect('rows-reordered', lambda *_: self.cache_layout()),
        ]

        # generate background with new data
        self._cache_background()

        # need redraw because of new data
        self.queue_draw()

    def get_model(self):
        """Get the data gtk.TreeModel."""
        return self._model

    def set_weight_column(self, column):
        """Set which column in the model has the item weighting."""
        assert column >= 0
        self._weight_column = int(column)
        self._weight_func = self._default_weight_func
        self._weight_args = []
        self._weight_kwargs = {}
        self.queue_draw()

    def get_weight_column(self):
        """
        Get which column in the model has the item weighting.  If the
        weight func is set, -1 is returned.
        """
        return self._weight_column

    def set_text_column(self, column):
        """
        The column in the model with the text for the treemap.
        """
        assert column >= 0
        self._text_column = column
        self.queue_draw()

    def get_text_column(self):
        """
        Retrieves the column that contains the text for the treemap.
        """
        return self._text_column

    def set_weight_func(self, func, *args, **kwargs):
        """
        Sets the callback to get the weight of an item.
        """
        self._weight_func = func
        self._weight_args = args
        self._weight_kwargs = kwargs

    def pack_start(self, cell, expand=True):
        """
        Pack a cell renderer into the TreeMap.
        
        Parameters:
          @cell: a gtk.CellRenderer
          @expand: should the cell expand to as much space as possible within
                   the allocated area.
        """
        self._cells.append((cell, expand))
        self._attrs[cell] = {}

    def add_attribute(self, cell, *args):
        """
        Add a property attribute for @cell that will be set before each
        cell renderering with the content from the data store.

        Parameters:
          @cell: a gtk.CellRenderer
          @args: args in multiples of two containing 'property name' and
                 model column.

        >>> treemap = TreeMap()
        >>> cell = gtk.CellRendererText()
        >>> treemap.pack_start(cell, True)
        >>> treemap.add_attribute(cell, 'text', 0)
        """
        if cell not in self._attrs:
            raise AttributeError, 'cell is not packed into the TreeMap'
        if len(args) % 2 != 0:
            raise AttributeError, 'args must be in sets of 2'
        attrs = {}
        i = 0
        while i < len(args):
            k,v = args[i:i+2]
            attrs[k] = v
            i += 2
        self._attrs[cell].update(attrs)

    def do_set_property(self, pspec, value):
        """
        GObject property setter.
        """
        if pspec.name == 'model':
            if not isinstance(value, gtk.TreeModel):
                raise TypeError, 'value must be of type gtk.TreeModel'
            self._model = value
        elif pspec.name == 'bg-color':
            self._bg = value
            self._bg_set = True
            if not value:
                self._bg_set = False
                self.on_style_set(None)
        else:
            raise AttributeError, 'invalid property %s' % pspec.name

    def do_get_property(self, pspec):
        """
        GObject property getter.
        """
        if pspec.name == 'model':
            return self._model
        else:
            raise AttributeError, 'invalid property %s' % pspec.name

    def do_style_set(self, old_style):
        if not self._bg_set:
            self._bg = self.style.bg[gtk.STATE_NORMAL]

    def do_realize(self):
        gtk.DrawingArea.do_realize(self)

    def do_size_allocate(self, alloc):
        gtk.DrawingArea.do_size_allocate(self, alloc)
        self._cache_background()

    def area_from_cursor(self):
        if self._cursor == (-1, -1):
            return None
        
        cx, cy = self._cursor
        items = self._item_cache

        # Check the last cursor match
        if self._last_cursor_match:
            x, y, w, h = self._last_cursor_match[2]
            if cx >= x and cx <= x + w:
                if cy >= y and cy <= y + h:
                    return self._last_cursor_match

        # find the item that best matches in each level
        # and then try to dive deeper into its children
        while items:
            next_item = None
            matched = False
            for item in items:
                _, _, (x, y, w, h) = item[:3]
                if cx >= x and cx <= x + w:
                    if cy >= y and cy <= y + h:
                        matched = item
                        next_item = item[3]
                        break
            if matched and not next_item:
                # we cache this box to save ourself a long lookup
                # next time around
                self._last_cursor_match = matched
                return matched
            items = next_item

    def do_expose_event(self, event):
        # create cairo handle
        c = self.window.cairo_create()

        # clip drawing region to event area
        c.rectangle(event.area)
        c.clip()

        # if there is not proper weighting information then we can't
        # really do an expose. so we can just clear the area and return
        if not self._has_valid_weighting():
            c.fill()
            return

        # paint actual treemap
        c.set_source_surface(self._bg_surface, 0, 0)
        c.paint()

        # highlight the selected grid if needed
        area = self.area_from_cursor()
        if area:
            _, _, (x, y, w, h) = area[:3]
            c.rectangle(x, y, w, h)
            if self._button_pressed:
                c.set_source_rgba(0, 0, 0, 0.1)
            else:
                c.set_source_rgba(1, 1, 1, 0.1)
            c.fill()
            pass

        # paint the title if needed
        if self._show_title:
            self.do_expose_title(c)

        del c

    def do_expose_title(self, c):
        # paint the translucent background
        c.set_source_rgba(0, 0, 0, 0.3)
        c.rectangle(0, self._title_offset, self.allocation.width, self._title_height)
        c.fill()

        # paint the lower title shadow
        c.rectangle(0, self._title_offset + self._title_height, self.allocation.width, 3)
        c.set_source_rgba(0, 0, 0, 0.1)
        c.fill()

        # paint the title text
        c.set_source_rgba(1, 1, 1, 1)
        p = c.create_layout()
        p.set_text(self._title)
        _, h = p.get_pixel_size()
        pad = (self._title_height - h) / 2
        c.move_to(pad, self._title_offset + pad)
        c.show_layout(p)
        del p

    def hide_title(self):
        """
        Hides the title bar from the widget using a linear slide animation.
        """
        if self._animated:
            gobject.source_remove(self._animated)
        def hide_func():
            if self._title_offset > -self._title_height:
                self._title_offset -= 2
                self.queue_draw()
            return self._title_offset > -self._title_height
        if self._title_offset != -self._title_height:
            self._animated = gobject.timeout_add(10, hide_func)

    def show_title(self):
        """
        Shows the title bar on the widget using a linear slide animation.
        """
        if self._animated:
            gobject.source_remove(self._animated)
        def show_func():
            if self._title_offset < 0:
                self._title_offset += 2
                self.queue_draw()
            return self._title_offset < 0
        if self._title_offset != 0:
            self._animated = gobject.timeout_add(10, show_func)

    def _cache_background(self):
        # clear cache entries
        self._last_cursor_match = None
        self._item_cache = []

        # make sure we can generate the image surface
        if not self._has_valid_weighting():
            return

        if hasattr(self, '_bg_surface'):
            self._bg_surface.finish()
            del self._bg_surface

        # get bounding box and create image surface
        w = self.allocation.width
        h = self.allocation.height
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
        c = cairo.Context(s)
        other = lambda d: d == 'horiz' and 'vert' or 'horiz'

        # get the items for the layer and draw it
        m = self._model
        def do_layer(i, x, y, w, h, direction='horiz', parent=None):
            items = []
            while i:
                weight = self._weight_func(m, i,
                                           *self._weight_args,
                                           **self._weight_kwargs)
                items.insert(0, [m.get_path(i), weight])
                i = m.iter_next(i)
            items.sort(lambda x,y: cmp(y[1], x[1]))
            if parent:
                parent.append(items)
            else:
                self._item_cache = items
            self._draw_layer(c, items, x, y, w, h, direction)
            for item in items:
                path, _, bbox = item
                i = m.get_iter(path)
                i = m.iter_children(i)
                do_layer(i, direction=other(direction), parent=item, *bbox)
        do_layer(m.get_iter_root(), 0, 0, w, h)

        # cache surface for rendering our background
        self._bg_surface = s

    def _draw_layer(self, c, rows, x, y, w, h, direction='horiz'):
        """
        Draws the data in rows by laying them out by weight within the
        bounding box x, y, w, h.  Rows is a list of 2-part tuple like
        [(gtk.TreePath, weight)].
        """
        if direction not in ('horiz', 'vert'):
            raise ValueError, 'Invalid direction "%s"' % direction

        # calculate the total weight ignoring integer sign
        total = float(sum([abs(b) for a,b in rows]))

        # nothing to draw
        if total == 0:
            return

        base = self.style.bg[gtk.STATE_SELECTED]
        base = (float(base.red)   / 65535,
                float(base.green) / 65535,
                float(base.blue)  / 65535)
        color = lambda: random_shade_of(*base)

        pc = pangocairo.CairoContext(c)

        # draw items for the layer
        for row in rows:
            path, weight = row[:2]
            myx, myy = x, y
            rate = (abs(weight) / total)

            # get our bounding box and update free space
            if direction == 'horiz':
                myw = w * rate
                myh = h
                x += myw
            else:
                myw = w
                myh = h * rate
                y += myh

            # track the bounding box
            row.append((myx, myy, myw, myh))

            # create shapes and fill
            c.rectangle(myx, myy, myw, myh)
            c.set_source_rgb(*color())
            c.fill()

            # try to place the text
            _iter = self._model.get_iter(path)
            text = self._model.get_value(_iter, self._text_column)
            l = pc.create_layout()
            l.set_width(int(myw * pango.SCALE))
            l.set_text(text)
            lw, lh = l.get_pixel_size()
            if lw <= myw and lh <= myh:
                c.set_source_rgb(1, 1, 1)
                c.move_to(myx + ((myw - lw) / 2), myy + ((myh - lh) / 2))
                pc.show_layout(l)
            del l

        del pc

    def _has_valid_weighting(self):
        if self._weight_func == self._default_weight_func:
            return self._weight_column >= 0
        return True

    def _default_weight_func(self, model, _iter):
        return model.get_value(_iter, self._weight_column)

if __name__ == '__main__':
    win = gtk.Window()
    win.set_title('Cairo TreeMap')
    win.set_default_size(640, 480)
    win.props.border_width = 24
    win.connect('delete-event', lambda *_: gtk.main_quit())
    f = gtk.Frame()
    f.set_shadow_type(gtk.SHADOW_NONE)
    win.add(f)
    f.show()
    treemap = TreeMap()
    f.add(treemap)
    treemap.show()
    model = gtk.TreeStore(str, int)
    i = model.append(None, row=('Item 1', 6))
    model.append(i, row=('Item 1.1', 5))
    j = model.append(i, row=('Item 1.2', 13))
    model.append(j, row=('Item 1.2.1', 8))
    model.append(j, row=('Item 1.2.2', 7))
    model.append(j, row=('Item 1.2.3', 3))
    k = model.append(j, row=('Item 1.2.4', 8))
    model.append(k, row=('Item 1.2.4.1', 2))
    model.append(k, row=('Item 1.2.4.2', 7))
    model.append(k, row=('Item 1.2.4.3', 9))
    model.append(i, row=('Item 1.3', 8))
    model.append(i, row=('Item 1.4', 17))
    model.append(i, row=('Item 1.5', 19))
    model.append(i, row=('Item 1.6', 3))
    model.append(None, row=('Item 4', 4))
    model.append(None, row=('Item 3', 3))
    model.append(None, row=('Item 2', 2))
    model.append(None, row=('Item 5', 5))
    model.append(None, row=('Item 6', 6))
    treemap.set_weight_column(1)
    treemap.set_text_column(0)
    treemap.set_model(model)
    treemap.props.bg_color = gtk.gdk.Color(5000, 50000, 13000)
    treemap.props.bg_color = win.style.bg[gtk.STATE_SELECTED]
    GDK_q = gtk.gdk.keyval_from_name('q')
    def quit_on_key(w,e,k):
        if e.keyval == gtk.gdk.keyval_from_name(k):
            gtk.main_quit()
    win.connect('key-press-event', quit_on_key, 'q')
    gobject.timeout_add_seconds(3, treemap.hide_title)
    e = treemap.get_events()
    treemap.set_events(e | gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)
    treemap.connect('enter-notify-event', lambda *_: treemap.show_title())
    treemap.connect('leave-notify-event', lambda *_: treemap.hide_title())
    win.show()
    gtk.main()
