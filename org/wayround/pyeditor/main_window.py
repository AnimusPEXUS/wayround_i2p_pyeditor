
from gi.repository import Gtk
from gi.repository import GtkSource

import org.wayround.pyeditor.main_menu
import org.wayround.pyeditor.buffer_clip


class MainWindow:

    def __init__(self):

        window = Gtk.Window()
        window.connect('delete-event', self.on_delete)

        self.main_menu = org.wayround.pyeditor.main_menu.MainMenu(self)
        buffer_clip = org.wayround.pyeditor.buffer_clip.BufferClip(self)
        buffer_clip.connect('list-changed', self.on_buffer_clip_list_changed)
        self.buffer_clip = buffer_clip

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        menu_bar = self.main_menu.get_widget()

        source_view = GtkSource.View()
        self.source_view = source_view

        buffer_listview = Gtk.ListView()
        projects_listview = Gtk.ListView()
        outline_listview = Gtk.ListView()
        project_treeview = Gtk.TreeView()

        paned_v = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        paned_h1 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        paned_h2 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        projects_notebook = Gtk.Notebook()

        projects_notebook.insert_page(
            projects_listview,
            Gtk.Label("Projects"),
            0
            )

        projects_notebook.insert_page(
            project_treeview,
            Gtk.Label("Project"),
            0
            )

        paned_v.add1()
        paned_v.add2(buffer_listview)

        paned_h1.add1(paned_v)
        paned_h1.add2(paned_h2)

        paned_h2.add2(source_view)
        paned_h2.add2(outline_listview)

        b.pack_start(menu_bar, False, False, 0)

        window.add(b)

        self._window = window

        return

    def get_widget(self):
        return self._window

    def show(self):
        self.get_widget().show_all()

    def destroy(self):
        self.main_menu.destroy()
        return

    def on_delete(self, widget, event):
        return Gtk.main_quit()

    def on_buffer_clip_list_changed(self, widget):
        return
