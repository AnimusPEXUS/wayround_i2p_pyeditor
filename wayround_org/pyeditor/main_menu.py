
import os.path

from gi.repository import Gtk, Gdk, Pango

import wayround_org.pyeditor.add_project_dialog
import wayround_org.pyeditor.buffer

import wayround_org.utils.path


class MainMenu:

    def __init__(self, main_window):

        self.main_window = main_window

        self.mode_interface = None

        mb = Gtk.MenuBar()

        tools_me = Gtk.Menu()

        tools_mi = Gtk.MenuItem.new_with_label("Tools")
        tools_mi.set_submenu(tools_me)

        change_font_mi = Gtk.MenuItem.new_with_label("Change Font..")
        tools_me.append(change_font_mi)
        change_font_mi.connect('activate', self.on_change_font_mi)

        file_mi = Gtk.MenuItem.new_with_label("File")
        project_mi = Gtk.MenuItem.new_with_label("Project")
        source_mi = Gtk.MenuItem.new_with_label("Source")
        self.source_mi = source_mi
        navigate_mi = Gtk.MenuItem.new_with_label("Navigate")

        mb.append(file_mi)
        mb.append(tools_mi)
        mb.append(project_mi)
        mb.append(source_mi)
        mb.append(navigate_mi)

        file_me = Gtk.Menu()
        file_mi.set_submenu(file_me)

        file_open_mi = Gtk.MenuItem.new_with_label("New/Open..")
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
        file_save_as_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_S,
            Gdk.ModifierType.CONTROL_MASK
            | Gdk.ModifierType.SHIFT_MASK
            | Gdk.ModifierType.MOD1_MASK,
            Gtk.AccelFlags.VISIBLE
            )

        file_save_all_mi = Gtk.MenuItem.new_with_label("Save All")
        file_save_all_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_S,
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        file_save_all_mi.connect('activate', self.on_file_save_all_mi)

        file_close_mi = Gtk.MenuItem.new_with_label("Close")
        file_close_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_W,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        file_close_mi.connect('activate', self.on_file_close_mi)

        file_close_all_mi = Gtk.MenuItem.new_with_label("Close All")
        file_close_all_mi.connect('activate', self.on_file_close_all_mi)

        file_me.append(file_open_mi)
        file_me.append(file_save_mi)
        file_me.append(file_save_as_mi)
        file_me.append(Gtk.SeparatorMenuItem())
        file_me.append(file_save_all_mi)
        file_me.append(Gtk.SeparatorMenuItem())
        file_me.append(file_close_mi)
        file_me.append(Gtk.SeparatorMenuItem())
        file_me.append(file_close_all_mi)

        project_me = Gtk.Menu()
        project_mi.set_submenu(project_me)

        project_add_mi = Gtk.MenuItem.new_with_label("Add..")
        project_rm_mi = Gtk.MenuItem.new_with_label("Remove")

        project_add_mi.connect('activate', self.on_project_add_mi)
        project_rm_mi.connect('activate', self.on_project_rm_mi)

        project_me.append(project_add_mi)
        project_me.append(project_rm_mi)

        source_mi.set_submenu()

        navigate_me = Gtk.Menu()
        navigate_mi.set_submenu(navigate_me)

        navigate_next_buff_mi = Gtk.MenuItem.new_with_label("Next Buffer")
        navigate_next_buff_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_Page_Down,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        navigate_next_buff_mi.connect(
            'activate',
            self.on_navigate_next_buff_mi
            )

        navigate_prev_buff_mi = Gtk.MenuItem.new_with_label("Previous Buffer")
        navigate_prev_buff_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_Page_Up,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        navigate_prev_buff_mi.connect(
            'activate',
            self.on_navigate_prev_buff_mi
            )

        navigate_me.append(navigate_prev_buff_mi)
        navigate_me.append(navigate_next_buff_mi)

        self._main = mb

        return

    def get_widget(self):
        return self._main

    def destroy(self):
        self.get_widget().destroy()
        return

    def on_file_open_mi(self, mi):

        path = self.main_window.project_treeview.get_selected_path()

        if not os.path.isdir(path):
            path_spl = wayround_org.utils.path.split(path)
            p = wayround_org.utils.path.join(path_spl[:-1])
            if os.path.isdir(p):
                path = p

        d = Gtk.FileChooserDialog(
            "Select File to Open (non-existing file can be selected)",
            self.main_window._window,
            Gtk.FileChooserAction.SAVE,
            [
                'Ok', Gtk.ResponseType.OK,
                'Cancel', Gtk.ResponseType.CANCEL
            ]
            )
        d.set_create_folders(True)
        d.set_current_folder(path)
        res = d.run()
        filename = None
        if res == Gtk.ResponseType.OK:
            filename = d.get_filename()

            self.main_window.open_file(filename)

        d.destroy()

        return

    def on_file_close_mi(self, mi):
        self.main_window.close_current_buffer()
        return

    def on_file_close_all_mi(self, mi):
        for i in self.main_window.buffer_clip.buffers[:]:
            self.main_window.close_buffer(i)
        return

    def on_file_save_mi(self, mi):
        if self.main_window.current_buffer is not None:
            self.main_window.current_buffer.save()
        return

    def on_file_save_all_mi(self, mi):

        for i in self.main_window.buffer_clip.buffers:
            if i.get_modified():
                i.save()

        return

    def on_project_add_mi(self, mi):
        d = wayround_org.pyeditor.add_project_dialog.AddProjectDialog(
            self.main_window
            )
        res = d.run()
        d.destroy()

        if res is not None:
            self.main_window.projects.add(res['name'], res['directory'])

        return

    def on_project_rm_mi(self, mi):

        sel = self.main_window.projects_listview.get_selection()

        if sel:

            model, itera = sel.get_selected()

            if itera:

                path = model.get_path(itera)

                name = model[path][0]

                d = Gtk.MessageDialog(
                    self.main_window.get_widget(),
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.YES_NO,
                    "Confirm project removal: {}\n\n"
                    "(none files removed. removing "
                    "only from PyEditor config records)".format(name)
                    )
                res = d.run()
                d.destroy()
                if res == Gtk.ResponseType.YES:
                    self.main_window.projects.rm(name)

        return

    def on_navigate_next_buff_mi(self, mi):

        self.main_window.select_current_buffer_in_list()

        sel = self.main_window.buffer_listview.get_selection()

        model, sel_rows = sel.get_selected_rows()

        if len(sel_rows) == 1:
            sel_row = sel_rows[0]

            sel_row_id = sel_row[0]

            if sel_row_id == model.iter_n_children() - 1:
                buf_id = int(model[Gtk.TreePath([0])][0])
            else:
                buf_id = int(model[Gtk.TreePath([sel_row_id + 1])][0])

            buf = None
            for i in self.main_window.buffer_clip.buffers:
                if id(i) == buf_id:
                    buf = i
                    break

            if buf is not None:
                self.main_window.set_buffer(buf)

        if self.main_window.source_view is not None:
            self.main_window.source_view.grab_focus()

        return

    def on_navigate_prev_buff_mi(self, mi):

        self.main_window.select_current_buffer_in_list()

        sel = self.main_window.buffer_listview.get_selection()

        model, sel_rows = sel.get_selected_rows()

        if len(sel_rows) == 1:
            sel_row = sel_rows[0]

            sel_row_id = sel_row[0]

            if sel_row_id == 0:
                buf_id = int(
                    model[Gtk.TreePath([model.iter_n_children() - 1])][0]
                    )
            else:
                buf_id = int(model[Gtk.TreePath([sel_row_id - 1])][0])

            buf = None
            for i in self.main_window.buffer_clip.buffers:
                if id(i) == buf_id:
                    buf = i
                    break

            if buf is not None:
                self.main_window.set_buffer(buf)

        if self.main_window.source_view is not None:
            self.main_window.source_view.grab_focus()

        return

    def on_change_font_mi(self, mi):
        desc = Pango.FontDescription.from_string(
            self.main_window.get_fixed_text_editor_font_desc()
            )
        d = Gtk.FontChooserDialog(
            "Select Fixed Font", 
            self.main_window.get_widget()
            )
        d.set_font_desc(desc)
        res = d.run()
        if res == Gtk.ResponseType.OK:
            self.main_window.set_fixed_text_editor_font_desc(
                d.get_font_desc().to_string()
                )
        d.destroy()
        return
