#! /usr/bin/env python

import gtk
import dbus
import gobject
import dbus.service
import dbus.mainloop.glib

gobject.threads_init()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
dbus.mainloop.glib.threads_init()

# Connect to the bus
bus = dbus.SessionBus()

# Define a D-BUS object
class SignalObject(dbus.service.Object):
    def __init__(self, conn, object_path='/'):
        dbus.service.Object.__init__(self, conn, object_path)

    @dbus.service.signal('com.burtonini.dbus.Signal')
    def broadcast_signal(self, message):
        # The signal is emitted when this method exits
        # You can have code here if you wish
        pass
# Create an instance of the object, which is part of the service
signal_object = SignalObject(bus)

def send_ping():
    signal_object.broadcast_signal("WTF?")
    print "Ping!"
    return True

# Call send_ping every second to send the signal
gobject.timeout_add(1000, send_ping)
gtk.main()
