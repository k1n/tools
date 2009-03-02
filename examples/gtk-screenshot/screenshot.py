#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# Author: 山猫
# License: GNU LGPL
# Last modified:


"""Gtk 截图程序示例
__revision__ = '0.1'
"""

import sys, time
import gtk


def screenshot(filename=''):
    w = gtk.gdk.screen_width()
    h = gtk.gdk.screen_height()
    screenshot = gtk.gdk.Pixbuf.get_from_drawable(
            gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h),
            gtk.gdk.get_default_root_window(),
            gtk.gdk.colormap_get_system(),
            0, 0, 0, 0, w, h)
    screenshot.save(filename or time.strftime('%Y-%m-%d-%s.png'), 'png')

def screenshotthumb(filename='', width=200, height=200):
    w = gtk.gdk.screen_width()
    h = gtk.gdk.screen_height()
    screenshot = gtk.gdk.Pixbuf.get_from_drawable(
            gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h),
#            gtk.gdk.get_default_root_window(),
            gtk.gdk.window_get_toplevels()[1],
            gtk.gdk.colormap_get_system(),
            0, 0, 0, 0, w, h)
    width, height = _size(screenshot.get_width(), screenshot.get_height(), width, height)
    thumb = screenshot.scale_simple(width, height, gtk.gdk.InterpType(2))
    thumb.save(filename or time.strftime('%Y-%m-%d-%s.png'), 'png')

def _scale_size(width, height, twidth, theight):
    rw = 1.0 * width/twidth
    rh = 1.0 * height/theight
    r = max(rh, rw)
    return int(width/r), int(height/r)

if __name__=="__main__":
    screenshot((sys.argv+[''])[1])
