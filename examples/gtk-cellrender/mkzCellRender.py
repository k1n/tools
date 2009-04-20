import gtk
import pango
import cairo
import gobject

class mkzCellRender(gtk.GenericCellRenderer):
	__gproperties__ = {
			'text': (gobject.TYPE_STRING,
				'Text to be displayed',
				'Text to be displayed',
				'',
				gobject.PARAM_READWRITE
				),
			'background': (gobject.TYPE_STRING,
				'Background of the cell',
				'The background of the cell',
				'#FFFFFF',
				gobject.PARAM_READWRITE
				)
			}

	def __init__(self):
		#gobject.GObject.__init__(self)
		gtk.GenericCellRenderer.__init__(self)
		self.__properties = {}
		#gtk.GenericCellRenderer.__init__(self)
	
	def on_get_size(self, widget, cell_area):
		#print "on_get_size, ", locals()
		if cell_area == None:
			return (0,0,0,0)
		x = cell_area.x
		y = cell_area.x
		w = cell_area.width
		h = cell_area.height

		return (x,y,w,h)

	def do_set_property(self, key, value):
		self.__properties[key] = value
	
	def do_get_property(self, key):
		return self.__properties[key]

	def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
		cairo_context = window.cairo_create()
		x = cell_area.x 
		y = cell_area.y 
		w = cell_area.width
		h = cell_area.height 
		if x == 0:
			curve_to = 'start'
		elif (x + w ) == widget.allocation.width:
			curve_to = 'end'
		else:
			curve_to = None
		self.render_rect(cairo_context, x, y, w, h, 1, curve_to)
		pat = cairo.LinearGradient(x, y, x, y + h)
		color = gtk.gdk.color_parse("#87D8F5")
		pat.add_color_stop_rgba(
							0.0,
							self.get_cairo_color(color.red),
							self.get_cairo_color(color.green),
							self.get_cairo_color(color.blue),
							1
							)
		color = gtk.gdk.color_parse(self.get_property('background'))
		pat.add_color_stop_rgb(
							1.0,
							self.get_cairo_color(color.red),
							self.get_cairo_color(color.green),
							self.get_cairo_color(color.blue)
							)
####	pat.add_color_stop_rgb(
####						0.8,
####						self.get_cairo_color(color.red),
####						self.get_cairo_color(color.green),
####						self.get_cairo_color(color.blue)
####						)

####	color = gtk.gdk.color_parse("#ffffff")
####	pat.add_color_stop_rgba(
####						1.0,
####						self.get_cairo_color(color.red),
####						self.get_cairo_color(color.green),
####						self.get_cairo_color(color.blue),
####						1
####						)

		cairo_context.set_source(pat)
		cairo_context.fill()

		context = widget.get_pango_context()
		layout = pango.Layout(context)
		layout.set_text(self.get_property('text'))
		layout.set_width(cell_area.width)
		widget.style.paint_layout(window, gtk.STATE_NORMAL, True,
					cell_area, widget, 'footext',
					cell_area.x, cell_area.y,
					layout)

	def render_rect(self, cr, x, y, w, h, o, curve_to):
		'''
		create a rectangle with rounded corners
		'''
		x0 = x
		y0 = y
		rect_width = w
		rect_height = h
		radius = 2 + o

		if curve_to == 'start':
			x1 = x0 + rect_width
			y1 = y0 + rect_height
			cr.move_to(x0, y0 + radius)
			cr.curve_to(x0, y0+radius, x0, y0, x0 + radius, y0)

			cr.line_to(x1, y0)
			cr.line_to(x1, y1)
			cr.line_to(x0 +radius, y1)
			cr.curve_to(x0+radius, y1, x0, y1, x0, y1-radius -1)
			cr.close_path()
		elif curve_to == 'end':
			x1 = x0 + rect_width
			y1 = y0 + rect_height
			cr.move_to(x0, y0)

			cr.line_to(x1 - radius, y0)
			cr.curve_to(x1-radius, y0, x1, y0, x1, y0 + radius)
			cr.line_to(x1, y1-radius)
			cr.curve_to(x1, y1-radius, x1, y1, x1 -radius, y1)
			cr.line_to(x0, y1)
			cr.close_path()
		else:
			x1 = x0 + rect_width
			y1 = y0 + rect_height
			cr.move_to(x0, y0 )
			cr.line_to(x1, y0)
			cr.line_to(x1, y1)
			cr.line_to(x0, y1)
			cr.close_path()



		
	
	def get_cairo_color(self, color):
		ncolor = color/65535.0
		return ncolor
		

	def on_activate(self, event, widget, path, background_area, cell_area, flags):
		print "on_activate, ", locals()
		pass

	def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
		print "on_activate, ", locals()
		pass

gobject.type_register(mkzCellRender)
