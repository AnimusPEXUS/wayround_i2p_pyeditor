
import os.path

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

import wayround_org.utils.gtk
import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.utils.error

import wayround_org.pyeditor.rename_file_dialog


class ProjectMenu:

    def __init__(self, main_window, files_tree):

        if not isinstance(
                files_tree,
                wayround_org.utils.gtk.DirectoryTreeView
                ):
            raise TypeError(
                "`files_tree' must be instance of "
                "wayround_org.utils.gtk.DirectoryTreeView"
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

        path = 'file://' + path

        #path = GLib.uri_escape_string(path, None, True)

        print("path: {}".format(path))
        Gtk.show_uri(None, path, Gdk.CURRENT_TIME)
        return

    def on_create_directory_mi(self, mi):
        path = self.main_window.project_treeview.get_selected_path()

        if not os.path.isdir(path):
            path_spl = wayround_org.utils.path.split(path)
            p = wayround_org.utils.path.join(path_spl[:-1])
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

            os.makedirs(filename)

        d.destroy()
        return

    def on_rename_mi(self, mi):

        path = self.main_window.project_treeview.get_selected_path()

        d = wayround_org.pyeditor.rename_file_dialog.RenameFileDialog(
            self.main_window,
            path,
            ''
            )
        res = d.run()
        d.destroy()
        if res is not None:

            d = os.path.dirname(path)
            dn = wayround_org.utils.path.join(d, res)
            try:
                os.rename(path, dn)
            except:

                t = wayround_org.utils.error.return_exception_info(
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

            pth_spl = wayround_org.utils.path.split(path)[:-1]
            if len(pth_spl) > 0:
                pth = wayround_org.utils.path.join(pth_spl)

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
            wayround_org.utils.file.remove_if_exists(path)

            pth_spl = wayround_org.utils.path.split(path)[:-1]
            if len(pth_spl) > 0:
                pth = wayround_org.utils.path.join(pth_spl)

                self.main_window.project_treeview.load_dir(
                    self.main_window.project_treeview.
                    get_selected_iter_parent(),
                    pth
                    )
        return
