
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

import org.wayround.utils.path
import org.wayround.utils.timer
import org.wayround.utils.gtk

import org.wayround.pyeditor.buffer


SUPPORTED_MIME = ['text/x-python']

SUPPORTED_EXT = ['py']

SYMBOL_REGEXP = re.compile(
    r'^[ \t]*(def |class )(.|\n)*?\s*:[ \t]*$',
    flags=re.M
    )

SYMBOL2_REGEXP = re.compile(
    r'^([ \t]*[a-zA-Z_][a-zA-Z0-9_\.]*?)[ \t]*\=.*$',
    flags=re.M
    )


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

        t = ''

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
        super().destroy()
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

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window

        paned_h2 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.paned_h2 = paned_h2

        font_desc = Pango.FontDescription.from_string("Clean 9")
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
        outline_treeview_sw.add(outline_treeview)

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
        self._sw = sw
        sw.add(self.view)

        self._status_label = Gtk.Label()
        self._status_label.set_alignment(0, 0.5)
        self._status_label.set_selectable(True)

        sw_f = Gtk.Frame()
        sw_f.add(sw)

        b.pack_start(sw_f, True, True, 0)
        b.pack_start(self._status_label, False, True, 0)

        self._main = paned_h2

        outline_treeview_sw_f = Gtk.Frame()
        outline_treeview_sw_f.add(outline_treeview_sw)

        paned_h2.add1(b)
        paned_h2.add2(outline_treeview_sw_f)

        self._signal_pointer = None
        self._completion_sig_point = None

        if not self.main_window.cfg.cfg.has_section('python'):
            self.main_window.cfg.cfg.add_section('python')

        p3_pos = self.main_window.cfg.cfg.getint(
            'python',
            'paned_pos',
            fallback=500
            )

        # print("got position: {}".format(p3_pos))

        paned_h2.set_position(p3_pos)

        return

    def get_view_widget_sw(self):
        return self._sw

    def get_view_widget(self):
        return self.view

    def get_widget(self):
        return self._main

    def destroy(self):

        p = self.paned_h2.get_position()
        # print("saving position: {}".format(p))
        self.main_window.cfg.cfg.set(
            'python',
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
            "line index: {}, "
            "column index: {}, "
            "line: {}, "
            "column: {}, "
            "offset: {}, "
            "offset (hex): {:x}".format(
                itera.get_line(),
                itera.get_line_offset(),
                itera.get_line() + 1,
                itera.get_line_offset() + 1,
                itera.get_offset(),
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
            v.scroll_to_iter(i, 0, True, 0.0, 0.5)
        return


class SourceMenu:

    def __init__(self, mode_interface):

        self.mode_interface = mode_interface
        self.main_window = mode_interface.main_window

        main_window = self.main_window

        source_me = Gtk.Menu()

        # source_toggle_comment_mi = Gtk.MenuItem.new_with_label(
        #     "Toggle Comment"
        #     )
        # source_comment_mi = Gtk.MenuItem.new_with_label("Comment")
        # source_uncomment_mi = Gtk.MenuItem.new_with_label("Uncomment")

        source_indent_mi = Gtk.MenuItem.new_with_label("Indent")
        source_indent_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_I,
            Gdk.ModifierType.CONTROL_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        source_indent_mi.connect(
            'activate',
            self.on_indent_mi,
            False
            )

        source_dedent_mi = Gtk.MenuItem.new_with_label("Dedent")
        source_dedent_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_I,
            Gdk.ModifierType.CONTROL_MASK
            | Gdk.ModifierType.SHIFT_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        source_dedent_mi.connect(
            'activate',
            self.on_indent_mi,
            True
            )

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

        # source_me.append(source_toggle_comment_mi)
        # source_me.append(source_comment_mi)
        # source_me.append(source_uncomment_mi)
        # source_me.append(Gtk.SeparatorMenuItem())

        source_me.append(edit_delete_line_mi)
        source_me.append(Gtk.SeparatorMenuItem())

        source_me.append(source_indent_mi)
        source_me.append(source_dedent_mi)
        source_me.append(Gtk.SeparatorMenuItem())

        source_me.append(source_pep8_mi)
        source_me.append(source_autopep8_mi)
        source_me.append(Gtk.SeparatorMenuItem())

        source_me.append(navigate_refresh_outline_mi)

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

    def on_edit_delete_line_mi(self, mi):

        res = self._get_selected_lines()

        b = self.main_window.current_buffer.get_buffer()
        b.delete(
            b.get_iter_at_line(res[0]),
            b.get_iter_at_line(res[1] + 1)
            )

        return

    def on_navigate_refresh_outline_mi(self, mi):
        mi = self.main_window.mode_interface
        if mi is not None and hasattr(mi, 'outline'):
            mi.outline.reload()
        return

    def _get_selected_lines(self):

        ret = None, None, False

        b = self.main_window.current_buffer.get_buffer()

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

    def on_indent_mi(self, mi, de=False):
        b = self.main_window.current_buffer.get_buffer()
        res = self._get_selected_lines()

        do_final_select = res[2]

        f_i = b.get_iter_at_line(res[0])
        l_i = b.get_iter_at_offset(
            b.get_iter_at_line(
                res[1] + 1
                ).get_offset() - 1,
            )

        t = b.get_text(f_i, l_i, False)

        t = indent(t, de=de)

        b.delete(f_i, l_i)

        b.insert(f_i, t)

        # l1_i = b.get_iter_at_line(res[0])
        # l2_i = b.get_iter_at_line(res[1] + 1)

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
        t = b.get_text(
            b.get_start_iter(),
            b.get_end_iter(),
            False
            )

        res = {}

        for i in SYMBOL_REGEXP.finditer(t):

            line = b.get_iter_at_offset(i.start()).get_line()
            s = b.get_iter_at_line(line)
            e = b.get_iter_at_offset(i.end())

            t2 = b.get_text(s, e, False)

            res[line] = t2

        for i in sorted(list(res.keys())):
            m.append([str(i + 1), res[i]])

        if val is not None:
            vscrl = o_sw.get_vscrollbar()
            if vscrl:
                GLib.idle_add(self._restore_vscroll, vscrl, val)

        return

    def _restore_vscroll(self, vscrl, val):
        vscrl.set_value(val)
        return


class SourceCompletionProvider(
        GObject.GObject,
        GtkSource.CompletionProvider
        ):

    def __init__(self):
        super().__init__()
        print("__init__")
        return

    def do_get_name(self):
        print("get_name")
        return "Python Completion Provider"

    def do_get_icon(self):
        print("get_icon")
        return None

    def do_populate(self, context):
        print("populate")
        p1 = GtkSource.CompletionItem.new('label1', '111', None, None)
        p2 = GtkSource.CompletionItem.new('label2', '222', None, None)
        p3 = GtkSource.CompletionItem.new('label3', '333', None, None)
        context.add_proposals(self, [p1, p2, p3], True)
        return

    def do_get_activation(self):
        print("activation")
        return GtkSource.CompletionActivation.USER_REQUESTED

    def do_match(self, context):
        print("match")
        # itera = context.get_iter()
        return True

    # def do_get_info_widget(self, proposal):
    #    return

    def do_update_info(self, proposal, info):
        print("update_info: {}, {}".format(proposal, info))
        return

    # def do_get_start_iter(self, context, proposal, itera):
    #    return

    # def do_activate_proposal(self, proposal, iter):
    #    return

    def do_get_interactive_delay(self):
        return -1

    # def do_get_priority(self):
    #     return 0


class ModeInterface:

    def __init__(self, main_window):
        self.main_window = main_window

        self.source_menu = SourceMenu(self)
        self.view = View(self)

        self.outline = Outline(self)

        self.lang_mgr = GtkSource.LanguageManager.get_default()

        #self.completion = self.view.get_view_widget().get_completion()
        #self.completion_provider = SourceCompletionProvider()
        #res = self.completion.add_provider(self.completion_provider)
        #print("add_provider: {}".format(res))

        # self.completion.create_context(None)
        return

    def destroy(self):
        self.source_menu.destroy()
        self.view.destroy()
        return

    def get_menu(self):
        return self.source_menu.get_widget()

    def get_menu_name(self):
        return "Python"

    def get_view_widget(self):
        return self.view.get_view_widget()

    def get_view_widget_sw(self):
        return self.view.get_view_widget_sw()

    def get_widget(self):
        return self.view.get_widget()

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

    def get_view(self):
        return self.view


def indent(txt, de=False):
    lines = txt.splitlines()
    if not de:
        for i in range(len(lines)):
            if lines[i] != '':
                lines[i] = '    {}'.format(lines[i])
    else:
        can_dedent = True
        for i in lines:
            if not i.startswith('    ') and not i == '':
                can_dedent = False
                break
        if can_dedent:
            for i in range(len(lines)):
                if lines[i] != '':
                    lines[i] = lines[i][4:]

    return '\n'.join(lines)
