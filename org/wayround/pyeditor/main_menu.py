
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

        file_close_mi = Gtk.MenuItem.new_with_label("Close")
        file_close_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_W,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        file_close_mi.connect('activate', self.on_file_close_mi)

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

        edit_delete_line_mi = Gtk.MenuItem.new_with_label("Delete Line")
        edit_delete_line_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_D,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        edit_delete_line_mi.connect(
            'activate',
            self.on_edit_delete_line_mi
            )

        edit_me.append(edit_delete_line_mi)

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

        navigate_refresh_outline_mi = \
            Gtk.MenuItem.new_with_label("Refresh Outline")

        navigate_refresh_outline_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_R,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        navigate_refresh_outline_mi.connect(
            'activate',
            self.on_navigate_refresh_outline_mi
            )

        navigate_me.append(navigate_next_buff_mi)
        navigate_me.append(navigate_prev_buff_mi)
        navigate_me.append(Gtk.SeparatorMenuItem())
        navigate_me.append(navigate_refresh_outline_mi)

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

    def on_file_close_mi(self, mi):

        self.main_window.close_current_buffer()

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

    def on_navigate_next_buff_mi(self, mi):

        buff = self.main_window.current_buffer

        if buff is None or buff in self.main_window.buffer_clip.buffers:

            new_index = -1

            if buff is None:
                new_index = 0

            else:

                buffs_count = len(self.main_window.buffer_clip.buffers)

                index = self.main_window.buffer_clip.buffers.index(buff)

                if index != -1:

                    if index == buffs_count - 1:
                        new_index = 0
                    else:
                        new_index = index + 1

                else:
                    if buffs_count != 0:
                        new_index = 0

            if new_index != -1:
                self.main_window.set_buffer(
                    self.main_window.buffer_clip.buffers[new_index]
                    )

        return

    def on_navigate_prev_buff_mi(self, mi):

        buff = self.main_window.current_buffer

        if buff is None or buff in self.main_window.buffer_clip.buffers:

            new_index = -1

            if buff is None:
                new_index = 0

            else:

                buffs_count = len(self.main_window.buffer_clip.buffers)

                index = self.main_window.buffer_clip.buffers.index(buff)

                if index != -1:

                    if index == 0:
                        new_index = buffs_count - 1
                    else:
                        new_index = index - 1
                else:
                    if buffs_count != 0:
                        new_index = buffs_count - 1

            if new_index != -1:
                self.main_window.set_buffer(
                    self.main_window.buffer_clip.buffers[new_index]
                    )

        return

    def on_edit_delete_line_mi(self, mi):

        b = self.main_window.current_buffer.get_buffer()

        if b:

            has_selection = b.get_has_selection()

            if not has_selection:
                ins = b.get_insert()
                ins_it = b.get_iter_at_mark(ins)
                ins_it_line = ins_it.get_line()

                line_it = b.get_iter_at_line(ins_it_line)
                line2_it = b.get_iter_at_line(ins_it_line + 1)

                b.delete(line_it, line2_it)

            else:

                first = b.get_iter_at_mark(b.get_insert()).get_offset()
                last = b.get_iter_at_mark(b.get_selection_bound()).get_offset()

                if first > last:
                    _x = last
                    last = first
                    first = _x
                    del _x

                first_iter_line = b.get_iter_at_line(
                    b.get_iter_at_offset(first).get_line()
                    )

                last_iter_line_plus_one = b.get_iter_at_line(
                    b.get_iter_at_offset(last).get_line() + 1
                    )

                b.delete(first_iter_line, last_iter_line_plus_one)

        return

    def on_navigate_refresh_outline_mi(self, mi):
        mi = self.main_window.mode_interface
        if mi is not None and hasattr(mi, 'outline'):
            mi.outline.reload()
        return
