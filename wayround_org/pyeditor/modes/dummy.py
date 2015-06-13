

from gi.repository import Gtk

SUPPORTED_MIME = []
SUPPORTED_FNM = []

class View:

    def __init__(self, mode_interface):

        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window

        self.view = Gtk.Label("Dummy")

        self._main = self.view

        return

    def get_view_widget_sw(self):
        return None

    def get_view_widget(self):
        return self._main

    def get_widget(self):
        return self._main

    def destroy(self):
        self.get_widget().destroy()


class SourceMenu:

    def __init__(self, mode_interface):

        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window

        source_me = Gtk.Menu()

        source_dummy_mi = Gtk.MenuItem.new_with_label(
            "Dummy"
            )
        source_dummy_mi.set_sensitive(False)

        source_me.append(source_dummy_mi)

        self._source_me = source_me

        return

    def get_widget(self):
        return self._source_me

    def destroy(self):
        self.get_widget().destroy()
        return


class ModeInterface:

    def __init__(self, main_window):
        self.main_window = main_window
        self.source_menu = SourceMenu(self)
        self.view = View(self)
        return

    def destroy(self):
        self.source_menu.destroy()
        self.view.destroy()
        return

    def get_menu(self):
        return self.source_menu.get_widget()

    def get_menu_name(self):
        return "Dummy"

    def get_widget(self):
        return self.get_view_widget()

    def get_view_widget(self):
        return self.view.get_widget()

    def get_view_widget_sw(self):
        return None

    def set_buffer(self, buff):
        return
