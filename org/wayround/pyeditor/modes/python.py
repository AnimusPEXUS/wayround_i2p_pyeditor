
import io
import os.path
import subprocess
import re

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GtkSource
from gi.repository import Pango
from gi.repository import GLib

import org.wayround.pyeditor.buffer
import org.wayround.utils.path


SYMBOL_REGEXP = re.compile(
    r'^[ \t]*(def |class )(.|\n)*?\s*:[ \t]*$',
    flags=re.M)


class Buffer(
        GObject.GObject,
        org.wayround.pyeditor.buffer.Buffer
        ):

    __gsignals__ = {
        'changed': (GObject.SIGNAL_RUN_FIRST, None, tuple())
    }

    def __init__(self, main_window, filename=None):

        super().__init__()

        self.state = {}
        self.mode_interface = None

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

            if self.mode_interface:
                self.mode_interface.outline.reload()

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

    def save_state(self):

        if self._b:

            m = self._b.get_insert()
            i = self._b.get_iter_at_mark(m)
            cp = i.get_offset()
            self.state['cursor-position'] = cp

            if self.main_window.current_buffer == self:
                sw = self.main_window.source_view_sw
                if sw is not None:
                    vsb = sw.get_vscrollbar()
                    if vsb is not None:
                        value = vsb.get_value()
                        self.state['v-scroll-pos'] = value

        return

    def restore_state(self):

        if self._b:

            if 'cursor-position' in self.state:
                cp = self.state['cursor-position']

                i = self._b.get_iter_at_offset(cp)

                self._b.place_cursor(i)

            GLib.idle_add(self.restore_state_idle)

        return

    def restore_state_idle(self):
        if self.main_window.current_buffer == self:

            if 'v-scroll-pos' in self.state:

                sw = self.main_window.source_view_sw
                if sw is not None:
                    vsb = sw.get_vscrollbar()
                    if vsb is not None:
                        value = self.state['v-scroll-pos']
                        vsb.set_value(value)

        return


class View:

    def __init__(self, mode_interface):

        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window

        font_desc = Pango.FontDescription.from_string("Clean 9")

        self.view = GtkSource.View()

        self.view.override_font(font_desc)

        self.view.set_auto_indent(True)
        self.view.set_draw_spaces(GtkSource.DrawSpacesFlags.ALL)
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

    def get_widget_sw(self):
        return self._main

    def get_widget(self):
        return self.view

    def destroy(self):
        if self._main:
            self._main.destroy()
        if self.view:
            self.view.destroy()
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

        try:
            import autopep8
        except:
            logging.exception("Can't use autopep8")
        else:

            buff = self.main_window.current_buffer

            if buff is not None:

                b = buff.get_buffer()

                t = b.get_text(
                    b.get_start_iter(),
                    b.get_end_iter(),
                    False
                    )

                buff.save_state()

                t = autopep8.fix_code(
                    t,
                    options=autopep8.parse_args(
                        ['--aggressive', '--ignore', 'E123', '']
                        )
                    )

                b.set_text(t)

                buff.restore_state()

        return


class Outline:

    def __init__(self, mode_interface):
        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window
        self.source_view = mode_interface.get_view()
        self.outline = self.main_window.outline

    def clear(self):
        m = self.outline.get_model()

        chi = m.get_iter_first()
        res = True

        while chi is not None and res is not False:
            res = m.remove(chi)

        return

    def reload(self):

        self.clear()

        m = self.outline.get_model()

        b = self.source_view.get_buffer()
        t = b.get_text(
            b.get_start_iter(),
            b.get_end_iter(),
            False
            )

        for i in SYMBOL_REGEXP.finditer(t):

            line = b.get_iter_at_offset(i.start()).get_line()
            s = b.get_iter_at_line(line)
            e = b.get_iter_at_offset(i.end())

            # TODO: figure out why markup is not copyed to outline.
            #        mingwhile setting it to False
            t2 = b.get_text(s, e, False)

            m.append([str(line + 1), t2])

        return


class ModeInterface:

    def __init__(self, main_window):
        self.main_window = main_window
        self.source_menu = SourceMenu(self)
        self.view = View(self)

        self.outline = Outline(self)

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

    def get_view_sw(self):
        return self.view.get_widget_sw()

    def set_buffer(self, buff):

        if not isinstance(buff, Buffer):
            raise Exception(
                "`buff' must be an instance of "
                "org.wayround.pyeditor.modes.python.Buffer"
                )

        buff.set_mode_interface(self)
        self.view.set_buffer(buff)
        self.outline.reload()
        return
