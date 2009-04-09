#!/usr/bin/python
# coding=utf-8

import gtk
import gobject

class GettableList (list):
    '''Dumb wrapper around Python list with a get () method to iterate \
the list'''

    current = 0

    def get (self):
        if not len (self):
            return None
        if self.current == -1:
            item = None
        else:
            item = self[self.current]
        self.current += 1
        if self.current == len (self):
            self.current = -1
        else:
            self.current = self.current % len (self)
        return item

# Animation is done using:
#  * A custom gtk.Label, for catching mouse press events
#  * A gtk.Alignment, for positionning and scrolling (the actual animation)
#  * A gtk.Layout, so that the Alignment can be wider than what's displayed
#    and thus let the Label appear and disappear smoothly

class AnimatedLabel (gtk.Layout):
    '''Pretty animated label'''

    items   = None # items must either be a GettableList object
                   # or expose a get () method'''
    timeout = 0
    format  = ""   # format must be a valid formatting string for a single %s

    item    = None
    next    = None

    current = None
    label   = None
    source  = None
    state   = 0    # 0 = appearing ; 1 = landed ; 2 = vanishing
    pos     = 0.0

    width   = 0
    height  = 0

    def __init__ (self, items, width, height, timeout, format = "%s"):
        '''Initiate object'''
        super (AnimatedLabel, self).__init__ ()
        self.items = items
        self.next = self.items.get () # Pop the first item
        self.width = width
        self.height = height
        self.timeout = timeout
        self.format = format
        self.set_size_request (width, height)
        self.connect ("button-press-event", self.on_button_press)
        self.connect ("map", self.reset_animation)

    def reset_animation (self, *args):
        '''Reset label and fire animation timer'''
        self.reset_label ()
        if not self.label:
            return
        self.source = gobject.timeout_add (5, self.animate)

    def make_label (self):
        '''Build the label widgets'''
        self.label = WindowedLabel ()
        self.label.connect ("button-press-event", self.on_button_press)
        self.label.set_justify (gtk.JUSTIFY_FILL)
        self.label.set_line_wrap (True)
        self.label.set_markup (self.format % self.item)
        self.label.set_selectable (True)

    def reset_label (self):
        '''Drop current label if any and create the new one'''
        if self.current:
            self.remove (self.current)
            self.current = None
            self.label = None
        self.item = self.next
        self.next = self.items.get ()
        if not self.item:
            return False
        self.make_label ()
        self.state = -1

    def on_button_press (self, widget, event):
        '''Switch to next item upon left click'''
        if event.button != 1 or not self.current:
            return
        # Remove the current timeout if any to avoid bad side effects
        if self.source:
            gobject.source_remove (self.source)
        self.animate ()
        return True

class VertAnimatedLabel (AnimatedLabel):
    '''Vertically animated label'''

    rewind_text       = ""
    last_label_height = 0

    def rewind_animate (self):
        '''Animation function for the rewind step'''
        self.source = None
        if self.state == -2:
            self.item = self.rewind_text
            self.make_label ()
            label_height = self.label.size_request ()[1]
            total_height = self.height + label_height
            self.pos = float (self.last_label_height) / total_height
            self.current.set (0.5, self.pos, 0, 0)
            self.state = 0
            self.source = gobject.timeout_add (10, self.rewind_animate)
        elif self.state == 0:
            if self.pos < 1.0:
                '''Move towards the bottom position'''
                self.pos = min (1.0, self.pos + 0.01)
                self.current.set (0.5, self.pos, 0, 0)
                self.source = gobject.timeout_add (10, self.rewind_animate)
            else:
                '''Bottommost position reached'''
                self.rewind_text = ""
                self.reset_animation ()
        return False

    def animate (self):
        '''The actual animation function'''
        self.source = None
        if self.state == -2:
            self.rewind_animate ()
        elif self.state == -1:
            self.rewind_text += "\n\n%s" % self.item
            self.state = 0
            self.animate ()
        elif self.state == 0:
            if self.pos:
                '''Move towards the top position'''
                self.pos = max (0, self.pos - 0.02)
                label_height = self.label.size_request ()[1]
                total_height = self.height + label_height
                real_pos = float (self.pos * self.height + label_height) \
                            / total_height
                self.current.set (0.5, real_pos, 0, 0)
                self.source = gobject.timeout_add (5, self.animate)
            else:
                '''Topmost position reached'''
                self.state = 1
                self.pos = 1.0
                self.source = gobject.timeout_add (self.timeout, self.animate)
        elif self.state == 1:
            '''Dont let selected labels vanish until they are unselected'''
            if self.label.get_selection_bounds () == ():
                self.state = 2
            self.source = gobject.timeout_add (5, self.animate)
        elif self.state == 2:
            if not self.next:
                self.state = -2
                self.last_label_height = self.label.size_request ()[1]
                self.reset_animation ()
                self.source = gobject.timeout_add (1, self.animate)
            elif self.pos:
                '''Move out of the visible region of the Layout'''
                self.pos = max (0, self.pos - 0.02)
                label_height = self.label.size_request ()[1]
                total_height = self.height + label_height
                real_pos = float (self.pos * label_height) \
                            / total_height
                self.current.set (0.5, real_pos, 0, 0)
                self.source = gobject.timeout_add (5, self.animate)
            else:
                '''Label has disappeared, bye bye'''
                self.reset_animation ()
        return False

    def make_label (self):
        '''Build a new label widget'''
        super (VertAnimatedLabel, self).make_label ()
        if not self.label:
            return
        self.label.set_size_request (self.width, -1)
        self.current = gtk.Alignment (0.0, 1.0)
        label_height = self.label.size_request ()[1]
        height = self.size_request ()[1]
        self.current.set_size_request (-1, 2 * label_height + height)
        self.current.add (self.label)
        self.put (self.current, 0, - label_height)
        self.pos = 1.0
        self.show_all ()

class HorzAnimatedLabel (AnimatedLabel):
    '''Horizontally animated label'''

    def animate (self):
        '''The actual animation function'''
        self.source = None
        if self.state == -2:
            self.reset_animation ()
        elif self.state <= 0:
            if self.pos != 0.5:
                '''Move towards the center position'''
                self.pos = max (0.5, self.pos - 0.02)
                self.current.set (self.pos, 0.5, 0, 0)
                self.source = gobject.timeout_add (5, self.animate)
            else:
                '''Center position reached, switch to return mode'''
                self.state = 1
                self.source = gobject.timeout_add (self.timeout, self.animate)
        elif self.state == 1:
            '''Dont let selected labels vanish until they are unselected'''
            if self.label.get_selection_bounds () == ():
                self.state = 2
            self.source = gobject.timeout_add (5, self.animate)
        elif self.state == 2:
            if self.pos:
                '''Disappear by moving left'''
                self.pos = max (0, self.pos - 0.02)
                self.current.set (self.pos, 0.5, 0, 0)
                self.source = gobject.timeout_add (5, self.animate)
            else:
                '''Left position reached, let's move on'''
                self.reset_animation ()
        return False

    def make_label (self):
        '''Build a new label widget'''
        super (HorzAnimatedLabel, self).make_label ()
        if not self.label:
            return
        self.label.set_size_request (-1, self.height)
        self.current = gtk.Alignment (1.0, 0.0)
        label_width = self.label.size_request ()[0]
        width = self.size_request ()[0]
        self.current.set_size_request (2 * label_width + width, -1)
        self.current.add (self.label)
        self.put (self.current, - label_width, 0)
        self.pos = 1.0
        self.show_all ()

class WindowedLabel (gtk.Label):
    '''Custom gtk.Label with an overlapping input-only gtk.gdk.Window'''

    event_window = None

    def __init__ (self, debug = False):
        '''Initialize object and plug all signals'''
        self.debug = debug
        super (WindowedLabel, self).__init__ ()

    def do_realize (self):
        '''Create a custom GDK window with which we will be able to play'''
        gtk.Label.do_realize (self)
        event_mask = self.get_events () | gtk.gdk.BUTTON_PRESS_MASK \
                                        | gtk.gdk.BUTTON_RELEASE_MASK \
                                        | gtk.gdk.KEY_PRESS_MASK
        self.event_window = gtk.gdk.Window (parent = self.get_parent_window (),
                                            window_type = gtk.gdk.WINDOW_CHILD,
                                            wclass = gtk.gdk.INPUT_ONLY,
                                            event_mask = event_mask,
                                            x = self.allocation.x,
                                            y = self.allocation.y,
                                            width = self.allocation.width,
                                            height = self.allocation.height)
        self.event_window.set_user_data (self)

    def do_unrealize (self):
        '''Destroy event window on unrealize'''
        self.event_window.set_user_data (None)
        self.event_window.destroy ()
        gtk.Label.do_unrealize (self)

    def do_size_allocate (self, allocation):
        '''Move & resize the event window to fit the Label's one'''
        gtk.Label.do_size_allocate (self, allocation)
        if self.flags () & gtk.REALIZED:
            self.event_window.move_resize (allocation.x, allocation.y,
                                           allocation.width, allocation.height)

    def do_map (self):
        '''Show event window'''
        gtk.Label.do_map (self)
        self.event_window.show ()
        '''Raise the event window to make sure it is over the Label's one'''
        self.event_window.raise_ ()

    def do_unmap (self):
        '''Hide event window on unmap'''
        self.event_window.hide ()
        gtk.Label.do_unmap (self)

gobject.type_register (WindowedLabel)

class GnomeAbout (gtk.Dialog):
    def __init__ (self):
        super (GnomeAbout, self).__init__ ("About the GNOME Desktop",
                                           buttons = (gtk.STOCK_CLOSE,
                                                      gtk.RESPONSE_CLOSE))

        self.set_default_size(400, 300)                                            
        alignment = gtk.Alignment (0.5, 0.5)
        label = HorzAnimatedLabel (GettableList(['hello', 'world', 'haha']), 400,
                                   30, 3000, "<b>%s</b>")
        alignment.add (label)
        self.vbox.pack_start (alignment)

        self.connect ("delete-event", gtk.main_quit)
        self.connect ("response", self.response_callback)

    def response_callback (self, widget, response):
        '''Handle dialog response when Close button is triggered'''
        if response == gtk.RESPONSE_CLOSE:
            gtk.main_quit ()

if __name__ == "__main__":
    about = GnomeAbout ()
    about.show_all ()
    gtk.main()
