#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os
import re
import urllib2
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1


class wget:
    def __init__(self):
        self.__OPENER = None

    def __initOpener(self):
        proxy = os.getenv("http_proxy")

        if proxy :
            http_proxy = urllib2.ProxyHandler({"http":proxy})
            opener = urllib2.build_opener(http_proxy)
        else:
            opener = urllib2.build_opener()

        self.__OPENER = opener

    def geturl(self,url):
        if self.__OPENER is None :
            self.__initOpener()

        urlfile = self.__OPENER.open(url)
        return urlfile

class MObj :
    def __init__(self):
        self.path     = None
        self.filename = None
        self.fullname = None

        self.lyname     = None
        self.lyfullname = None

        self.artic = None
        self.title = None

    def debug_print(self):
        print "debug_print==============================BEGIN"
        print "FILE"
        print " [%s]" % self.fullname
        print " [%s]" % self.path
        print " [%s]" % self.filename
        print "LYRIC"
        print " [%s]" % self.lyfullname
        print " [%s]" % self.lyname
        print "ID3"
        print " [%s]" % self.artic
        print " [%s]" % self.title
        print "debug_print==============================END"

class MusicManager :
    def __init__(self,mpath,lpath):
        self.__MusicPath = mpath
        self.__LyricPath = lpath
        self.__RE_MP3="(?i)\.mp3$"
        self.__RE_LYRIC="\.lyric$"

    def setMusicPath(self,mpath):
        self.__MusicPath = mpath

    def getMusicPath(self):
        return self.__MusicPath

    def setLyricPath(self,mpath):
        self.__LyricPath = mpath

    def getLyricPath(self):
        return self.__LyricPath

    def __getMusicObj(self,fullname):
        UNKNOW="UNKNOWN"
        m=MObj()
        m.fullname = fullname
        m.path = os.path.dirname(fullname)
        m.filename = os.path.basename(fullname)
        try:
            id3info = ID3(fullname)
            tit2 = id3info.getall('TIT2')
            tpe1 = id3info.getall('TPE1')
            if tit2 == None or len(tit2) == 0 or len(str(tit2[0])) == 0 :
                m.title = None
            else:
                m.title = str(tit2[0])
            if len(tpe1) == 0 or len(str(tpe1[0])) == 0 :
                m.artic = None
            else:
                m.artic = str(tpe1[0])
            if m.artic and m.title :
                m.lyname = "%s.%s" % ( m.title,"lyric" )
                m.lyfullname = "%s/%s/%s" % (self.__LyricPath,m.artic,m.lyname)
        except Exception,e:
            print e

        return m

    def __searchLyric(self,artic=None,title=None,check=True):
        """ get lyric from mp3.sogou.com """
        w = wget()
        URL = "http://mp3.sogou.com/gecisearch.so?query=%s-%s" % ( artic,title )
        URL = unicode(URL,"UTF8").encode("GB18030")
        f = w.geturl(URL)
        for html in f.readlines():
            if html.find("downlrc.jsp") < 0 : continue
            #if html.find("LRC") < 1 : continue
            link = html[html.find("downlrc.jsp"):html.find("LRC")-2]
            link = "http://mp3.sogou.com/" + link
            lines = w.geturl(link).readlines()
            if check == False :
                return lines
            art=tit=None
            for n in lines :
                n = unicode(n,"GB18030").encode("UTF8")
                if re.search("^\[ar:",n): 
                    art = n[n.find("[ar:"):]
                    art = art[4:art.find("]")]
                if re.search("^\[ti:",n):
                    tit = n[n.find("[ti:"):]
                    tit = tit[4:tit.find("]")]
                if art != None and tit != None : break
            if title == tit :
                return lines
            if title and tit and str(title).upper() == tit.upper() :
                return lines
            return []
        return []

    def __getMusicList(self):
        LIST = []
        for root,dirs,files in os.walk(self.__MusicPath):
            for f in files:
                if not re.search(self.__RE_MP3,f): continue
                fullname = "%s/%s" % (root,f)
                LIST.append(fullname)
        return LIST

    def __getMusicObjList(self):
        LIST = []
        for root,dirs,files in os.walk(self.__MusicPath):
            for f in files:
                if not re.search(self.__RE_MP3,f): continue
                fullname = "%s/%s" % (root,f)
                obj = self.__getMusicObj(fullname)
                if obj != None :
                    LIST.append(obj)
        return LIST

    def __getLyricList(self):
        LIST = []
        for root,dirs,files in os.walk(self.__LyricPath):
            for f in files:
                if not re.search(self.__RE_LYRIC,f): continue
                fullname = "%s/%s" % (root,f)
                LIST.append(fullname)
        return LIST

    def lyricUpdate(self,filename) :
        if not os.path.isfile(filename) :
            print "file not found [%s]" % filename
            return False
        m = self.__getMusicObj(filename)
        result = self.__searchLyric(m.artic,m.title,False)
        #print len(result), m.lyfullname
        if len(result) > 0 :
            path = os.path.dirname(m.lyfullname)
            if not os.path.exists(path):
                os.mkdir(path)
            f=open(m.lyfullname,"w+")
            for n in result :
                f.write(unicode(n,"GB18030").encode("UTF8"))
            f.close()

    def LyricUpdate(self):
        for m in self.__getMusicObjList() :
            if m.lyfullname is None : continue
            if os.path.isfile(m.lyfullname): continue
            result = self.__searchLyric(m.artic,m.title)
            print len(result), m.fullname,"[%s/%s]"%(m.artic,m.title)
            if len(result) > 0 :
                path = os.path.dirname(m.lyfullname)
                if not os.path.exists(path):
                    os.mkdir(path)
                f=open(m.lyfullname,"w+")
                for n in result :
                    f.write(unicode(n,"GB18030").encode("UTF8"))
                f.close()

    def LyricClean(self,auto=False):
        mlist = [m.lyfullname for m in mm.__getMusicObjList()]
        llist = mm.__getLyricList()
        
        for l in llist :
            if l in mlist : continue
            if auto == True:
                os.unlink(l)
                print "delete",
            print l

    def __saveLyric(self,lines,art,tit,conv=True):
        s = "".join(lines)
        if conv :
            s = unicode(s,"GB18030").encode("UTF8")
        lypath = "%s/%s" % ( self.__LyricPath,art )
        if not os.path.exists(lypath):
            os.mkdir(lypath)
        lyfullname = "%s/%s.lyric" % (lypath,tit)
        f = open(lyfullname,"w+")
        f.write(s)
        f.close()

    def __music_fix(self,file):
        m = self.__getMusicObj(file)
        print m.artic,m.title,m.lyfullname
        if m.artic and m.title and m.lyname and os.path.exists(m.lyfullname) :
                print "ok",m.fullname
                return

        str = m.filename[:-4]
        if m.artic != None :
            str = "%s/%s" % ( str,m.artic )
        if m.title : str = "%s/%s" % ( str,m.title )
        lines = self.__searchLyric(artic="",title=str,check=False)
        print "search [%s] get [%d] lines" % ( str,len(lines) )

        art=tit=None
        for n in lines :
            n = unicode(n,"GB18030").encode("UTF8")
            if re.search("\[ti:.*\]",n):
                tit = n[n.find("[ti:"):]
                tit = tit[4:tit.find("]")]
            if re.search("\[ar:.*\]",n):
                art = n[n.find("[ar:"):]
                art = art[4:art.find("]")]
            if art != None and tit != None : break
        print "[%s/%s]" % (art, tit)
        self.__saveLyric(lines,art,tit,True)

        if m.artic is None and m.title is None :
            id3obj = ID3()
        else:
            id3obj = ID3(file)

        if m.artic == None and art != None :
            id3obj.add( TPE1(encoding=3, text=art.decode("UTF8")) )
        if m.title == None and tit != None :
            if m.filename.find(tit) < 0 :
                tit = m.filename[:-4]
            id3obj.add( TIT2(encoding=3, text=tit.decode("UTF8")) )
        id3obj.save(file)

    def MusicFix(self,file=None):
        if file is not None :
            self.__music_fix(file)
        else:
            LIST = self.__getMusicList()
            for f in LIST :
                self.__music_fix(f)

HELP="""
    lyrics update [ file.mp3 ]
    lyrics clean [delete]
    lyrics fix [ music_path lyric_path ]
    ------------------
    lyrics
        [-m|--music-path music_path]
        [-l|--lyric-path lyric_path]
        [-c|--clean [-y] ]
        [-u|--updae]
"""

if __name__ == "__main__":

    argc = len(sys.argv)

    if argc < 2 :
        print HELP
        exit(0)

    MusicPath="/domain/MyMusic"
    LyricPath=os.path.expanduser('~')

    mm = MusicManager(MusicPath,LyricPath)

    if argc == 4:
        mm.setMusicPath(sys.argv[2])
        mm.setLyricPath(sys.argv[3])

    print "MusicPath=[%s]" % mm.getMusicPath()
    print "LyricPath=[%s]" % mm.getLyricPath()

    if sys.argv[1] == "update":
        if argc == 3 :
            filename = sys.argv[2]
            filename = os.path.abspath(filename)
            mm.lyricUpdate(filename)
        else:
            mm.LyricUpdate()
        print "-- END --"

    elif sys.argv[1] == "clean":
        flag=False
        if argc == 3 and sys.argv[2] == 'delete' :
            flag=True
        mm.LyricClean(auto=flag)
        print "-- END --"

    elif sys.argv[1] == "fix":
            #mm.MusicFix("/home/biff/yinyue/英雄泪-王杰.mp3")
            mm.MusicFix("/home/biff/yinyue/其实你不懂我的心.mp3")
            #mm.MusicFix()


