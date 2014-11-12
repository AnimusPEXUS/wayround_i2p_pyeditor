
import os.path
import logging
import importlib
import importlib.util
import modulefinder
import fnmatch

import magic

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GtkSource
from gi.repository import Pango

import org.wayround.utils.gtk
import org.wayround.utils.path

import org.wayround.pyeditor.buffer_clip
import org.wayround.pyeditor.config
import org.wayround.pyeditor.main_menu
import org.wayround.pyeditor.project_clip
import org.wayround.pyeditor.project_menu
import org.wayround.pyeditor.modes.dummy


class MainWindow:

    def __init__(self):

        self.cfg = org.wayround.pyeditor.config.Config(self)
        self.cfg.load()

        self.mode_interface = None
        self.current_buffer = None
        self.projects = org.wayround.pyeditor.project_clip.ProjectClip(self)
        self.projects.connect('list-changed', self.on_projects_list_changed)
        self.open_projects = []

        self.accel_group = Gtk.AccelGroup()

        window = Gtk.Window()
        window.add_accel_group(self.accel_group)
        window.connect('delete-event', self.on_delete)

        self.main_menu = org.wayround.pyeditor.main_menu.MainMenu(self)
        buffer_clip = org.wayround.pyeditor.buffer_clip.BufferClip(self)
        buffer_clip.connect('list-changed', self.on_buffer_clip_list_changed)
        self.buffer_clip = buffer_clip

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        menu_bar = self.main_menu.get_widget()

        self.source_widget = None
        self.source_view = None
        self.source_view_sw = None

        buffer_listview = Gtk.TreeView()
        buffer_listview_sw = Gtk.ScrolledWindow()
        buffer_listview_sw.add(buffer_listview)
        buffer_listview.set_activate_on_single_click(True)
        buffer_listview.set_headers_visible(False)
        self.buffer_listview = buffer_listview
        buffer_listview.set_model(
            Gtk.ListStore(
                str,
                str,
                str,
                str,
                str
                )
            )

        buffer_listview.connect(
            'row-activated',
            self.on_buffer_listview_row_activated
            )

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 0)
        # _c.set_title('Project')
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 1)
        # _c.set_title('Name')
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 2)
        # _c.set_title('Changed')
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 3)
        # _c.set_title('Display Path')
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _c.set_visible(False)
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 4)
        # _c.set_title('RealPath')
        buffer_listview.append_column(_c)

        projects_listview = Gtk.TreeView()
        self.projects_listview = projects_listview
        projects_listview.set_headers_visible(False)
        projects_listview.set_model(Gtk.ListStore(str))
        projects_listview.connect(
            'row-activated',
            self.on_projects_listview_row_activated
            )

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 0)
        # _c.set_title('Name')
        projects_listview.append_column(_c)

        project_treeview = org.wayround.utils.gtk.DirectoryTreeView()
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
        projects_listview_sw.add(projects_listview)

        projects_notebook.append_page(
            projects_listview_sw,
            Gtk.Label("Projects")
            )

        project_treeview_sw = Gtk.ScrolledWindow()
        project_treeview_sw.add(project_treeview)

        self.project_label = Gtk.Label("Project")

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

        self.project_menu = org.wayround.pyeditor.project_menu.ProjectMenu(
            self,
            self.project_treeview
            )

        self.project_treeview.connect(
            'button-press-event',
            self.on_project_treeview_button_press_event
            )

        buffer_listview_sw_f = Gtk.Frame()
        buffer_listview_sw_f.add(buffer_listview_sw)

        projects_notebook_f = Gtk.Frame()
        projects_notebook_f.add(projects_notebook)

        paned_v.add1(buffer_listview_sw_f)
        paned_v.add2(projects_notebook_f)

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

        filename = org.wayround.utils.path.realpath(filename)

        mode = MODES['dummy']

        if not force_mode:

            with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
                file_mime = m.id_filename(filename)

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

            if mode == MODES['dummy']:
                acceptable_mode_mods = []
                for i in MODES_FNM_MAP.keys():
                    if fnmatch.fnmatch(filename, i):
                        len_MODES_FNM_MAP_fm = len(MODES_FNM_MAP[i])

                        if len_MODES_FNM_MAP_fm == 0:
                            pass
                        elif len_MODES_FNM_MAP_fm == 1:
                            mode = MODES_FNM_MAP[i][
                                list(MODES_FNM_MAP[i].keys())[0]
                                ]
                        else:
                            # TODO: create mode selection dialog
                            pass

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
        if buff in self.buffer_clip.buffers:

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
        for i in range(len(self.buffer_clip.buffers)):
            if self.buffer_clip.buffers[i] == self.current_buffer:
                opened_index = i

        if opened_index != -1:
            self.buffer_listview.get_selection().select_path(
                Gtk.TreePath([opened_index])
                )
        return

    def on_delete(self, widget, event):

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
        return Gtk.main_quit()

    def on_buffer_clip_list_changed(self, widget):
        m = self.buffer_listview.get_model()

        chi = m.get_iter_first()
        res = True

        while chi is not None and res is not False:
            res = m.remove(chi)

        proj_dict = self.projects.get_dict()

        for i in self.buffer_clip.buffers:

            b_filename = org.wayround.utils.path.realpath(i.get_filename())

            proj_name = ''

            for j, k in proj_dict.items():
                k_plus_slash = org.wayround.utils.path.realpath(k) + '/'
                # print("k_plus_slash == {}".format(k_plus_slash))
                # print(" ? {}".format(b_filename))
                if b_filename.startswith(k_plus_slash):
                    proj_name = j
                    # print("    proj_name == {}".format(proj_name))
                    break

            disp_file_path = b_filename

            if proj_name != '':
                disp_file_path = os.path.dirname(
                    org.wayround.utils.path.relpath(
                        b_filename,
                        org.wayround.utils.path.realpath(proj_dict[proj_name])
                        )
                    )

            m.append(
                [
                    proj_name,
                    i.get_title(),
                    str(i.get_modified()),
                    disp_file_path,
                    b_filename
                    ]
                )

        self.select_current_buffer_in_list()

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
        ind = path.get_indices()
        self.set_buffer(self.buffer_clip.buffers[ind[0]])
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
        fpth = org.wayround.utils.path.join(
            self.project_treeview.get_root_directory(),
            pth
            )

        if os.path.isfile(fpth):
            self.open_file(fpth)
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
            'org.wayround.pyeditor.modes.{}'.format(name)
            )
    except:
        logging.exception("Can't load module `{}'".format(name))
        ret = 1
    else:
        ret = mod
    return ret


def find_modes():
    mf = modulefinder.ModuleFinder()
    return list(mf.find_all_submodules(org.wayround.pyeditor.modes))


def create_module_map():

    ret = None, None, None

    mime_map = {}
    ext_map = {}
    modules = {}

    modes = find_modes()

    for i in modes:

        try:

            mod = importlib.import_module(
                'org.wayround.pyeditor.modes.{}'.format(i)
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


MODES, MODES_MIME_MAP, MODES_FNM_MAP = create_module_map()
