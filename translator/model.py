# coding: utf-8
import gtk
import gobject
from gtkmvc import Model

LANGUAS = {
    'auto':'检测语言',
    'de':'德语',
    'ru':'俄语',
    'fr':'法语',
    'ja':'日语',
    'en':'英语',
    'zh-TW':'正體中文',
    'zh-CN':'简体中文',
}

class MyModel(Model):
    __properties__ = {
        'in_lang': 'auto',
        'out_lang': 'zh-TW',
        'out_model': None,
        'in_model': None,
        'in_buffer': None,
        'out_buffer': None,
    }
    
    def __init__(self):
        Model.__init__(self)

        self.out_model = self.create_select_model()
        self.in_model = self.create_select_model()

    def create_select_model(self):
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)

        list = LANGUAS.items()
        list.sort()
        for k, v in list:
            iter = model.append()
            model.set(iter,
                    0, k,
                    1, v)

        return model
