#!/usr/bin/python

import gtk
from gui import worker

def main():
    window = worker.get_widget('main_window')
    window.show_all()

    gtk.main()

if __name__ == '__main__':
    main()
