import nautilus
import logging
logging.basicConfig(level = logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/tmp/markeblems.log',
                    filemode='w')

class InfoProvider(nautilus.InfoProvider):
    def __init__(self):
        pass

    def update_file_info(self, file, emblem):
        file.add_emblem(emblem)
        logging.debug("Added %s to %s success" % (emblem, file.get_name()))

provider = InfoProvider()

class MarkEmblemsProvider(nautilus.MenuProvider):
    def __init__(self):
        pass

    def on_favourite_activate(self, widget, files):
        for file in files:
            logging.debug(file.get_string_attribute('emblems'))
            provider.update_file_info(file, 'favorite')

    def get_file_items(self, window, files):
        submenu = nautilus.Menu()

        item = nautilus.MenuItem('MarkEmblemsProvider::Favourite', 'Favourite', '')
        item.connect('activate', self.on_favourite_activate, files)
        submenu.append_item(item)

        item = nautilus.MenuItem('MarkEmblemsProvider::Update', 'Update', '')
        submenu.append_item(item)

        item = nautilus.MenuItem('MarkEmblemsProvider::Web', 'Web', '')
        submenu.append_item(item)

        menuitem = nautilus.MenuItem('MarkEmblemsProvider::Foo', 'Mark', '')
        menuitem.set_submenu(submenu)

        return menuitem,

    def get_background_items(self, window, file):
        submenu = nautilus.Menu()
        submenu.append_item(nautilus.MenuItem('MarkEmblemsProvider::Bar', 'Bar', ''))

        menuitem = nautilus.MenuItem('MarkEmblemsProvider::Foo', 'Foo', '')
        menuitem.set_submenu(submenu)

        return menuitem,
