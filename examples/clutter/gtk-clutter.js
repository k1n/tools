const GtkClutter = imports.gi.GtkClutter;
const Gtk = imports.gi.Gtk;

GtkClutter.init('');

let win = new GtkClutter.Window();
let button = new Gtk.Button({label: 'Hello'});

win.add(button);
win.set_border_width(20);
win.set_default_size(240, 120);
win.show_all()

Gtk.main();
