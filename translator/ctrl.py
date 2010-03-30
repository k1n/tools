import gtk
import urllib
import urllib2
from sgmllib import SGMLParser
from gtkmvc import Controller

class URLLister(SGMLParser):
    def __init__(self, result):
        SGMLParser.__init__(self)
        self.result = result
        self.open = False

    def start_textarea(self, attrs):
        id = [v for k, v in attrs if k=='id']
        print id
        if 'suggestion' in id:
            print 'ok, open now'
            self.open = True

    def start_br(self, attrs):
        if self.open:
            self.result.append('\n')

    def handle_data(self, text):
        if self.open:
            print text
            self.result.append(text.strip().replace('<br>', '\n'))

    def end_textarea(self):
        if self.open:
            self.open = False

class MyController(Controller):
    def __init__(self, model):
        Controller.__init__(self, model)

    def register_view(self, view):
        Controller.register_view(self, view)

        self.view['window'].connect('destroy', gtk.main_quit)
        
        self.init_cbox_model()
        self.init_tview_buffer()

    def translate(self, text, lin, lout):
        result = []
        values={'hl':'zh-CN','ie':'UTF-8','text':text,'langpair':"%s|%s" % (lin, lout)}
        url='http://translate.google.cn/translate_t'
        data = urllib.urlencode(values)

        req = urllib2.Request(url, data)
        req.add_header('User-Agent', "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)")

        response = urllib2.urlopen(req)
        parser = URLLister(result)
        response_data = response.read()
        parser.feed(response_data)

        return result

    def init_tview_buffer(self):
        self.model.in_buffer = self.view['tview_in'].get_buffer()
        self.model.out_buffer = self.view['tview_out'].get_buffer()

    def init_cbox_model(self):
        self.view['cbox_in'].set_model(self.model.in_model)
        self.view['cbox_in'].set_active(2)
        textcell = gtk.CellRendererText()
        self.view['cbox_in'].pack_start(textcell, True)
        self.view['cbox_in'].add_attribute(textcell, 'text', 1)

        self.view['cbox_out'].set_model(self.model.out_model)
        self.view['cbox_out'].set_active(7)
        textcell = gtk.CellRendererText()
        self.view['cbox_out'].pack_start(textcell, True)
        self.view['cbox_out'].add_attribute(textcell, 'text', 1)

    def on_switch_button_clicked(self, widget):
        out_active = self.view['cbox_out'].get_active()
        in_active = self.view['cbox_in'].get_active()

        self.view['cbox_out'].set_active(in_active)
        self.view['cbox_in'].set_active(out_active)

    def on_btn_translate_clicked(self, widget):
        in_buffer = self.model.in_buffer
        out_buffer = self.model.out_buffer

        text = in_buffer.get_text(in_buffer.get_start_iter(), in_buffer.get_end_iter())
        text = self.translate(text, *self.view.get_in_and_out())
        out_buffer.set_text(''.join(text))
