
import os.path
import logging
import importlib

from gi.repository import Gtk
from gi.repository import GtkSource

import org.wayround.utils.gtk

import org.wayround.pyeditor.buffer_clip
import org.wayround.pyeditor.config
import org.wayround.pyeditor.main_menu
import org.wayround.pyeditor.project_clip
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

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        menu_bar = self.main_menu.get_widget()

        source_view = None
        self.source_view = source_view

        buffer_listview = Gtk.TreeView()
        buffer_listview_sw = Gtk.ScrolledWindow()
        buffer_listview_sw.add(buffer_listview)
        buffer_listview.set_activate_on_single_click(True)
        buffer_listview.set_headers_visible(False) 
        self.buffer_listview = buffer_listview
        buffer_listview.set_model(Gtk.ListStore(str, str, str))
        buffer_listview.connect(
            'row-activated',
            self.on_buffer_listview_row_activated
            )

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 0)
        _c.set_title('Name')
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 1)
        _c.set_title('Changed')
        buffer_listview.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 2)
        _c.set_title('Path')
        buffer_listview.append_column(_c)

        projects_listview = Gtk.TreeView()
        self.projects_listview = projects_listview
        projects_listview.set_activate_on_single_click(True)
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
        _c.set_title('Name')
        projects_listview.append_column(_c)

        outline_listview = Gtk.TreeView()
        project_treeview = org.wayround.utils.gtk.DirectoryTreeView()
        self.project_treeview = project_treeview
        project_treeview.connect(
            'row-activated',
            self.on_project_treeview_row_activated
            )

        paned_v = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        self.paned_v=paned_v
        paned_h1 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.paned_h1=paned_h1
        paned_h2 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.paned_h2 = paned_h2

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
        
        self.project_label =Gtk.Label("Project") 
        
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


        paned_v.add1(buffer_listview_sw)
        paned_v.add2(projects_notebook)

        paned_h1.add1(paned_v)
        paned_h1.add2(paned_h2)

        paned_h2.add2(outline_listview)

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

        p3_pos = self.cfg.cfg.getint('general', 'paned3_pos', fallback=500)
        
        paned_h2.set_position(p3_pos)
        
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

    def set_view_widget(self, widget):
        self.source_view = widget
        self.paned_h2.add1(widget)
        widget.show_all()
        return

    def open_file(self, filename, set_buff=True):
        ret = 0

        if not os.path.isfile(filename):
            ret = 1

        if ret == 0:
            if filename.endswith('.py'):

                mode = load_mode('python')

                buff = mode.Buffer(self)
                buff.open(filename)

                self.buffer_clip.add(buff)

                if set_buff:
                    self.set_buffer(buff)
                
                ret = buff

        return ret
        
    def close_current_buffer(self):
        
        if self.current_buffer is not None:
            # TODO: add dialog on case buffer not saved
            self.buffer_clip.remove(self.current_buffer)
            self.current_buffer.destroy()
            self.current_buffer = None
            self.install_mode('dummy')
        
        return

    def install_mode(self, name=None, cls=None):

        if name is not None:
            mod = load_mode(name)
            if isinstance(mod, int):
                logging.error("Can't load module")
            else:
                self.install_mode(cls=mod.ModeInterface)

        elif cls is not None:

            if type(self.mode_interface) != cls:

                if self.mode_interface is not None:
                    self.mode_interface.destroy()

                self.mode_interface = cls(self)

                menu = self.mode_interface.get_menu()
                self.main_menu.source_mi.set_submenu(menu)

                self.set_view_widget(self.mode_interface.get_view())

        return

    def set_buffer(self, buff):
        if buff in self.buffer_clip.buffers:
            self.install_mode(cls=buff.get_mode_interface())
            self.mode_interface.set_buffer(buff)
            self.current_buffer = buff
            self.select_current_buffer_in_list()
            self._window.set_title(buff.get_title())
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

        self.cfg.cfg.set(
            'general', 
            'paned3_pos', 
            str(self.paned_h2.get_position())
            )
        
        self.buffer_clip.save_config()
        return Gtk.main_quit()

    def on_buffer_clip_list_changed(self, widget):
        m = self.buffer_listview.get_model()

        chi = m.get_iter_first()
        res = True

        while chi is not None and res is not False:
            res = m.remove(chi)

        for i in self.buffer_clip.buffers:
            m.append([i.get_title(), str(i.get_modified()), i.get_filename()])

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
