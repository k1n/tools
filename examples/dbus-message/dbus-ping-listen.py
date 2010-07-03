#! /usr/bin/env python

import gtk
import dbus
import gobject
import dbus.service
import dbus.mainloop.glib

gobject.threads_init()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
dbus.mainloop.glib.threads_init()

bus = dbus.SessionBus()

def signal_callback(message):
    print "Received signal with message:", message

# Catch signals from a specific interface and object, and call signal_callback
# when they arrive.
bus.add_signal_receiver(signal_callback,
                        signal_name='broadcast_signal',
                        dbus_interface="com.burtonini.dbus.Signal", # Interface
                        )

# Enter the event loop, waiting for signals
gtk.main()
