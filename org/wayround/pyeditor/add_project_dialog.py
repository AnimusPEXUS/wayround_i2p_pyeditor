
import os.path

from gi.repository import Gtk


class AddProjectDialog:

    def __init__(self, main_window):
        self.main_window = main_window
        self.result = None

        window = Gtk.Window()
        window.set_title("Adding Project")
        self._window = window

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        g = Gtk.Grid()

        b.pack_start(g, True, True, 0)

        window.add(b)

        g.attach(Gtk.Label("Name"), 0, 0, 1, 1)
        g.attach(Gtk.Label("Directory"), 0, 1, 1, 1)

        name_entry = Gtk.Entry()
        self._name_entry = name_entry
        directory_entry = Gtk.Entry()
        self._directory_entry = directory_entry

        g.attach(name_entry, 1, 0, 1, 1)
        g.attach(directory_entry, 1, 1, 1, 1)

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

    def stop(self):
        Gtk.main_quit()
        return
