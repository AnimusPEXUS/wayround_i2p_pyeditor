
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
import wayround_org.pyeditor.module_commons


MODE_NAME = 'cython'

SUPPORTED_MIME = []

SUPPORTED_FNM = ['*.pyx']

SYMBOL_REGEXP = re.compile(
    r'^[ \t]*(cdef| def |class )(.|\n)*?\s*:[ \t]*$',
    flags=re.M
    )

# SYMBOL2_REGEXP = re.compile(
#     r'^([ \t]*[a-zA-Z_][a-zA-Z0-9_\.]*?)[ \t]*\=.*$',
#     flags=re.M
#     )


class Buffer(wayround_org.pyeditor.module_commons.Buffer):

    @staticmethod
    def get_mode_interface():
        return ModeInterface


class View(wayround_org.pyeditor.module_commons.View):

    @staticmethod
    def get_language_name():
        return MODE_NAME

    def apply_spec_view_settings(self):
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
        source_pep8_mi.set_no_show_all(True)
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

        edit_delete_trailing_whitespace_mi = Gtk.MenuItem.new_with_label(
            "Delete Trailing Whitespace"
            )
        edit_delete_trailing_whitespace_mi.add_accelerator(
            'activate',
            main_window.accel_group,
            Gdk.KEY_F,
            Gdk.ModifierType.CONTROL_MASK
            | Gdk.ModifierType.SHIFT_MASK
            | Gdk.ModifierType.MOD1_MASK,
            Gtk.AccelFlags.VISIBLE
            )
        edit_delete_trailing_whitespace_mi.connect(
            'activate',
            self.on_delete_trailing_whitespace_mi
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
        source_me.append(edit_delete_trailing_whitespace_mi)
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
                        ['--aggressive', 
                         '--ignore', 'E123,E721', 
                         #'--ignore', '', 
                         ''
                        ]
                        )
                    )

                b.set_text(t)

                buff.restore_state()

        return

    def on_edit_delete_line_mi(self, mi):
        b = self.main_window.current_buffer.get_buffer()
        wayround_org.pyeditor.module_commons.delete_selected_lines(b)
        return

    def on_navigate_refresh_outline_mi(self, mi):
        mi = self.main_window.mode_interface
        if mi is not None and hasattr(mi, 'outline'):
            mi.outline.reload()
        return

    def _get_selected_lines(self):
        b = self.main_window.current_buffer.get_buffer()
        return wayround_org.pyeditor.module_commons.get_selected_lines(b)

    def on_indent_mi(self, mi, de=False):
        b = self.main_window.current_buffer.get_buffer()
        wayround_org.pyeditor.module_commons.indent_buffer(b, de, 4)
        return

    def on_delete_trailing_whitespace_mi(self, mi):
        buff = self.main_window.current_buffer
        b = buff.get_buffer()

        t = b.get_text(
            b.get_start_iter(),
            b.get_end_iter(),
            False
            )

        buff.save_state()

        t = wayround_org.pyeditor.module_commons.delete_trailing_whitespace(t)

        b.set_text(t)

        buff.restore_state()
        return


class Outline(wayround_org.pyeditor.module_commons.Outline):

    def search(self, buff):
        res = {}

        t = buff.get_text(
            buff.get_start_iter(),
            buff.get_end_iter(),
            False
            )

        for i in SYMBOL_REGEXP.finditer(t):

            line = buff.get_iter_at_offset(i.start()).get_line()
            s = buff.get_iter_at_line(line)
            e = buff.get_iter_at_offset(i.end())

            t2 = buff.get_text(s, e, False)

            res[line] = t2

        return res


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

    @staticmethod
    def get_menu_name():
        return "Cython"

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
                "wayround_org.pyeditor.modes.python.Buffer"
                )

        buff.set_mode_interface(self)
        buff.set_language(self.lang_mgr.get_language('python'))
        self.view.set_buffer(buff)
        self.outline.reload()
        return

    def get_view(self):
        return self.view


def indent(txt, de=False):
    return wayround_org.pyeditor.module_commons.indent_text(txt, de, 4)
