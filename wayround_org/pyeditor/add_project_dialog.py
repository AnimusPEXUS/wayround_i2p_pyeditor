
import os.path

from gi.repository import Gtk, Gdk


class AddProjectDialog:

    def __init__(self, main_window):

        self.main_window = main_window
        self.result = None

        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Adding Project")
        window.set_modal(True)
        window.set_transient_for(main_window.get_widget())
        window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        window.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        window.set_default_size(500, 300)
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

        g.attach(Gtk.Label("Name"), 0, 0, 1, 1)
        g.attach(Gtk.Label("Directory"), 0, 1, 1, 1)

        name_entry = Gtk.Entry()
        name_entry.set_hexpand(True)
        self._name_entry = name_entry

        directory_entry = Gtk.Entry()
        directory_entry.set_hexpand(True)
        self._directory_entry = directory_entry

        directory_select_button = Gtk.Button("Browse..")
        directory_select_button.set_valign(Gtk.Align.CENTER)
        directory_select_button.connect(
            'clicked',
            self.on_directory_select_button
            )

        g.attach(name_entry, 1, 0, 2, 1)
        g.attach(directory_entry, 1, 1, 1, 1)
        g.attach(directory_select_button, 2, 1, 1, 1)

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

        directory = self._directory_entry.get_text()

        if os.path.isdir(directory):

            self.result = {
                'name': self._name_entry.get_text(),
                'directory': directory,
                }
            self.stop()

        else:
            d = Gtk.MessageDialog(
                self.get_widget(),
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Directory does not exist"
                )
            d.run()
            d.destroy()

        return

    def on_cancel_button_clicked(self, widget):
        self.result = None
        self.stop()
        return

    def on_directory_select_button(self, widget):
        d = Gtk.FileChooserDialog(
            "Select Directory with Project",
            self._window,
            Gtk.FileChooserAction.SELECT_FOLDER,
            [
                'Ok', Gtk.ResponseType.OK,
                'Cancel', Gtk.ResponseType.CANCEL
                ]
            )
        res = d.run()
        filename = None
        if res == Gtk.ResponseType.OK:
            filename = d.get_filename()

            self._directory_entry.set_text(filename)

        d.destroy()

        return

    def stop(self):
        Gtk.main_quit()
        return
