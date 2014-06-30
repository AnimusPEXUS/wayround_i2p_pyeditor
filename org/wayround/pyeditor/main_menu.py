
from gi.repository import Gtk, Gdk

import org.wayround.pyeditor.add_project_dialog
import org.wayround.pyeditor.buffer


class MainMenu:

    def __init__(self, main_window):

        self.main_window = main_window

        self.mode_interface = None

        mb = Gtk.MenuBar()

        file_mi = Gtk.MenuItem.new_with_label("File")
        project_mi = Gtk.MenuItem.new_with_label("Project")
        edit_mi = Gtk.MenuItem.new_with_label("Edit")
        source_mi = Gtk.MenuItem.new_with_label("Source")
        self.source_mi = source_mi
        navigate_mi = Gtk.MenuItem.new_with_label("Navigate")
        search_mi = Gtk.MenuItem.new_with_label("Search")
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
        file_open_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_O,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        file_open_mi.connect('activate', self.on_file_open_mi)

        file_save_mi = Gtk.MenuItem.new_with_label("Save")
        file_save_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_S,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        file_save_mi.connect('activate', self.on_file_save_mi)

        file_save_as_mi = Gtk.MenuItem.new_with_label("Save as..")

        file_save_all_mi = Gtk.MenuItem.new_with_label("Save All")
        file_save_all_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_S,
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
            Gtk.AccelFlags.VISIBLE
            )

        file_close_mi = Gtk.MenuItem.new_with_label("Close")

        file_me.append(file_open_mi)
        file_me.append(file_save_mi)
        file_me.append(file_save_as_mi)
        file_me.append(Gtk.SeparatorMenuItem())
        file_me.append(file_save_all_mi)
        file_me.append(Gtk.SeparatorMenuItem())
        file_me.append(file_close_mi)

        project_me = Gtk.Menu()
        project_mi.set_submenu(project_me)

        project_add_mi = Gtk.MenuItem.new_with_label("Add")
        project_delete_mi = Gtk.MenuItem.new_with_label("Delete")

        project_add_mi.connect('activate', self.on_project_add_mi)

        project_me.append(project_add_mi)
        project_me.append(project_delete_mi)

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
        print('activated')
        return

    def on_file_save_mi(self, mi):
        if self.main_window.current_buffer is not None:
            self.main_window.current_buffer.save()
        return

    def on_project_add_mi(self, mi):
        d = org.wayround.pyeditor.add_project_dialog.AddProjectDialog(
            self.main_window
            )
        res = d.run()
        d.destroy()

        if res is not None:
            self.main_window.projects.add(res['name'], res['directory'])

        return
