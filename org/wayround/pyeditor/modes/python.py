

import os.path
import subprocess

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GtkSource
from gi.repository import Pango

import org.wayround.pyeditor.buffer
import org.wayround.utils.path


class Buffer(
        GObject.GObject,
        org.wayround.pyeditor.buffer.Buffer
        ):

    __gsignals__ = {
        'changed': (GObject.SIGNAL_RUN_FIRST, None, tuple())
    }

    def __init__(self, main_window, filename=None):

        super().__init__()

        self.main_window = main_window
        self.filename = filename
        self._b = None

        if filename is not None:
            self.open(filename)

        return

    def open(self, filename):

        if os.path.isfile(filename):

            with open(filename, 'r') as f:
                t = f.read()

            self._b = GtkSource.Buffer()
            self._b.set_text(t)
            self._b.set_modified(False)
            self._b.connect(
                'modified-changed',
                self.on_buffer_modified_changed
                )

            self.filename = filename

            self.emit('changed')

        return

    def save(self, filename=None):

        ret = 0

        if filename is None:
            filename = self.filename

        filename = org.wayround.utils.path.abspath(filename)

        d = os.path.dirname(filename)

        if not os.path.isdir(d):
            try:
                os.makedirs(d)
            except:
                pass

            if not os.path.isdir(d):
                ret = 1

        if ret == 0:

            t = self._b.get_text(
                self._b.get_start_iter(),
                self._b.get_end_iter(),
                False
                )

            with open(filename, 'w') as f:
                f.write(t)

            self._b.set_modified(False)

            # self.emit('changed')

        return ret

    def get_modified(self):
        return self._b.get_modified()

    def set_modified(self, value):
        return self._b.set_modified(value)

    def get_buffer(self):
        return self._b

    def get_filename(self):
        return self.filename

    def destroy(self):
        return

    def get_title(self):
        return os.path.basename(self.filename)

    def get_mode_interface(self):
        return ModeInterface

    def set_mode_interface(self, mode_interface):
        self.mode_interface = mode_interface
        self._b.set_language(
            self.mode_interface.lang_mgr.get_language('python')
            )

    def on_buffer_modified_changed(self, widget):
        self.emit('changed')
        return
        
    def get_config(self):
        return {}
        
    def set_config(self, data):
        return


class View:

    def __init__(self, mode_interface):

        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window

        font_desc = Pango.FontDescription.from_string("Clean 9")

        self.view = GtkSource.View()

        self.view.override_font(font_desc)

        self.view.set_auto_indent(True)
        self.view.set_draw_spaces(
            #             GtkSource.DrawSpacesFlags.SPACE |
            #             GtkSource.DrawSpacesFlags.TAB |
            #             GtkSource.DrawSpacesFlags.NEWLINE |
            #             GtkSource.DrawSpacesFlags.NBSP |
            #             GtkSource.DrawSpacesFlags.LEADING |
            #             GtkSource.DrawSpacesFlags.TEXT |
            #             GtkSource.DrawSpacesFlags.TRAILING
            GtkSource.DrawSpacesFlags.ALL
           # GtkSource.DrawSpacesFlags(
           #     GtkSource.DrawSpacesFlags.ALL
           #     & ~GtkSource.DrawSpacesFlags.NEWLINE
           #     & ~GtkSource.DrawSpacesFlags.TEXT
           #     & ~GtkSource.DrawSpacesFlags.SPACE
           #     )
            )
        self.view.set_highlight_current_line(True)
        self.view.set_indent_on_tab(True)
        self.view.set_indent_width(4)
        self.view.set_insert_spaces_instead_of_tabs(True)
        self.view.set_right_margin_position(80)
        self.view.set_show_line_marks(True)
        self.view.set_show_line_numbers(True)
        self.view.set_show_right_margin(True)
        self.view.set_smart_home_end(True)
        self.view.set_tab_width(4)

        sw = Gtk.ScrolledWindow()
        sw.add(self.view)

        self._main = sw

        return

    def get_widget(self):
        return self._main

    def destroy(self):
        self.get_widget().destroy()
        return

    def set_buffer(self, buff):
        self.view.set_buffer(buff.get_buffer())
        return


class SourceMenu:

    def __init__(self, mode_interface):

        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window
        
        main_window = self.main_window

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
        source_autopep8_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_F,
            Gdk.ModifierType.CONTROL_MASK
                | Gdk.ModifierType.SHIFT_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        source_autopep8_mi.connect(
            'activate',
            self.on_source_autopep8_mi
            )


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
        
    def on_source_autopep8_mi(self, mi):
        
        buff = sekf.main_window.current_buffer
        
        if buff is not None:
            
            b = buff.get_buffer()
            
            t = b.get_text(
                b.get_start_iter(),
                b.get_end_iter(),
                False
                )
            
            strio1 = io.StringIO(t)
            strio2 = io.StringIO()
            
            p=subprocess.Popen(
                ['autopep8', '--ignore', 'E123'], 
                strin=strion1, 
                strout=strio2
                )
            res = p.wait()
            
            strio1.close()
                                    
            strio2.seek(0)
            t = strio2.read()
            
            strio2.close()
            
            if res == 0:
            
                b.set_text(t)
        
        return


class ModeInterface:

    def __init__(self, main_window):
        self.main_window = main_window
        self.source_menu = SourceMenu(self)
        self.view = View(self)
        self.lang_mgr = GtkSource.LanguageManager.get_default()
        return

    def destroy(self):
        self.source_menu.destroy()
        self.view.destroy()
        return

    def get_menu(self):
        return self.source_menu.get_widget()

    def get_view(self):
        return self.view.get_widget()

    def set_buffer(self, buff):

        if not isinstance(buff, Buffer):
            raise Exception(
                "`buff' must be an instance of "
                "org.wayround.pyeditor.modes.python.Buffer"
                )

        buff.set_mode_interface(self)
        self.view.set_buffer(buff)
        return
