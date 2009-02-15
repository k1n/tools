# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*-
#
# Copyright 2007 Sevenever
# Copyright(C) 2007 Sevenever
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or(at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

import sys
import os
import gtk
import gobject
import re
from xml.dom import minidom
import rb
import rhythmdb
from ttpClient import ttpClient
import random
import locale

ui_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="ViewMenu" action="View">
      <menuitem name="ttplyrics" action="TTPLyrics"/>
    </menu>
  </menubar>
</ui>
"""

LYRICS_FOLDER="~/.lyrics"
LYRIC_TITLE_STRIP=["\(live[^\)]*\)", "\(acoustic[^\)]*\)",
                    "\([^\)]*mix\)", "\([^\)]*version\)",
                    "\([^\)]*edit\)", "\(feat[^\)]*\)"]
LYRIC_TITLE_REPLACE=[("/", "-"),(" & ", " and ")]
LYRIC_ARTIST_REPLACE=[("/", "-"),(" & ", " and ")]

MAX_RETRY = 5

class TTPLyricsWindow(gtk.Window):
    '''
    the main lyrics window
    '''
    
    def __init__(self, parent):
	'''
	initialize the window, create widgets and child window
	'''
	
        gtk.Window.__init__(self)
        self.lyrics_grabber = TTPLyricGrabber()
	
        #Create a lyrics search result window
        self.schRsltDlg = TTPSearchResultWindow(self)  
        
        self.create_UI(parent)
                    
        self.show_all()

    def create_UI(self, parent):
	'''
	create all UI widgets
	'''
        self.set_border_width(12)
        self.set_transient_for(parent)
        self.set_title(_('ttplyrics by sevenever'))

        #create widget
        view = gtk.TextView()
        view.set_wrap_mode(gtk.WRAP_WORD)
        view.set_editable(False)
        self.buffer = view.get_buffer()

        sw = gtk.ScrolledWindow()
        sw.add(view)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type(gtk.SHADOW_IN)

        lblArtist = gtk.Label(_('Artist'))
        self.txtArtist = gtk.Entry()
        self.txtArtist.set_width_chars(30)
        lblTitle = gtk.Label(_('Title'))
        self.txtTitle = gtk.Entry()
        self.txtTitle.set_width_chars(30)

        btnSearch = gtk.Button(label=_('Search'),
                                stock=gtk.STOCK_FIND_AND_REPLACE)
        btnSearch.connect('clicked', self.search_lyrics, self.schRsltDlg)

        btnClose = gtk.Button(stock=gtk.STOCK_CLOSE)
        btnClose.connect('clicked', lambda w: self.destroy())

        #packing all
        vbox = gtk.VBox(spacing=12)
        vbox.pack_start(sw, expand=True)
        
        bbox = gtk.HBox()

        #bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.pack_start(lblArtist, expand=False)
        bbox.pack_start(self.txtArtist, expand=False)
        bbox.pack_end(btnSearch, expand=False)
        vbox.pack_start(bbox, expand=False)
        
        bbox1 = gtk.HBox()
        #bbox.set_layout(gtk.BUTTONBOX_END)
        bbox1.pack_start(lblTitle, expand=False)
        bbox1.pack_start(self.txtTitle, expand=False)
        bbox1.pack_end(btnClose, expand=False)
        vbox.pack_start(bbox1, expand=False)
        
        self.add(vbox)
        self.set_focus_chain([view, self.txtArtist,
                                self.txtTitle, btnSearch, btnClose])
        self.set_default_size(400, 600)

        return 

    def search_lyrics(self, widget, rsltDlg):
	'''
	callback for search button click event.
	if rsltDlg is not None, it show the search result list in this dialog
	else it show the first result in the lyrics window.
	'''
	
        artist = self.txtArtist.get_text()
        title = self.txtTitle.get_text()
        self.set_title(title + " - " + artist + " - ttplyrics")

        self.grab_lyrics_by_ar_ti(artist, title, rsltDlg)
    
    def show_lyrics(self, entry, shell):
	'''
	show lyrics in lyrics window for entry.
	'''
	
        db = shell.props.db
        title = db.entry_get(entry, rhythmdb.PROP_TITLE)
        artist = db.entry_get(entry, rhythmdb.PROP_ARTIST)
        self.txtArtist.set_text(artist)
        self.txtTitle.set_text(title)

        self.search_lyrics(None, None)
        
    def grab_lyrics_by_ar_ti(self, artist, title, rsltDlg):
	'''
	Search lyrics by artist and title.
	if rsltDlg is not None, it show the search result list in this dialog
	else it show the first result in the lyrics window.
	'''
        self.buffer.set_text(_("Searching for lyrics..."))
        self.lyrics_grabber.get_lyrics(artist, title, self.buffer.set_text, rsltDlg)
        

class TTPSearchResultWindow(object):
    '''
    Display the lyrics search result list.
    Allow user to select one search result item.
    '''
    
    def __init__(self, parent):
	'''
        Create a new window
	'''
	
        self.dlg = gtk.Dialog(None,
                                parent, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OK, gtk.RESPONSE_OK))
                                
        self.dlg.set_transient_for(parent)
        self.dlg.set_title(_('search result-ttplyrics'))

	#create ListStore for store result list
        self.list = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)

        #TreeView for display
        self.view = gtk.TreeView(self.list)

        self.col = gtk.TreeViewColumn('select a lyrics')

        self.view.append_column(self.col)
        
        self.cell1 = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()
        
        self.col.pack_start(self.cell1, True)
        self.col.pack_start(self.cell2, True)
        
        self.col.add_attribute(self.cell1, 'text', 1)
        self.col.add_attribute(self.cell2, 'text', 2)

        self.view.get_selection().set_mode(gtk.SELECTION_SINGLE)

        #when double-click a item
        self.view.connect('row-activated', self.double_clicked)
        self.dlg.vbox.pack_start(self.view)
	
        self.dlg.set_default_size(200, 250)        
    def set_lyricsList(self, lrcli):
	'''
	update the search result list.
	'''
	
        self.list.clear()
        for item in lrcli:
            self.list.append([item[0], item[1], item[2]])
    
    def run(self):
	'''
	run the dialog, let user select one item.
	return a tuple contain Id, artist, title
	'''
	
        self.dlg.show_all()
        if gtk.RESPONSE_OK == self.dlg.run():
            (model, iter) = self.view.get_selection().get_selected()
            if iter:
                result = model.get(iter, 0, 1, 2)
            else:
                result = None
        else:
            result = None
        self.dlg.hide_all()
        
        return result
    
    def double_clicked(self, view, path, view_column):
	'''
	close dialog and response RESPONSE_OK
	'''
	
        self.view.get_selection().unselect_all()
        self.view.get_selection().select_path(path)
        self.dlg.response(gtk.RESPONSE_OK)

class TTPLyricGrabber(object):
    '''
    '''
    
    def __init__(self):
        self.loader = rb.Loader()

    def _build_cache_path(self, artist, title):
        lyrics_folder = os.path.expanduser(LYRICS_FOLDER)
        if not os.path.exists(lyrics_folder):
            os.mkdir(lyrics_folder)
        try:
            artist_folder = lyrics_folder + '/' + artist[:128].encode(locale.getdefaultlocale()[1])
        except UnicodeEncodeError:
            artist_folder = lyrics_folder + '/' + artist[:128]
            
        if not os.path.exists(artist_folder):
            os.mkdir(artist_folder)

        try:
            title_filename = title[:128].encode(locale.getdefaultlocale()[1]) + '.lyric'
        except UnicodeEncodeError:
            title_filename = title[:128] + '.lyric'

        return artist_folder + '/' + title_filename

    def get_lyrics(self, artist, title, callback, listDlg=None):
        self.callback = callback

        # replace ampersands and the like
        for exp in LYRIC_ARTIST_REPLACE:
                p = re.compile(exp[0])
                artist = p.sub(exp[1], artist)
        for exp in LYRIC_TITLE_REPLACE:
                p = re.compile(exp[0])
                title = p.sub(exp[1], title)

        # strip things like "(live at Somewhere)", "(accoustic)", etc
        for exp in LYRIC_TITLE_STRIP:
            p = re.compile(exp)
            title = p.sub('', title)

        # compress spaces
        title = title.strip().replace(u'`','').replace(u'/','')
        artist = artist.strip().replace(u'`','').replace(u'/','')

        self.cache_path = self._build_cache_path(artist, title)

        if not listDlg:
            if os.path.exists(self.cache_path):
                self.loader.get_url(self.cache_path, callback)
                return

        callback('Get Lyrics list on TTplayer lyrics server...')
        self.theurl = 'http://lrcct2.ttplayer.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0' %(ttpClient.EncodeArtTit(artist.replace(u' ','').lower()), ttpClient.EncodeArtTit(title.replace(u' ','').lower()))
        self.retry = 1
	self.callback('The' + str(self.retry) + 'th try...')
	self.loader.get_url(self.theurl, self.search_results, listDlg)
	            
    def search_results(self, data, listDlg=None):
        if data is not None:
            if self.retry < MAX_RETRY:
                self.retry += 1
                self.callback('The' + str(self.retry) + 'th try...')
                self.loader.get_url(self.theurl, self.search_results, listDlg)
                return
        else:
            self.callback("Server did not respond.")
            return

        try:
            dom1=minidom.parseString(data)
            resultli = dom1.getElementsByTagName('lrc')
            li = []
            for node in resultli:
                li.append((node.getAttribute('id'),node.getAttribute('artist'),node.getAttribute('title')))
        except:
            self.callback("Couldn't parse search results.")
            return
        
        if len(li)==0:
            self.callback('No lyrics found')
            return
        if listDlg:
            listDlg.set_lyricsList(li)
            result = listDlg.run()
            if result:
                Id,artist,title = result
            else:
                self.callback('')
                return
        else:
            Id,artist,title = li[0]

        self.theurl = 'http://lrcct2.ttplayer.com/dll/lyricsvr.dll?dl?Id=%d&Code=%d&uid=01&mac=%012x' %(int(Id),ttpClient.CodeFunc(int(Id),(artist + title).encode('UTF8')), random.randint(0,0xFFFFFFFFFFFF))
        self.retry = 1
	self.callback('The ' + str(self.retry) + 'th try...')
	self.loader.get_url(self.theurl, self.lyrics)

    def lyrics(self, data):
        if data is None:
	    if self.retry < MAX_RETRY:
		self.retry += 1
		self.callback('The ' + str(self.retry) + 'th try...')
		self.loader.get_url(self.theurl, self.lyrics)
		return
	    else:
		self.callback("Error occored while fetch lyrics content")
		return
	
        text = data
        text += "\n\n"+_("Lyrics provided by www.ttplayer.com")
        text += "\n\n"+_("ttplyrics plugin by sevenever")

        self.callback(text)
	
        f = file(self.cache_path, 'w')
        f.write(text)
        f.close()

	return


class TTPLyricsDisplayPlugin(rb.Plugin):

    def __init__(self):
        rb.Plugin.__init__(self)
        self.window = None

    def activate(self, shell):
        self.autoreload()
        self.action = gtk.Action('TTPLyrics', _('_TTPLyrics'),
                                  _('View lyrics from ttplayer <http://www.ttplayer.com>'),
                                  'rb-song-lyrics')
        self.activate_id = self.action.connect('activate', self.show_lyrics_window, shell)

        self.action_group = gtk.ActionGroup('TTPLyricsPluginActions')
        self.action_group.add_action(self.action)

        uim = shell.get_ui_manager()
        uim.insert_action_group(self.action_group, 0)
        self.ui_id = uim.add_ui_from_string(ui_str)
        uim.ensure_update()

        sp = shell.get_player()
        self.pec_id = sp.connect('playing-song-changed', self.playing_entry_changed, shell)
        self.playing_entry_changed(sp, sp.get_playing_entry(), shell)
        import dbus_pyosd
        from dbus.mainloop.glib import DBusGMainLoop
        DBusGMainLoop(set_as_default=True)
        dbus_loop = gobject.MainLoop()
        lybus = dbus_pyosd.LyricsDBus()
        lybus.connect()
        #dbus_loop.run()


    def deactivate(self, shell):

        uim = shell.get_ui_manager()
        uim.remove_ui(self.ui_id)
        uim.remove_action_group(self.action_group)

        self.action_group = None
        self.action = None

        sp = shell.get_player()
        sp.disconnect(self.pec_id)
        
        if self.window is not None:
            self.window.destroy()
            self.window = None
        
    def playing_entry_changed(self, sp, entry, shell):
        if entry is not None:
            self.show_song_lyrics(None, shell)

    def show_lyrics_window(self, action, shell):
        if self.window is not None:
            self.window.destroy()
        self.window = TTPLyricsWindow(shell.props.window)
        self.window.show_all()
        sp = shell.get_player()
        entry = sp.get_playing_entry()
        self.playing_entry_changed(sp, entry, shell)
    
    def show_song_lyrics(self, action, shell):
        sp = shell.get_player()
        entry = sp.get_playing_entry()

        if entry is None:
            return
        
        if self.window is None:
            return

        self.window.show_lyrics(entry, shell)
        
    def autoreload(self):
        mod_name = 'ttplyrics'
        module = sys.modules[mod_name]
        filename = module.__file__[ : module.__file__.rindex('.') ] + '.py'
        mtime = os.path.getmtime( filename )
        if 'loadtime' not in module.__dict__ or  mtime > module.loadtime:
            reload( module )
            module.loadtime = mtime

