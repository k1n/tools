#!/usr/bin/python

# Use the up and down cursor keys to cycle through news stories, and Q to quit

import clutter
import feedparser
import urllib
import time
black=clutter.Color(0,0,0,255)
blue=clutter.Color(50,50,255,255)
white=clutter.Color(255,255,255,255)


class simplefeed():
    def __init__(self):
        self.feed= feedparser.parse('http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/world/rss.xml')
        self.img, self.data =urllib.urlretrieve(self.feed.feed.image.href)
        self.stage=clutter.Stage()
        self.ident =clutter.texture_new_from_file(self.img)
        self.head=clutter.Text()
        self.body=clutter.Text()
        self.entry=0
        #initialize elements of the display group
        self.head.set_position(130, 5)
        self.head.set_color(blue)
        self.body=clutter.Text()
        self.body.set_max_length(70)
        self.body.set_position(130, 22)
        self.body.set_size(250, 100)
        self.body.set_line_wrap(True)
        
        #get first feeed entry for text elements
        self.setfeed()
        #create group to hold elements
        self.group= clutter.Group()
        self.group.add(self.ident, self.head, self.body)
        self.group.show_all()
        #set up stage
        self.stage.set_size(400,60)
        self.stage.set_color(white)
        self.stage.show_all()
        self.stage.add(self.group)
        self.stage.connect('key-press-event', self.parseKeyPress)
        clutter.main()


    def setfeed(self):
        self.head.set_text(self.feed.entries[self.entry].title)
        self.body.set_text(self.feed.entries[self.entry].summary)
        
    def flipfeed(self):
        #animate display out of sight
        x=self.group.animate(clutter.EASE_OUT_EXPO,1200,'x',800,'y',0,'rotation-angle-y',180)
        #we need to wait in order for this to happen, so we connect the completed feed to the second half of the animation
        #which resets the graphic and sets the new text
        x.connect('completed', self.flip2)

    def flip2(self, event):
        self.group.animate(clutter.EASE_OUT_EXPO,100,'x',0,'y',0,'rotation-angle-y',0)
        self.setfeed()
        
    def parseKeyPress(self, stage, event):
        #do stuff when the user presses a key
        if event.keyval == clutter.keysyms.q:
            #if the user pressed "q" quit the app
            clutter.main_quit()
        elif event.keyval == clutter.keysyms.Down:
            #if the user pressed Down arrow - get an older entry
            self.entry+=1
            if (self.entry > len(self.feed.entries)):
                self.entry-=1
            else:
                self.flipfeed()
        elif event.keyval == clutter.keysyms.Up:
            #if the user pressed Up arrow - get a more recent entry
            self.entry -=1
            if (self.entry < 0):
                self.entry =0
            else:
                self.flipfeed()

if __name__=="__main__":
    test = simplefeed()
   

