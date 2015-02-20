
import json
import collections

from gi.repository import GObject
from gi.repository import Gtk

import wayround_org.pyeditor.buffer
import wayround_org.utils.path
import wayround_org.utils.gtk


class ConfigFileListLoadingProcessWindow:

    def __init__(self):
        window = Gtk.Window()
        #window.set_default_size(300, 10)
        window.set_resizable(False)
        window.set_decorated(False)
        window.set_deletable(False)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_title("PyEditor")

        prog_bar = Gtk.ProgressBar()
        # prog_bar.set_margin_top(10)
        # prog_bar.set_margin_bottom(10)
        # prog_bar.set_margin_start(10)
        # prog_bar.set_margin_end(10)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_spacing(5)

        l = Gtk.Label("loading buffers.. please wait.")
        l.set_alignment(0, 0.5)

        b.pack_start(l, False, False, 0)
        b.pack_start(prog_bar, False, False, 0)

        window.add(b)

        self._window = window
        self._prog_bar = prog_bar
        return

    def show(self):
        self.get_widget().show_all()
        return

    def get_widget(self):
        return self._window

    def set_fraction(self, value):
        return self._prog_bar.set_fraction(value)

    def destroy(self):
        self.get_widget().destroy()


class BufferClip(GObject.GObject):

    __gsignals__ = {
        'list-changed-add': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (object,)
            ),
        'list-changed-rm': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'list-changed-edit': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (object,)
            )
    }

    def __init__(self, main_window):

        self.buffers = []
        self.main_window = main_window

        super().__init__()

        return

    def add(self, buff):

        if not isinstance(buff, wayround_org.pyeditor.buffer.Buffer):
            raise Exception(
                "`buff' must be an instance of "
                "wayround_org.pyeditor.buffer.Buffer"
                )

        self.buffers.append(buff)

        self.buffers.sort(key=lambda x: x.get_filename())

        self.save_config()

        buff.connect('changed', self.on_buffer_changed_edit)

        self.emit('list-changed-add', (id(buff), buff,))

        return

    def remove(self, buff):

        if not isinstance(buff, wayround_org.pyeditor.buffer.Buffer):
            raise Exception(
                "`buff' must be an instance of "
                "wayround_org.pyeditor.buffer.Buffer"
                )

        ret = 0

        if buff in self.buffers:
            buff_id = id(buff)
            del self.buffers[self.buffers.index(buff)]
            buff.destroy()
            self.save_config()
            self.emit('list-changed-rm', (buff_id,))

        return ret

    def save_config(self):

        cfg = collections.OrderedDict()

        for i in self.buffers:

            setting_name = wayround_org.utils.path.realpath(i.get_filename())

            cfg[setting_name] = i.get_config()

        if 'buffer_settings' not in self.main_window.cfg.cfg.sections():
            self.main_window.cfg.cfg.add_section('buffer_settings')

        self.main_window.cfg.cfg.set(
            'buffer_settings',
            'buffer_state',
            json.dumps(list(cfg.items()))
            )

        self.main_window.cfg.save()

        return

    def load_config(self):

        cfg = self.main_window.cfg.cfg.get(
            'buffer_settings',
            'buffer_state',
            fallback=None
            )

        if cfg is not None:

            cfg = collections.OrderedDict(json.loads(cfg))

            lck = list(cfg.keys())
            lck_l = len(lck)

            pw = ConfigFileListLoadingProcessWindow()
            pw.set_fraction(0)
            pw.show()

            for ii in range(lck_l):
                i = lck[ii]
                res = self.main_window.open_file(i, False)

                if res != 1:
                    res.set_config(cfg[i])

                if ii == 0:
                    pw.set_fraction(0)
                else:
                    pw.set_fraction(1.0 / (lck_l / ii))
                wayround_org.utils.gtk.process_events()

            pw.set_fraction(1)
            wayround_org.utils.gtk.process_events()
            pw.destroy()

        return

    def on_buffer_changed_edit(self, widg):
        self.emit('list-changed-edit', (id(widg), widg,))
        return
