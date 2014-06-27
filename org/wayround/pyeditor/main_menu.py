
from gi.repository import Gtk


class MainMenu:

    def __init__(self, main_window):

        self.main_window = main_window

        mb = Gtk.MenuBar()

        file_mi = Gtk.MenuItem.new_with_label("File")
        edit_mi = Gtk.MenuItem.new_with_label("Edit")
        source_mi = Gtk.MenuItem.new_with_label("Source")
        self.source_mi = source_mi
        navigate_mi = Gtk.MenuItem.new_with_label("Navigate")
        search_mi = Gtk.MenuItem.new_with_label("Search")
        project_mi = Gtk.MenuItem.new_with_label("Project")
        window_mi = Gtk.MenuItem.new_with_label("Window")
        help_mi = Gtk.MenuItem.new_with_label("Help")

        mb.append(file_mi)
        mb.append(edit_mi)
        mb.append(source_mi)
        mb.append(navigate_mi)
        mb.append(search_mi)
        mb.append(project_mi)
        mb.append(window_mi)
        mb.append(help_mi)

        file_me = Gtk.Menu()
        file_mi.set_submenu(file_me)

        file_open_mi = Gtk.MenuItem.new_with_label("Open")
        file_close_mi = Gtk.MenuItem.new_with_label("Close")

        file_me.append(file_open_mi)
        file_me.append(file_close_mi)

        edit_me = Gtk.Menu()
        edit_mi.set_submenu(edit_me)

        edit_cut_mi = Gtk.MenuItem.new_with_label("Cut")
        edit_copy_mi = Gtk.MenuItem.new_with_label("Copy")
        edit_paste_mi = Gtk.MenuItem.new_with_label("Paste")

        edit_me.append(edit_cut_mi)
        edit_me.append(edit_copy_mi)
        edit_me.append(edit_paste_mi)

        source_mi.set_submenu()

        self._main = mb

        return

    def get_widget(self):
        return self._main

    def destroy(self):
        self.get_widget().destroy()
        return

    def on_file_open_mi(self, mi):
        return