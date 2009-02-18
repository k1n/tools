import threading
import cPickle as pickle
from googlereader.reader import GoogleReader
from utils import offline_mode, offline_feed

class Reader(threading.Thread):
    _gr = GoogleReader()
    entry = None
    feed = None
    entries = []
    previous = None

    def __init__(self):
        super(Reader, self).__init__()

    @offline_mode(None)
    def run(self, login = None, passwd = None):
        print 'start parse feed'
        self._gr.identify(login, passwd)
        self._gr.login()
        self.feed = self.get_unread_feed()
        self.entries = self.get_entries()
        self.channels = self.get_channels()
        self.entry = self.entries[0]
        print 'finish parse feed'

    # Low API
    @offline_mode('data/unread_feed.obj')
    def get_unread_feed(self):
        feed = None
        while not feed:
            try:
                feed = self._gr.get_unread()
            except:
                pass

        return feed

    @offline_feed
    def get_feed(self, feed_id):
        feed = None
        while not feed:
            try:
                feed = self._gr.get_feed(feed = feed_id)
            except:
                pass

        return feed

    @offline_mode('data/sub_list.obj')
    def get_sub_list(self):
        return self._gr.get_subscription_list()['subscriptions']

    @offline_mode('data/unread_count.obj')
    def get_unread_count(self):
        return self._gr.get_unread_count()

    # High API
    def get_channels(self):
        channels = {}
        for channel in self.get_sub_list():
            channels[channel['id']] = {'title': channel['title']}

        unread_count = self.get_unread_count()
        for item in unread_count['unreadcounts']:
            id = item['id']
            if id.startswith('feed'):
                channels[id]['count'] = item['count']

        return channels

    def get_entries(self):
        return list(self.feed.get_entries())

    def get_entry(self):
        return self.entry

    def get_previous(self):
        return self.previous

    def add_star(self, entry):
        ok = False
        while not ok:
            try:
                self._gr.add_star(entry['google_id'])
            except:
                print 'add start'
            else:
                ok = True

    def set_read(self, entry = None):
        if entry is None:
            entry = self.entry
        ok = False
        while not ok:
            try:
                self._gr.set_read(entry['google_id'])
            except:
                pass
            else:
                ok = True

    def iter_next(self):
        self.previous = self.entry

        if len(self.entries) == 1:
            self.feed = self.get_unread_feed()
            self.entries = self.get_entries()

        self.entries.remove(self.entry)
        self.entry = self.entries[0]

reader = Reader()
import threading
import cPickle as pickle
from googlereader.reader import GoogleReader
from utils import offline_mode, offline_feed

class Reader(threading.Thread):
    _gr = GoogleReader()
    entry = None
    feed = None
    entries = []
    previous = None

    def __init__(self):
        super(Reader, self).__init__()

    @offline_mode(None)
    def run(self, login = None, passwd = None):
        print 'start parse feed'
        self._gr.identify(login, passwd)
        self._gr.login()
        self.feed = self.get_unread_feed()
        self.entries = self.get_entries()
        self.channels = self.get_channels()
        self.entry = self.entries[0]
        print 'finish parse feed'

    # Low API
    @offline_mode('data/unread_feed.obj')
    def get_unread_feed(self):
        feed = None
        while not feed:
            try:
                feed = self._gr.get_unread()
            except:
                pass

        return feed

    @offline_feed
    def get_feed(self, feed_id):
        feed = None
        while not feed:
            try:
                feed = self._gr.get_feed(feed = feed_id)
            except:
                pass

        return feed

    @offline_mode('data/sub_list.obj')
    def get_sub_list(self):
        return self._gr.get_subscription_list()['subscriptions']

    @offline_mode('data/unread_count.obj')
    def get_unread_count(self):
        return self._gr.get_unread_count()

    # High API
    def get_channels(self):
        channels = {}
        for channel in self.get_sub_list():
            channels[channel['id']] = {'title': channel['title']}

        unread_count = self.get_unread_count()
        for item in unread_count['unreadcounts']:
            id = item['id']
            if id.startswith('feed'):
                channels[id]['count'] = item['count']

        return channels

    def get_entries(self):
        return list(self.feed.get_entries())

    def get_entry(self):
        return self.entry

    def get_previous(self):
        return self.previous

    def add_star(self, entry):
        ok = False
        while not ok:
            try:
                self._gr.add_star(entry['google_id'])
            except:
                print 'add start'
            else:
                ok = True

    def set_read(self, entry = None):
        if entry is None:
            entry = self.entry
        ok = False
        while not ok:
            try:
                self._gr.set_read(entry['google_id'])
            except:
                pass
            else:
                ok = True

    def iter_next(self):
        self.previous = self.entry

        if len(self.entries) == 1:
            self.feed = self.get_unread_feed()
            self.entries = self.get_entries()

        self.entries.remove(self.entry)
        self.entry = self.entries[0]

reader = Reader()
