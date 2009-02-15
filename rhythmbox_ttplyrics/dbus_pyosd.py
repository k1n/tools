#!/bin/env python
# -*- coding: utf8 -*-
# 2008-12-27 22:16:45

import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop

import os
import sys
import re
import time
import posd# python-osd

class LyricsOSD :
    def __init__(self):
        self.__RE_TIME=r"^\[[0-9][0-9][:.][0-5][0-9][:.][0-9][0-9]\]"
        self.__RE_OFFSET=r"^\[OFFSET *[+-][0-9]*\]"
        self.__lines = None
        self.__pos = 0
        self.__btime = time.time() # begin time
        self.__OFFSET = 0

        self.__OSD=None
        self.__initOSD()

    def __initOSD(self):
        import imp, ConfigParser

        self.__OSD = posd.PangoOsd()

    def Reset(self):
        print "CALL Reset"
        self.__OSD.hide()
        self.__lines = None
        self.__pos = 0
        self.__btime = time.time()
        self.__OFFSET = 0

    def __countTime(self,stime):
        try:
            sec = "%d.%d" % (int(stime[0:2])*60+int(stime[3:5]),int(stime[6:8]))
        except:
            sec = "0.0"
        return eval(sec)

    def __filterSong(self,song):
        if song == None : return "~~ ~~ ~~"

        song = song.replace("\n","").replace("\r","")

        if len(song) == 0 : song = "~~ ~~ ~~"

        return song

    def __GetLyrics(self,filename):
        self.__lines = None
        if filename == None : return
        if not os.path.exists(filename) : return

        lines=None
        try:
            f = open(filename,'r')
            lines = f.readlines()
            f.close()
        except IOError,message:
            print >> sys.stderr, message

        if lines == None : return

        self.__lines = []
        for line in lines:
            if line == "" : continue
            if line[0] != '[': continue
            ti=[]
            while re.search(self.__RE_TIME,line):
                ti.append(line[0:10])
                line = line[10:]
            if len(ti) == 0 :
                self.__lines.append("[00:00.00]"+line)
            else:
                for t in ti:
                    self.__lines.append(t+line)

        if len(self.__lines) == 0 :
            self.__lines == None
            return

        self.__lines.sort()

    def __getHead(self,lines):
        song=''
        stime=''
        for line in lines :
            if line[1:9] == "00:00.00" :
                song = song + " " + line[10:]
                self.__pos=self.__pos+1
            else:
                stime = line[1:9]
                break
        song = song.replace('[','').replace(']','')
        song = song.replace('ti:','').replace('ar:','')
        song = song.replace('al:','').replace('by:','')
        return [stime,song]

    def __getSong(self,lines,idx):
        line = lines[idx]
        stime= line[1:9]
        song = line[10:]
        return [stime,song]

    def LyricsShow(self,filename=None,elapsed=0):
        offset = elapsed - self.__OFFSET
        if offset < 0 : offset = 0

        if self.__lines == None :
            self.__GetLyrics(filename)
        if self.__lines == None : return
        if len(self.__lines) == 0 : return

        if elapsed > 0 and abs(self.__btime + offset - time.time()) > 0.2 :
            self.__btime = time.time() - offset

            self.__pos = 1
            n=-1
            while n < 0 and self.__pos < len(self.__lines) :
                stime,song = self.__getSong(self.__lines,self.__pos)
                if re.search(self.__RE_OFFSET,song):
                    self.__OFFSET = eval(song.replace(']','')[8:])
                ntime = self.__countTime(stime)
                n = self.__btime + ntime - time.time()
                self.__pos = self.__pos + 1
            self.__pos = self.__pos - 2
            if self.__pos < 0 : self.__pos = 0
            print "%2d/%d SEED" % ( self.__pos, len(self.__lines) )

        if self.__pos >= len(self.__lines) : return

        if self.__pos == 0 :
            stime,song = self.__getHead(self.__lines)
        else:
            stime,song = self.__getSong(self.__lines,self.__pos)

        ntime=self.__countTime(stime)
        n = self.__btime + ntime - time.time()
        if n > 0 : return

        song = self.__filterSong(song)

        if re.search(self.__RE_OFFSET,song):
            self.__OFFSET = eval(song.replace(']','')[8:])

        self.__OSD.display(song)
        i = self.__OSD.get_number_lines()
        while i > 1 :
            i = i - 1
            song = self.__getSong(self.__lines,self.__pos + i)[1]
            song = self.__filterSong(song)
            self.__OSD.display(song,line=i)

        self.__pos = self.__pos + 1

        print "%2d/%d %s %6.2f/%2.2f %6.2f %.2f %s" % ( self.__pos, len(self.__lines), stime, elapsed, offset, ntime, time.time(), song )


class LyricsDBus :
    def __init__(self):
        print "CALL __init__"
        self.__handlers = []
        self.__player = None
        self.__shell = None

        self.__OSD = None
        self.elapsed = -1
        self.__lyfilename = None

    def __set_uri(self,uri):
        print "CALL __set_uri (%s)" % uri
        if uri is not None and uri != "" :
            self.__uri = uri
            self.__shell.getSongProperties(uri,
                    reply_handler=self.__set_song_properties,
                    error_handler=self._report_dbus_error)
        else:
            self._set_no_song()

    def __set_song_properties(self,prop):
        print "CALL __set_song_properties"
        self.title = prop.get("title")
        self.artist = prop.get("artist")
        self.__lyfilename = "%s/.lyrics/%s/%s.lyric" % (os.getenv("HOME"),self.artist,self.title)
        self.__OSD.Reset()

    def __set_playing(self,playing):
        print "CALL __set_playing (%s)" % playing
        self.playing = playing
        self.__OSD.Reset()

        if not self.playing and self.elapsed < 0 :
            self._set_no_song()

    def __set_elapsed(self, elapsed):
        #print "CALL __set_elapsed (%s) " % elapsed
        self.elapsed = elapsed

        self.__OSD.LyricsShow(self.__lyfilename,self.elapsed)

        if not self.playing and self.elapsed < 0 :
            self._set_no_song()

    def __property_changed(self,uri,prop,old_val,new_val):
        print "CALL __property_changed (%s|%s|%s|%s)" % ( uri,prop,old_val,new_val)
        if prop == "title":
            self.title = new_val
        elif prop == "artist":
            self.artist = new_val
        self.__lyfilename = "%s/.lyrics/%s/%s.lyric" % (os.getenv("HOME"),self.artist,self.title)
        self.__OSD.Reset()

    def connect (self):
        print "CALL connect"
        if self.__player is not None:
            return

        bus = dbus.SessionBus ()

        proxy = bus.get_object ("org.gnome.Rhythmbox", "/org/gnome/Rhythmbox/Player")
        self.__player = dbus.Interface (proxy, "org.gnome.Rhythmbox.Player")

        proxy = bus.get_object ("org.gnome.Rhythmbox", "/org/gnome/Rhythmbox/Shell")
        self.__shell = dbus.Interface (proxy, "org.gnome.Rhythmbox.Shell")

        self.__handlers = [
                self.__player.connect_to_signal ("playingChanged", self.__set_playing),
                self.__player.connect_to_signal ("elapsedChanged", self.__set_elapsed),
                self.__player.connect_to_signal ("playingUriChanged", self.__set_uri),
                self.__player.connect_to_signal ("playingSongPropertyChanged", self.__property_changed),
                ]

        self.__player.getPlaying (reply_handler=self.__set_playing,
                error_handler=self._report_dbus_error)

        self.__player.getElapsed (reply_handler=self.__set_elapsed,
                error_handler=self._report_dbus_error)

        self.__player.getPlayingUri (reply_handler=self.__set_uri,
                error_handler=self._report_dbus_error)

        self.__OSD = LyricsOSD()

        self.connected = True

    def disconnect(self):
        print "CALL disconnect"
        for handler in self.__handlers:
            handler.remove()
        self.__handlers = []
        self.__player = None
        self.__shell = None
        self.__ODS = None

    def _set_no_song(self):
        print "CALL _set_no_song"
        self.__OSD.Reset()

    def _report_dbus_error(self,err):
        print "CALL _report_dbus_error"

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    dbus_loop = gobject.MainLoop()

    lybus = LyricsDBus()
    lybus.connect()

    dbus_loop.run()
