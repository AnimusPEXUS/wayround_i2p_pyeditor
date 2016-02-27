
import os.path
import logging
import importlib
import importlib.util
import modulefinder
import fnmatch
import collections

import mimetypes

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GtkSource
from gi.repository import Pango

import wayround_org.utils.gtk
import wayround_org.utils.path

import wayround_org.pyeditor.buffer_clip
import wayround_org.pyeditor.config
import wayround_org.pyeditor.main_menu
import wayround_org.pyeditor.project_clip
import wayround_org.pyeditor.project_menu
import wayround_org.pyeditor.modes.dummy


class MainWindow:

    def __init__(self):

        self.cfg = wayround_org.pyeditor.config.Config(self)
        self.cfg.load()

        self.mode_interface = None
        self.current_buffer = None
        self.projects = wayround_org.pyeditor.project_clip.ProjectClip(self)
        self.projects.connect('list-changed', self.on_projects_list_changed)
        self.open_projects = []

        self.accel_group = Gtk.AccelGroup()

        window = Gtk.Window()
        window.set_title("PyEditor")
        window.add_accel_group(self.accel_group)
        window.set_hide_titlebar_when_maximized(True)
        window.connect('delete-event', self.on_delete)

        self.main_menu = wayround_org.pyeditor.main_menu.MainMenu(self)
        buffer_clip = wayround_org.pyeditor.buffer_clip.BufferClip(self)
        buffer_clip.connect(
            'list-changed-edit', self.on_buffer_clip_list_changed_edit
            )
        buffer_clip.connect(
            'list-changed-rm', self.on_buffer_clip_list_changed_rm
            )
        buffer_clip.connect(
            'list-changed-add', self.on_buffer_clip_list_changed_add
            )
        self.buffer_clip = buffer_clip

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        menu_bar = self.main_menu.get_widget()

        self.source_widget = None
        self.source_view = None
        self.source_view_sw = None

        buffer_listview = Gtk.TreeView()
        buffer_listview_sw = Gtk.ScrolledWindow()
        buffer_listview_sw.set_overlay_scrolling(False)
        buffer_listview_sw.add(buffer_listview)
        buffer_listview.set_activate_on_single_click(True)
        # buffer_listview.set_headers_visible(False)
        self.buffer_listview = buffer_listview
        buffer_listview.set_model(
            Gtk.ListStore(
                str,
                # corresponding buffer instance id (integer converted to str)
                # as Python id(object) result is too large for int
                str,  # project
                str,  # filebasename
                str,  # modified?
                str,  # subdir in project
                str  # real path
                )
            )
        m = buffer_listview.get_model()
        m.set_sort_func(1, buffer_list_sorter1, None)
        m.set_sort_func(2, buffer_list_sorter2, None)
        del(m)

        buffer_listview.connect(
            'row-activated',
            self.on_buffer_listview_row_activated
            )

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 1)
        _c.set_title('Project')
        _c.set_sort_column_id(1)
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 2)
        _c.set_title('Name')
        _c.set_sort_column_id(1)
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 3)
        _c.set_title('Changed?')
        _c.set_sort_column_id(2)
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 4)
        _c.set_title('Display Path')
        _c.set_sort_column_id(1)
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _c.set_visible(False)
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 5)
        _c.set_title('Path')
        buffer_listview.append_column(_c)

        projects_listview = Gtk.TreeView()
        self.projects_listview = projects_listview
        # projects_listview.set_headers_visible(False)
        projects_listview.set_model(Gtk.ListStore(str))
        projects_listview.connect(
            'row-activated',
            self.on_projects_listview_row_activated
            )

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 0)
        _c.set_title('Name')
        projects_listview.append_column(_c)

        project_treeview = wayround_org.utils.gtk.DirectoryTreeView()
        self.project_treeview = project_treeview
        project_treeview.connect(
            'row-activated',
            self.on_project_treeview_row_activated
            )

        paned_v = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        # paned_v.set_property('handle-size', 5)
        self.paned_v = paned_v
        paned_h1 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.paned_h1 = paned_h1

        projects_notebook = Gtk.Notebook()
        self.projects_notebook = projects_notebook

        projects_listview_sw = Gtk.ScrolledWindow()
        projects_listview_sw.set_overlay_scrolling(False)
        projects_listview_sw.add(projects_listview)

        projects_notebook.append_page(
            projects_listview_sw,
            Gtk.Label("Projects")
            )

        project_treeview_sw = Gtk.ScrolledWindow()
        project_treeview_sw.set_overlay_scrolling(False)
        project_treeview_sw.add(project_treeview)

        self.project_label = Gtk.Label("Dbl. click one of projects")

        projects_notebook.append_page(
            project_treeview_sw,
            self.project_label
            )

        projects_notebook.child_set_property(
            projects_listview_sw,
            'tab-expand',
            False
            )

        projects_notebook.child_set_property(
            project_treeview_sw,
            'tab-expand',
            True
            )

        self.project_menu = wayround_org.pyeditor.project_menu.ProjectMenu(
            self,
            self.project_treeview
            )

        self.project_treeview.connect(
            'button-press-event',
            self.on_project_treeview_button_press_event
            )

        # buffer_listview_sw_f = Gtk.Frame()
        # buffer_listview_sw_f.add(buffer_listview_sw)

        # projects_notebook_f = Gtk.Frame()
        # projects_notebook_f.add(projects_notebook)

        projects_notebook_sw = Gtk.ScrolledWindow()
        projects_notebook_sw.set_overlay_scrolling(False)
        projects_notebook_sw.add(projects_notebook)

        paned_v.add1(buffer_listview_sw)
        paned_v.add2(projects_notebook_sw)

        paned_h1.add1(paned_v)

        b.pack_start(menu_bar, False, False, 0)
        b.pack_start(paned_h1, True, True, 0)

        window.add(b)

        mxzd = self.cfg.cfg.get('general', 'maximized', fallback=True)

        w = self.cfg.cfg.getint('general', 'width', fallback=640)
        h = self.cfg.cfg.getint('general', 'height', fallback=480)

        p1_pos = self.cfg.cfg.getint('general', 'paned1_pos', fallback=-100)

        paned_v.set_position(p1_pos)

        p2_pos = self.cfg.cfg.getint('general', 'paned2_pos', fallback=100)

        paned_h1.set_position(p2_pos)

        # print('mxzd {}, w {}, h {}'.format(mxzd, w, h))

        if not mxzd:
            window.unmaximize()

        window.resize(w, h)

        if mxzd:
            window.maximize()

        self._window = window

        return

    def get_widget(self):
        return self._window

    def show(self):
        self.get_widget().show_all()
        return

    def destroy(self):
        self.main_menu.destroy()
        return

    def set_view_widget(self, source_widget, view_widget, view_widget_sw=None):
        self.source_widget = source_widget
        self.source_view = view_widget
        self.source_view_sw = view_widget_sw

        self.paned_h1.add2(source_widget)
        source_widget.show_all()
        return

    def open_file(
            self,
            filename,
            set_buff=True,
            force_mode=None
            ):
        ret = 0

        filename = wayround_org.utils.path.realpath(filename)
        # print("filename: {}".format(filename))

        mode = MODES['dummy']

        if not force_mode:

            file_mime = mimetypes.guess_type(filename)

            if file_mime in MODES_MIME_MAP:
                len_MODES_MIME_MAP_fm = len(MODES_MIME_MAP[file_mime])

                if len_MODES_MIME_MAP_fm == 0:
                    pass
                elif len_MODES_MIME_MAP_fm == 1:
                    mode = MODES_MIME_MAP[file_mime][
                        list(MODES_MIME_MAP[file_mime].keys())[0]
                        ]
                else:
                    # TODO: create mode selection dialog
                    pass

            # print("mode by mime: {}".format(mode))

            # if mode not found by mume type, try find it by filemask
            if mode == MODES['dummy']:
                acceptable_mode_mods = []
                for i in MODES_FNM_MAP.keys():
                    if fnmatch.fnmatch(os.path.basename(filename), i):
                        len_MODES_FNM_MAP_fm = len(MODES_FNM_MAP[i])

                        if len_MODES_FNM_MAP_fm == 0:
                            pass
                        elif len_MODES_FNM_MAP_fm == 1:
                            mode = MODES_FNM_MAP[i][
                                list(MODES_FNM_MAP[i].keys())[0]
                                ]
                            break
                        else:
                            # TODO: create mode selection dialog
                            pass

            # print("mode by fm: {}".format(mode))

        else:
            try:
                mode = MODES[force_mode]
            except:
                logging.exception("error setting mode `{}'".format(force_mode))
                ret = 2

        if mode == MODES['dummy']:
            d = Gtk.MessageDialog(
                self.get_widget(),
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Can't find suitable mode for file\n`{}'\n({})".format(
                    filename,
                    file_mime
                    )
                )
            d.run()
            d.destroy()
            ret = 1

        if ret == 0:

            buff = mode.Buffer(self)
            buff.open(filename)

            self.buffer_clip.add(buff)

            if set_buff:
                self.set_buffer(buff)

            ret = buff

        return ret

    def close_buffer(self, buff):

        ret = 0

        if buff in self.buffer_clip.buffers:

            if hasattr(buff, 'get_modified') and buff.get_modified() == True:
                d = Gtk.MessageDialog(
                    self.get_widget(),
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.YES_NO,
                    "Buffer with Text for `{}' is not saved\n"
                    "Close this Buffer Anyway?".format(buff.get_title())
                    )
                res = d.run()
                d.destroy()
                if res == Gtk.ResponseType.YES:
                    ret = 0
                else:
                    ret = 1

        else:
            ret = 2

        if ret == 0:

            if buff == self.current_buffer:
                self.set_buffer(None)

            self.buffer_clip.remove(buff)
            buff.destroy()

        return

    def close_current_buffer(self):

        if (self.current_buffer is not None
                and self.current_buffer in self.buffer_clip.buffers):

            self.close_buffer(self.current_buffer)

        return

    def install_mode(self, name=None, cls=None):

        if name is not None:
            mod = load_mode(name)
            if isinstance(mod, int):
                logging.error("Can't load module")
            else:
                self.install_mode(cls=mod.ModeInterface)

        elif cls is not None:

            if not isinstance(self.mode_interface, cls):

                if self.mode_interface is not None:
                    self.mode_interface.destroy()

                mi = cls(self)

                self.mode_interface = mi

                menu = mi.get_menu()
                menu.show_all()

                self.main_menu.source_mi.set_submenu(menu)

                self.main_menu.source_mi.set_label(mi.get_menu_name())

                self.set_view_widget(
                    mi.get_widget(),
                    mi.get_view_widget(),
                    mi.get_view_widget_sw()
                    )

        return

    def set_buffer(self, buff):

        if buff is None or buff not in self.buffer_clip.buffers:
            self._window.set_title("PyEditor")

            if self.current_buffer is not None:
                self.current_buffer.save_state()

            self.install_mode('dummy')
            self.current_buffer = None
            self.select_current_buffer_in_list()

        else:

            if self.current_buffer is not None:
                self.current_buffer.save_state()

            self.install_mode(cls=buff.get_mode_interface())

            self.mode_interface.set_buffer(buff)

            self.current_buffer = buff

            self.select_current_buffer_in_list()

            self.current_buffer.restore_state()

            self._window.set_title(
                "{} - PyEditor".format(buff.get_title())
                )
        return

    def select_current_buffer_in_list(self):

        opened_index = -1

        buf_id = id(self.current_buffer)

        mod = self.buffer_listview.get_model()

        iter_ = None

        chi = mod.get_iter_first()

        if chi:
            while True:

                if int(mod[chi][0]) == buf_id:
                    iter_ = chi
                    break

                chi = mod.iter_next(chi)

                if not chi:
                    break

        if iter_ is not None:
            self.buffer_listview.get_selection().select_iter(iter_)

        return

    def signal_settings_changed(self):
        if hasattr(
                self.mode_interface, 'settings_changed'
                ):
            self.mode_interface.settings_changed()
        return

    def get_fixed_text_editor_font_desc(self):
        try:
            ret = self.cfg.cfg.get('general', 'fixed_text_editor_font_desc')
        except:
            ret = "Clean 9"
        return ret

    def set_fixed_text_editor_font_desc(self, desc):
        self.cfg.cfg.set('general', 'fixed_text_editor_font_desc', desc)
        self.cfg.save()
        self.signal_settings_changed()
        return

    def on_delete(self, widget, event):

        found_not_saved = False
        close_anyway = False
        ret = True

        for buff in self.buffer_clip.buffers:

            if hasattr(buff, 'get_modified') and buff.get_modified() == True:
                found_not_saved = True

        if found_not_saved:
            d = Gtk.MessageDialog(
                self.get_widget(),
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                "Not Saved Buffers found.\n"
                "Continue closing PyEditor?"
                )
            res = d.run()
            d.destroy()
            close_anyway = res == Gtk.ResponseType.YES

        if not found_not_saved or (found_not_saved and close_anyway):

            self.install_mode('dummy')

            self.cfg.cfg.set(
                'general',
                'maximized',
                str(self._window.is_maximized())
                )
            ws = self._window.get_size()
            self.cfg.cfg.set('general', 'width', str(ws[0]))
            self.cfg.cfg.set('general', 'height', str(ws[1]))

            self.cfg.cfg.set(
                'general',
                'paned1_pos',
                str(self.paned_v.get_position())
                )

            self.cfg.cfg.set(
                'general',
                'paned2_pos',
                str(self.paned_h1.get_position())
                )

            self.destroy()

            self.buffer_clip.save_config()
            Gtk.main_quit()
            ret = False
        return ret

    def on_buffer_clip_list_changed_add(self, widget, tup):

        id_, buff = tup
        m = self.buffer_listview.get_model()

        proj_dict = self.projects.get_dict()

        b_filename = wayround_org.utils.path.realpath(buff.get_filename())

        proj_name = ''

        for j, k in proj_dict.items():
            k_plus_slash = wayround_org.utils.path.realpath(k) + '/'
            if b_filename.startswith(k_plus_slash):
                proj_name = j
                break

        disp_file_path = b_filename

        if proj_name != '':
            disp_file_path = os.path.dirname(
                wayround_org.utils.path.relpath(
                    b_filename,
                    wayround_org.utils.path.realpath(proj_dict[proj_name])
                    )
                )

        m.append(
            [
                str(id_),
                proj_name,
                buff.get_title(),
                str(buff.get_modified()),
                disp_file_path,
                b_filename
                ]
            )
        return

    def on_buffer_clip_list_changed_edit(self, widget, tup):
        id_, buff = tup
        m = self.buffer_listview.get_model()

        b_filename = wayround_org.utils.path.realpath(buff.get_filename())

        proj_dict = self.projects.get_dict()

        proj_name = ''

        for j, k in proj_dict.items():
            k_plus_slash = wayround_org.utils.path.realpath(k) + '/'
            if b_filename.startswith(k_plus_slash):
                proj_name = j
                break

        chi = m.get_iter_first()
        if chi:
            while True:

                if int(m[chi][0]) == id_:
                    m.set_value(chi, 1, proj_name)
                    m.set_value(chi, 2, buff.get_title())
                    m.set_value(chi, 3, str(buff.get_modified()))

                chi = m.iter_next(chi)

                if chi in (False, None):
                    break

        return

    def on_buffer_clip_list_changed_rm(self, widget, tup):
        id_ = tup[0]
        m = self.buffer_listview.get_model()

        chi = m.get_iter_first()
        res = True

        if chi:
            while True:

                if int(m[chi][0]) == id_:
                    m.remove(chi)
                    break

                chi = m.iter_next(chi)

                if chi in (False, None):
                    break

        # while chi is not None and res is not False:
        #    res = m.remove(chi)
        return

    def on_projects_list_changed(self, widget):
        m = self.projects_listview.get_model()

        chi = m.get_iter_first()
        res = True

        while chi is not None and res is not False:
            res = m.remove(chi)

        lst = widget.get_list()

        for i in lst:
            m.append([i])

        return

    def on_buffer_listview_row_activated(self, widget, path, column):

        sel = widget.get_selection()
        model, iter_ = sel.get_selected()

        buf_id = int(model[iter_][0])

        buf = None
        for i in self.buffer_clip.buffers:
            if id(i) == buf_id:
                buf = i

        if buf is not None:
            self.set_buffer(buf)

            if self.source_view is not None:
                self.source_view.grab_focus()
        return

    def on_projects_listview_row_activated(self, widget, path, column):

        m = self.projects_listview.get_model()
        name = m[path][0]

        path = self.projects.get(name)
        self.project_treeview.set_root_directory(path)

        self.project_label.set_text(name)

        self.projects_notebook.set_current_page(1)

        return

    def on_project_treeview_row_activated(self, widget, path, column):
        pth = self.project_treeview.convert_indices_to_path(path.get_indices())
        fpth = wayround_org.utils.path.join(
            self.project_treeview.get_root_directory(),
            pth
            )

        if os.path.isfile(fpth):
            self.open_file(fpth)

        if self.source_view is not None:
            self.source_view.grab_focus()
        return

    def on_project_treeview_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.project_menu.get_widget().popup(
                None, None, None, None, event.button, event.time
                )


def load_mode(name='dummy'):

    ret = 0

    if not isinstance(name, str):
        raise TypeError("`name' must be str")

    try:
        mod = importlib.import_module(
            'wayround_org.pyeditor.modes.{}'.format(name)
            )
    except:
        logging.exception("Can't load module `{}'".format(name))
        ret = 1
    else:
        ret = mod
    return ret


def find_modes():
    mf = modulefinder.ModuleFinder()
    ret = list(mf.find_all_submodules(wayround_org.pyeditor.modes))
    if 'text_plain' in ret:
        text_plain_pos = ret.index('text_plain')
        ret = ret[:text_plain_pos] + ret[text_plain_pos + 1:] + ['text_plain']
    # print("{}".format(ret))
    return ret


def create_module_map():

    ret = None, None, None

    mime_map = collections.OrderedDict()
    ext_map = collections.OrderedDict()
    modules = collections.OrderedDict()

    modes = find_modes()

    for i in modes:

        try:

            mod = importlib.import_module(
                'wayround_org.pyeditor.modes.{}'.format(i)
                )

        except:
            logging.exception("error loading mode module or package")
        else:

            if not hasattr(mod, 'SUPPORTED_MIME'):
                logging.error(
                    "mode module `{}' has not SUPPORTED_MIME attr".format(
                        mod
                        )
                    )
            else:

                for j in mod.SUPPORTED_MIME:
                    if not j in mime_map:
                        mime_map[j] = {}

                    if not mod in mime_map[j]:
                        mime_map[j][i] = mod

                modules[i] = mod

            if not hasattr(mod, 'SUPPORTED_FNM'):
                logging.error(
                    "mode module `{}' has not SUPPORTED_FNM attr".format(
                        mod
                        )
                    )
            else:

                for j in mod.SUPPORTED_FNM:
                    if not j in ext_map:
                        ext_map[j] = {}

                    if not mod in ext_map[j]:
                        ext_map[j][i] = mod

                modules[i] = mod

    ret = modules, mime_map, ext_map

    return ret


def buffer_list_sorter1(model, row1, row2, user_data):
    val11 = model[row1][1]
    val12 = model[row2][1]
    # print('val11: {}'.format(val11))
    # print('val12: {}'.format(val12))
    if val11 < val12:
        ret = -1
    elif val11 > val12:
        ret = 1
    else:
        val41 = model[row1][4]
        val42 = model[row2][4]
        # print('val21: {}'.format(val21))
        # print('val22: {}'.format(val22))
        if val41 < val42:
            ret = -1
        elif val41 > val42:
            ret = 1
        else:
            val21 = model[row1][2]
            val22 = model[row2][2]
            # print('val21: {}'.format(val21))
            # print('val22: {}'.format(val22))
            if val21 < val22:
                ret = -1
            elif val21 > val22:
                ret = 1
            else:
                ret = 0
    return ret


def buffer_list_sorter2(model, row1, row2, user_data):
    val31 = model[row1][3] == 'True'
    val32 = model[row2][3] == 'True'
    if val31 and not val32:
        ret = 1
    elif not val31 and val32:
        ret = -1
    else:
        ret = 0
    return ret

MODES, MODES_MIME_MAP, MODES_FNM_MAP = create_module_map()

# print("{}\n\n{}\n\n{}\n\n".format(MODES, MODES_MIME_MAP, MODES_FNM_MAP))
