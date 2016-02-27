
import io
import os.path
import subprocess
import re
import modulefinder

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GtkSource
from gi.repository import Pango
from gi.repository import GLib

import wayround_org.utils.path
import wayround_org.utils.timer
import wayround_org.utils.gtk

import wayround_org.pyeditor.buffer

C_COMMENT_RE = re.compile(
    r'/\*.*?\*/',
    flags=re.M | re.S,
    )

CPP_COMMENT_RE = re.compile(
    r'//.*$'
    )


class Buffer(
        GObject.GObject,
        wayround_org.pyeditor.buffer.Buffer
        ):

    __gsignals__ = {
        'changed': (GObject.SIGNAL_RUN_FIRST, None, tuple())
        }

    @staticmethod
    def get_mode_interface():
        raise Exception(
            "You must override this method in your class."
            " It must return ModeInterface class (not it's instance)"
            )
        return ModeInterface

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

        t = ''

        if os.path.isfile(filename):

            with open(filename, 'r') as f:
                t = f.read()

        if self._b is None:
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

    def reopen(self):
        return self.open(self.filename)

    def save(self, filename=None):

        ret = 0

        if filename is None:
            filename = self.filename

        filename = wayround_org.utils.path.abspath(filename)

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
        super().destroy()
        return

    def get_title(self):
        return os.path.basename(self.filename)

    def set_mode_interface(self, mode_interface):
        self.mode_interface = mode_interface
        return

    def set_language(self, language):
        self._b.set_language(language)
        return

    def on_buffer_modified_changed(self, widget):
        self.emit('changed')
        return

    def get_config(self):
        return self.state

    def set_config(self, data):
        self.state = data
        self.restore_state()
        return

    def save_state(self):

        if self._b:

            m = self._b.get_insert()
            i = self._b.get_iter_at_mark(m)
            cp = i.get_offset()
            self.state['cursor-position'] = cp

            if self.main_window.current_buffer == self:
                sw = self.mode_interface.get_view_widget_sw()
                if sw is not None:
                    vsb = sw.get_vscrollbar()
                    if vsb is not None:
                        value = vsb.get_value()
                        self.state['v-scroll-pos'] = value
                
                if hasattr(self.mode_interface.view, 'outline_sw'):
                    sw = self.mode_interface.view.outline_sw
                    if sw is not None:
                        vsb = sw.get_vscrollbar()
                        if vsb is not None:
                            value = vsb.get_value()
                            self.state['outline-v-scroll-pos'] = value
                    
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

            if 'outline-v-scroll-pos' in self.state:
                
                if hasattr(self.mode_interface.view, 'outline_sw'):
                    sw = self.mode_interface.view.outline_sw

                    if sw is not None:
                        vsb = sw.get_vscrollbar()
                        if vsb is not None:
                            value = self.state['outline-v-scroll-pos']
                            vsb.set_value(value)

        return


class View:

    @staticmethod
    def get_language_name():
        raise Exception(
            "You must override this staticmethod in your class."
            " It must return single word string (language name)"
            )
        return 'python'

    def __init__(self, mode_interface):

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window

        paned_h2 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.paned_h2 = paned_h2

        font_desc = Pango.FontDescription.from_string(
            self.main_window.get_fixed_text_editor_font_desc()
            )
        outline_treeview = Gtk.TreeView()
        outline_treeview.set_activate_on_single_click(True)
        outline_treeview.connect(
            'row-activated',
            self.on_outline_treeview_row_activated
            )
        outline_treeview.override_font(font_desc)
        outline_treeview.set_model(Gtk.ListStore(str, str))
        outline_treeview.set_headers_visible(False)
        self.outline = outline_treeview

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 0)
        # _c.set_title('Line')
        outline_treeview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'markup', 1)
        # _c.set_title('Text')
        outline_treeview.append_column(_c)

        outline_treeview_sw = Gtk.ScrolledWindow()
        self.outline_sw = outline_treeview_sw
        outline_treeview_sw.set_overlay_scrolling(False)
        outline_treeview_sw.add(outline_treeview)

        self.view = GtkSource.View()

        self.view.override_font(font_desc)

        self.apply_spec_view_settings()

        sw = Gtk.ScrolledWindow()
        self._sw = sw
        sw.add(self.view)
        sw.set_overlay_scrolling(False)

        self._status_label = Gtk.Label()
        self._status_label.set_alignment(0, 0.5)
        self._status_label.set_selectable(True)

        # sw_f = Gtk.Frame()
        # sw_f.add(sw)

        b.pack_start(sw, True, True, 0)
        b.pack_start(self._status_label, False, True, 0)

        self._main = paned_h2

        # outline_treeview_sw_f = Gtk.Frame()
        # outline_treeview_sw_f.add(outline_treeview_sw)

        paned_h2.add1(b)
        paned_h2.add2(outline_treeview_sw)
        paned_h2.child_set_property(outline_treeview_sw, 'resize', False)
        paned_h2.child_set_property(outline_treeview_sw, 'shrink', True)

        self._signal_pointer = None
        self._completion_sig_point = None

        if not self.main_window.cfg.cfg.has_section(self.get_language_name()):
            self.main_window.cfg.cfg.add_section(self.get_language_name())

        p3_pos = self.main_window.cfg.cfg.getint(
            self.get_language_name(),
            'paned_pos',
            fallback=500
            )

        paned_h2.set_position(p3_pos)

        return

    def apply_spec_view_settings(self):
        return

    def get_view_widget_sw(self):
        return self._sw

    def get_view_widget(self):
        return self.view

    def get_widget(self):
        return self._main

    def destroy(self):

        p = self.paned_h2.get_position()
        self.main_window.cfg.cfg.set(
            self.get_language_name(),
            'paned_pos',
            str(p)
            )

        self.main_window.buffer_clip.save_config()

        if self._main:
            self._main.destroy()
        if self.view:
            self.view.destroy()
        if self._sw:
            self._sw.destroy()
        return

    def set_buffer(self, buff):

        b = self.view.get_buffer()

        if b is not None:
            if self._signal_pointer:
                b.disconnect(self._signal_pointer)

        b = buff.get_buffer()
        self.view.set_buffer(b)

        self._signal_pointer = b.connect(
            'notify::cursor-position',
            self.on_cursor_position
            )

        return

    def _refresh_status(self):
        b = self.view.get_buffer()

        itera = b.get_iter_at_mark(b.get_insert())

        self._status_label.set_text(
            """\
line index: {} | column index: {} | offset (hex): {:x}
line: {} | column: {} | offset: {}""".format(
                itera.get_line(),
                itera.get_line_offset(),
                itera.get_offset(),
                itera.get_line() + 1,
                itera.get_line_offset() + 1,
                itera.get_offset()
                )
            )

    def on_cursor_position(self, gobject, pspec):
        self._refresh_status()
        return

    def on_outline_treeview_row_activated(self, widget, path, column):

        v = self.view

        m = widget.get_model()
        line = int(m[path][0])

        if v:
            b = v.get_buffer()
            i = b.get_iter_at_line(line - 1)
            b.place_cursor(i)
            v.scroll_to_iter(i, 0, True, 0.0, 0.2)
        return


class Outline:

    def __init__(self, mode_interface):
        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window
        self.source_view = mode_interface.get_view_widget()
        self.outline = self.mode_interface.get_view().outline

    def clear(self):
        m = self.outline.get_model()

        chi = m.get_iter_first()
        res = True

        while chi is not None and res is not False:
            res = m.remove(chi)

        return

    def reload(self):

        val = None
        o_sw = self.mode_interface.get_view().outline_sw
        vscrl = o_sw.get_vscrollbar()
        if vscrl:
            val = vscrl.get_value()

        self.clear()

        m = self.outline.get_model()

        b = self.source_view.get_buffer()

        res = self.search(b)

        for i in sorted(list(res.keys())):
            m.append([str(i + 1), res[i]])

        if val is not None:
            vscrl = o_sw.get_vscrollbar()
            if vscrl:
                GLib.idle_add(self._restore_vscroll, vscrl, val)

        return

    def search(self):
        raise Exception(
            "You must override this method in your class."
            " It must return dict where key in int and value is str"
            )
        return 'python'

    def _restore_vscroll(self, vscrl, val):
        vscrl.set_value(val)
        return


def get_selected_lines(buff):
    """
    Returns numbers of selected lines

    the 3rd result value - is bool, indicatind whatever some text is actually
    selected or 1st and 2nd results are simply indicating line in which cursor
    is currently positioned
    """

    ret = None, None, False

    b = buff

    if b:

        has_selection = b.get_has_selection()

        if not has_selection:
            ins = b.get_insert()
            ins_it = b.get_iter_at_mark(ins)
            ins_it_line = ins_it.get_line()

            ret = ins_it_line, ins_it_line, False

        else:

            first = b.get_iter_at_mark(b.get_insert()).get_offset()
            last = b.get_iter_at_mark(b.get_selection_bound()).get_offset()

            if first > last:
                _x = last
                last = first
                first = _x
                del _x

            first_l = b.get_iter_at_offset(first).get_line()
            last_l = first_l

            last_line_off = b.get_iter_at_offset(last).get_line_offset()

            if last_line_off == 0:
                last_l = b.get_iter_at_offset(last).get_line() - 1
            else:
                last_l = b.get_iter_at_offset(last).get_line()

            if last_l < first_l:
                last_l = first_l

            ret = first_l, last_l, True

    return ret


def indent_text(txt, de=False, indent_size=4):

    indent_space = ' ' * indent_size

    lines = txt.splitlines()

    if not de:
        for i in range(len(lines)):
            if lines[i] != '':
                lines[i] = '{}{}'.format(indent_space, lines[i])
    else:
        can_dedent = True
        for i in lines:
            if not i.startswith(indent_space) and not i == '':
                can_dedent = False
                break
        if can_dedent:
            for i in range(len(lines)):
                if lines[i] != '':
                    lines[i] = lines[i][indent_size:]

    return '\n'.join(lines)


def indent_buffer(buff, de=False, indent_size=4):

    b = buff

    res = get_selected_lines(buff)

    do_final_select = res[2]

    f_i = b.get_iter_at_line(res[0])
    l_i = b.get_iter_at_offset(
        b.get_iter_at_line(
            res[1] + 1
            ).get_offset() - 1,
        )

    t = b.get_text(f_i, l_i, False)

    t = indent_text(t, de, indent_size)

    b.delete(f_i, l_i)

    b.insert(f_i, t)

    f_i = b.get_iter_at_line(res[0])
    l_i = b.get_iter_at_offset(
        b.get_iter_at_line(
            res[1] + 1
            ).get_offset() - 1,
        )

    if do_final_select:
        b.select_range(f_i, l_i)
    else:
        pass

    return


def delete_selected_lines(buff):

    res = get_selected_lines(buff)

    buff.delete(
        buff.get_iter_at_line(res[0]),
        buff.get_iter_at_line(res[1] + 1)
        )

    return


def find_c_comments(text):
    """
    Searches for comments and returns list of ranges

    `text' must be bytes
    """

    comments_list = []

    for i in C_COMMENT_RE.finditer(text):
        r = range(i.start(), i.end())
        comments_list.append(r)

    for i in CPP_COMMENT_RE.finditer(text):
        r = range(i.start(), i.end())
        comments_list.append(r)

    ret = merge_c_overlapping_comments(comments_list)

    return ret


def merge_c_overlapping_comments(comments_list):
    ret = []

    for i in comments_list:
        found = False
        for j in ret:

            if i.start in j or i.stop in j:

                j_index = ret.index(j)

                if i.start in j and not i.stop in j:
                    ret[j_index] = range(j.start, i.stop)
                    j = ret[j_index]

                if i.end in j and not i.start in j:
                    ret[j_index] = range(i.start, j.stop)
                    j = ret[j_index]

                found = True
                break

        if not found:
            ret.append(i)

    return ret


def delete_trailing_whitespace(text):
    lines = text.split('\n')
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    return '\n'.join(lines)
