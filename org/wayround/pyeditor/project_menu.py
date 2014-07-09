
import os.path

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

import org.wayround.utils.gtk
import org.wayround.utils.path
import org.wayround.utils.file
import org.wayround.utils.error

import org.wayround.pyeditor.rename_file_dialog


class ProjectMenu:

    def __init__(self, main_window, files_tree):

        if not isinstance(
                files_tree,
                org.wayround.utils.gtk.DirectoryTreeView
                ):
            raise TypeError(
                "`files_tree' must be instance of "
                "org.wayround.utils.gtk.DirectoryTreeView"
                )

        self.main_window = main_window
        self.files_tree = files_tree

        menu = Gtk.Menu()

        open_file_manager_mi = Gtk.MenuItem("Open With External Program")
        open_file_manager_mi.connect('activate', self.on_open_file_manager_mi)

        create_directory_mi = Gtk.MenuItem("Create Dir..")
        create_directory_mi.connect('activate', self.on_create_directory_mi)

        rename_mi = Gtk.MenuItem("Rename..")
        rename_mi.connect('activate', self.on_rename_mi)

        delete_mi = Gtk.MenuItem("Delete..")
        delete_mi.connect('activate', self.on_delete_mi)

        menu.append(open_file_manager_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(create_directory_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(rename_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(delete_mi)

        menu.show_all()

        self._main = menu

        return

    def get_widget(self):
        return self._main

    def on_open_file_manager_mi(self, mi):
        path = self.main_window.project_treeview.get_selected_path()

        uri = GLib.uri_escape_string(path, None, True)
        Gtk.show_uri(None, uri, Gdk.CURRENT_TIME)
        return

    def on_create_directory_mi(self, mi):
        path = self.main_window.project_treeview.get_selected_path()

        if not os.path.isdir(path):
            path_spl = org.wayround.utils.path.split(path)
            p = org.wayround.utils.path.join(path_spl[:-1])
            if os.path.isdir(p):
                path = p

        d = Gtk.FileChooserDialog(
            "Create Directory",
            self.main_window.get_widget(),
            Gtk.FileChooserAction.CREATE_FOLDER,
            [
                'Ok', Gtk.ResponseType.OK,
                'Cancel', Gtk.ResponseType.CANCEL
                ]
            )
        d.set_current_folder(path)
        res = d.run()
        filename = None
        if res == Gtk.ResponseType.OK:
            filename = d.get_filename()

            self._directory_entry.set_text(filename)

        d.destroy()
        return

    def on_rename_mi(self, mi):

        path = self.main_window.project_treeview.get_selected_path()

        d = org.wayround.pyeditor.rename_file_dialog.RenameFileDialog(
            self.main_window,
            path,
            ''
            )
        res = d.run()
        d.destroy()
        if res is not None:

            d = os.path.dirname(path)
            dn = org.wayround.utils.path.join(d, res)
            try:
                os.rename(path, dn)
            except:

                t = org.wayround.utils.error.return_exception_info(
                    sys.exc_info()
                    )

                d = Gtk.MessageDialog(
                    self.main_window.get_widget(),
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Can't rename file\n\n{}".format(t)
                    )
                d.run()
                d.destroy()

            pth_spl = org.wayround.utils.path.split(path)[:-1]
            if len(pth_spl) > 0:
                pth = org.wayround.utils.path.join(pth_spl)

                self.main_window.project_treeview.load_dir(
                    self.main_window.project_treeview.
                    get_selected_iter_parent(),
                    pth
                    )
        return

    def on_delete_mi(self, mi):

        path = self.main_window.project_treeview.get_selected_path()

        d = Gtk.MessageDialog(
            self.main_window.get_widget(),
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            "Confirm deletion of {}".format(path)
            )
        res = d.run()
        d.destroy()
        if res == Gtk.ResponseType.YES:
            org.wayround.utils.file.remove_if_exists(path)

            pth_spl = org.wayround.utils.path.split(path)[:-1]
            if len(pth_spl) > 0:
                pth = org.wayround.utils.path.join(pth_spl)

                self.main_window.project_treeview.load_dir(
                    self.main_window.project_treeview.
                    get_selected_iter_parent(),
                    pth
                    )
        return
