#!/usr/bin/python

import gtk

UNO,DOS,BG = range(3)

model = gtk.ListStore(int, int, str)
for i in xrange(99):
	iter = model.append()
	val = str(i)
	color = "#84AFBE"
	model.set(iter, 
			UNO, i, 
			DOS, i,
			BG, color)

import mkzCellRender
render = mkzCellRender.mkzCellRender()
#render = gtk.CellRendererText()

window = gtk.Window()
window.connect('destroy',gtk.main_quit)
treeview = gtk.TreeView(model)
column1 = gtk.TreeViewColumn('UNO', render, text = UNO, background= BG)
column2 = gtk.TreeViewColumn('DOS', render,text = DOS, background=BG)
column3 = gtk.TreeViewColumn('BG', render,text = BG, background=BG)
treeview.append_column(column1)
treeview.append_column(column2)
treeview.append_column(column3)
scrolledw = gtk.ScrolledWindow()
scrolledw.add(treeview)
window.add(scrolledw)
window.set_size_request(400,400)
window.show_all()


gtk.main()
