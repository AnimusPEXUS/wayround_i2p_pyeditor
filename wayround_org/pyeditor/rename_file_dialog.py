

import os.path

from gi.repository import Gtk, Gdk


class RenameFileDialog:

    def __init__(self, main_window, old_filename, new_filename_base=''):

        self.main_window = main_window
        self.old_filename = old_filename

        if new_filename_base == '':
            new_filename_base = os.path.basename(old_filename)

        self.result = None

        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Rename File")
        window.set_modal(True)
        window.set_transient_for(main_window.get_widget())
        window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        window.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self._window = window

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)

        g = Gtk.Grid()
        g.set_column_spacing(5)
        g.set_row_spacing(5)
        g.set_row_homogeneous(True)

        b.pack_start(g, True, True, 0)

        window.add(b)

        g.attach(Gtk.Label("Current Full Filename"), 0, 0, 1, 1)
        g.attach(Gtk.Label("New base or relative name"), 0, 1, 1, 1)

        name_label = Gtk.Label(old_filename)
        name_label.set_hexpand(True)
        self._name_label = name_label

        newname_entry = Gtk.Entry()
        newname_entry.set_text(new_filename_base)

        newname_entry.set_hexpand(True)
        self._newname_entry = newname_entry

        g.attach(name_label, 1, 0, 1, 1)
        g.attach(newname_entry, 1, 1, 1, 1)

        bb = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)

        ok_button = Gtk.Button("Ok")
        ok_button.connect('clicked', self.on_ok_button_clicked)
        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self._cancel_button = cancel_button

        bb.pack_start(ok_button, False, False, 0)
        bb.pack_start(cancel_button, False, False, 0)

        b.pack_start(bb, False, False, 0)

        window.connect('delete-event', self.on_delete)

        return

    def run(self):
        self.show()
        Gtk.main()
        return self.result

    def show(self):
        self.get_widget().show_all()
        return

    def destroy(self):
        self.get_widget().destroy()
        return

    def on_delete(self, widget, event):
        return self._cancel_button.emit('clicked')

    def get_widget(self):
        return self._window

    def on_ok_button_clicked(self, widget):

        newname = self._newname_entry.get_text()

        if newname != '':

            self.result = newname
            self.stop()

        else:
            d = Gtk.MessageDialog(
                self.get_widget(),
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "New name field must be not empty"
                )
            d.run()
            d.destroy()

        return

    def on_cancel_button_clicked(self, widget):
        self.result = None
        self.stop()
        return

    def stop(self):
        Gtk.main_quit()
        return
