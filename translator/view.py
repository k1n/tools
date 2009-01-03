from gtkmvc.view import View

class MyView(View):
    def __init__(self, ctrl):
        View.__init__(self, ctrl, 'basic.glade')

    def get_in_and_out(self):
        return self['cbox_in'].get_active_text(), self['cbox_out'].get_active_text()
