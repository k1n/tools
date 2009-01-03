#!/usr/bin/python

import gtk

from model import MyModel
from view import MyView
from ctrl import MyController

m = MyModel()
c = MyController(m)
v = MyView(c)

gtk.main()
