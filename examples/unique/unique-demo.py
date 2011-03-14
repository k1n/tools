#!/usr/bin/python

from gi.repository import Gtk, Unique

class MainWindow(Gtk.Window):
    pass

def message_received_cb(app, command, message, time, window):
    print app, command, message, time
    if command == Unique.Command.ACTIVATE:
        window.present()

    return False

if __name__ == '__main__':
    app = Unique.App(name='me.imtx.unique-demo', startup_id='')
    
    if app.is_running():
        app.send_message(Unique.Command.ACTIVATE, Unique.MessageData())
    else:
        window = MainWindow()
        app.watch_window(window)
        window.connect("destroy", Gtk.main_quit)
        app.connect("message-received", message_received_cb, window)

        window.show_all()
        Gtk.main()
