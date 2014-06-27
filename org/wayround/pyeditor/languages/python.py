
from gi.repository import Gtk


class SourceMenu:

    def __init__(self, lang_interface):

        self.lang_interface = lang_interface
        self.main_window = lang_interface.main_window

        source_me = Gtk.Menu()

        source_toggle_comment_mi = Gtk.MenuItem.new_with_label(
            "Toggle Comment"
            )
        source_comment_mi = Gtk.MenuItem.new_with_label("Comment")
        source_uncomment_mi = Gtk.MenuItem.new_with_label("Uncomment")

        source_indent_mi = Gtk.MenuItem.new_with_label("Indent")
        source_dedent_mi = Gtk.MenuItem.new_with_label("Dedent")

        source_pep8_mi = Gtk.MenuItem.new_with_label("Use pep8.py")
        source_autopep8_mi = Gtk.MenuItem.new_with_label("Use autopep8.py")

        source_me.append(source_toggle_comment_mi)
        source_me.append(source_comment_mi)
        source_me.append(source_uncomment_mi)
        source_me.append(Gtk.SeparatorMenuItem())
        source_me.append(source_indent_mi)
        source_me.append(source_dedent_mi)
        source_me.append(Gtk.SeparatorMenuItem())
        source_me.append(source_pep8_mi)
        source_me.append(source_autopep8_mi)

        self._source_me = source_me

        return

    def get_widget(self):
        return self._source_me

    def destroy(self):
        self.get_widget().destroy()
        return


class LanguageInterface:

    def __init__(self, main_window):
        self.main_window = main_window
        self.source_menu = SourceMenu()
        return

    def install(self):
        self.main_window.main_menu.source_mi.set_submenu(
            self.source_menu.get_widget()
            )
        return

    def destroy(self):
        self.source_menu.destroy()
        return
