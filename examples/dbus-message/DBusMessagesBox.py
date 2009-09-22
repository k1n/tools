#!/usr/bin/python

import os
import re
import pygtk
pygtk.require('2.0')
import gtk

import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from _dbus_bindings import Connection as _Connection

DBUS_MESSAGE_TYPE_METHOD_CALL = 1
DBUS_MESSAGE_TYPE_METHOD_RETURN = 2
DBUS_MESSAGE_TYPE_ERROR = 3
DBUS_MESSAGE_TYPE_SIGNAL = 4

DBUS_MESSAGES_BOX_DOMAIN = "org.invaliddomain.DBusMessagesBox"

dbus_message_type = { DBUS_MESSAGE_TYPE_METHOD_CALL : "method_call",
                      DBUS_MESSAGE_TYPE_METHOD_RETURN : "method_return",
                      DBUS_MESSAGE_TYPE_ERROR : "error",
                      DBUS_MESSAGE_TYPE_SIGNAL : "signal"
                    }

class DBusMessagesBox:
    messages = []
    entities = {}

    def print_msg(self, msg):
        print "== New message =="
        print "type = " + dbus_message_type[msg.get_type()]
        if (msg.get_sender()):
            print "sender = " + msg.get_sender()
        else:
            print "sender = None"
        if (msg.get_destination()):
            print "destination = " + msg.get_destination()
        else:
            print "destination = None"
        if (msg.get_serial()):
            print "serial = ",
            print msg.get_serial()
        else:
            print "serial = None"
        if (msg.get_path()):
            print "path = " + msg.get_path()
        else:
            print "path = None"
        if (msg.get_interface()):
            print "interface = " + msg.get_interface()
        else:
            print "interface = None"
        if (msg.get_member()):
            print "member = " + msg.get_member()
        else:
            print "member = None"
        print "================="

    def get_human_name(self, name):
        if name[0] == ':':
            best_candidates = []
            candidates = []
            for k, v in self.entities.iteritems():
                if v['owner'] == name and k[0] != ':':
                    candidate = k[k.rfind(".")+1:]
                    if candidate in self.options['prefered_names']:
                        best_candidates.append(candidate)
                    else:
                        candidates.append(candidate)
            if len(best_candidates) != 0:
                return best_candidates[0]
            elif len(candidates) != 0:
                if len(candidates) > 1:
                    print "Multiple candidates:"
                    print candidates
                    print "You can choose with the 'prefered_names' option"
                return candidates[0]
            else:
                return name
        else:
            return name[name.rfind(".")+1:]

    def parse(self, mscfile):
        f=open(mscfile, 'w')

        seen = {}

        # take only entities that have sent or received at least 1 message
        entities_with_msg = filter(lambda s: self.entities[s]['nb_msg'] > 0, self.entities.keys())
        owners = map(lambda s: self.entities[s]['owner'], entities_with_msg)
        for item in owners:
            short_item = self.get_human_name(item)
            if not short_item in skip_entities:
                seen[short_item] = seen.get(short_item, 0) + 1
        uniq = sorted(seen.keys())

        f.write("msc {\n")
        f.write("  ")
        f.write(','.join(map(lambda s: '"' + s + '"', uniq)),)
        f.write(";\n\n")

        for i, msg_record in enumerate(self.messages):
            if msg_record['skip']:
                continue

            # change the sender and dest strings at parsing time because
            # we cannot do it at receiving time
            msg_record['sender_str'] = self.get_human_name(msg_record['sender_str'])
            if msg_record['dest_str'] != "":
                msg_record['dest_str'] = self.get_human_name(msg_record['dest_str'])

            if msg_record['sender_str'] in self.options['skip_entities']:
                continue
            if msg_record['dest_str'] in self.options['skip_entities']:
                continue

            f.write('  "' + msg_record['sender_str'] + '"')
            f.write(msg_record['symbol_str'])
            if msg_record['message'].get_type() != DBUS_MESSAGE_TYPE_SIGNAL:
                f.write('"' + msg_record['dest_str'] + '"')
            f.write(' [ label = "(#%d)'%(i) + msg_record['label_str'] + '",')
            f.write(' URL = "' + msg_record['URL_str'] + '" ] ;\n')

        f.write("}\n\n")

    def add_new_entity(self):
        print "##### call list_names ####"
        for n in self.bus.list_names():
            print "entity %s" % (n)
            if not self.entities.has_key(n):
                print "============ add new entity '%s' =============" % (n)
                self.entities[n] = { 'serial' : {}, 'nb_msg' : 0 }
                if n[0] == ':':
                    self.entities[n]['owner'] = n
                else:
                    self.entities[n]['owner'] = self.bus.get_name_owner(n)
                print "============  owner is      '%s' =============" % (self.entities[n]['owner'])
        print "##########################"

    def add_msg(self, msg):
        print "adding new message"
        msg_record = { 'skip' : 0 }
        msg_record['message'] = msg
        indice = len(self.messages)
        msg_record['URL_str'] = "%d" % (indice)

        if (msg.get_type() == DBUS_MESSAGE_TYPE_METHOD_CALL):
            sender = msg.get_sender()
            dest = msg.get_destination()
            serial = msg.get_serial()

            msg_record['sender_str'] = sender
            msg_record['dest_str'] = dest
            msg_record['symbol_str'] = '=>'
            msg_record['label_str'] = 'call ' + msg.get_member() + (" (s=%d)" % (serial))

            if not self.entities.has_key(sender):
                self.add_new_entity()
            if not self.entities.has_key(dest):
                self.add_new_entity()

            self.entities[sender]['nb_msg'] +=1
            self.entities[dest]['nb_msg'] += 1
            self.entities[sender]['serial'][serial] = {}
            self.entities[sender]['serial'][serial]['call_indice'] = indice
            self.entities[sender]['serial'][serial]['return_indice'] = None

        elif (msg.get_type() == DBUS_MESSAGE_TYPE_METHOD_RETURN):
            sender = msg.get_sender()
            dest = msg.get_destination()
            serial = msg.get_reply_serial()
            member = '???'

            if not self.entities.has_key(sender):
                self.add_new_entity()
            if not self.entities.has_key(dest):
                self.add_new_entity()

            if not self.entities[dest]['serial'].has_key(serial):
                print "Warning: method return (%s->%s) without call: serial %d" \
                      % (self.get_human_name(sender), \
                         self.get_human_name(dest), serial)
            else:
                call_indice = self.entities[dest]['serial'][serial]['call_indice']
                member = self.messages[call_indice]['message'].get_member()

            msg_record['sender_str'] = sender
            msg_record['dest_str'] = dest
            msg_record['symbol_str'] = '>>'
            msg_record['label_str'] = member + ' returns' + (" (s=%d)" % (serial))

            self.entities[sender]['nb_msg'] += 1
            self.entities[dest]['nb_msg'] += 1
            self.entities[dest]['serial'][serial] = {}
            self.entities[dest]['serial'][serial]['return_indice'] = indice

        elif (msg.get_type() == DBUS_MESSAGE_TYPE_SIGNAL):
            sender = msg.get_sender()

            msg_record['sender_str'] = sender
            msg_record['dest_str'] = ''
            msg_record['symbol_str'] = '~>'
            msg_record['label_str'] = 'signal ' + msg.get_member()

            if not self.entities.has_key(sender):
                self.add_new_entity()

            self.entities[sender]['nb_msg'] += 1


        elif (msg.get_type() == DBUS_MESSAGE_TYPE_ERROR):
            sender = msg.get_sender()
            dest = msg.get_destination()
            serial = msg.get_reply_serial()

            if not self.entities.has_key(sender):
                self.add_new_entity()
            if not self.entities.has_key(dest):
                self.add_new_entity()

            msg_record['sender_str'] = sender
            msg_record['dest_str'] = dest
            msg_record['symbol_str'] = '>>'
            msg_record['label_str'] = 'ERROR' + (" (s=%d)" % (serial))

            self.entities[sender]['nb_msg'] += 1
            self.entities[dest]['nb_msg'] += 1
            print "error msg 7"
            self.entities[dest]['serial'][serial] = {}
            print "error msg 8"
            self.entities[dest]['serial'][serial]['return_indice'] = indice
            print "error msg 9"

        else:
            print "Invalid message"
            msg_record['skip'] = 1

        self.messages.append(msg_record)
        print "added"

    def msg_cb(self, _bus, msg):
        self.print_msg(msg)

        # if this is a new entity, get the owner
        if msg.get_type() == DBUS_MESSAGE_TYPE_SIGNAL:
            if (msg.get_member() == "NameAcquired") \
                or (msg.get_member() == "NameOwnerChanged"):
                print "??????????? msg callback new entity ????"
                self.add_new_entity()
                print "????? end"

        # add message in the array
        self.add_msg(msg)

    def start_recording(self):
        if (self.recording):
            return
        self.bus.add_match_string("")
        self.bus.add_message_filter(self.msg_cb)
        self.add_new_entity()
        self.recording = 1

    def stop_recording(self):
        if (not self.recording):
            return
        self.bus.remove_message_filter(self.msg_cb)
        self.bus.remove_match_string("")
        self.recording = 0

    def __init__(self, options):
        self.options = options
        self.recording = 0
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.bus.request_name(DBUS_MESSAGES_BOX_DOMAIN)

if __name__ == "__main__":
    #skip_entities = set([])
    #skip_entities = set(["DBusMessagesBox", "DBus"])
    skip_entities = set(["DBusMessagesBox"])
    options = { 'skip_entities' : skip_entities, \
                'prefered_names' : ['gabble', 'salut', 'ChatFilter'] }

    box = DBusMessagesBox(options)
    box.start_recording()
    try:
        gtk.main()
    except:
        print

    box.stop_recording()

    print "parsing now"
    box.parse("/tmp/file.msc")
    os.system("mscgen -T png -i /tmp/file.msc -o /tmp/file.png")


