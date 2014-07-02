
import json
import collections

from gi.repository import GObject

import org.wayround.pyeditor.buffer
import org.wayround.utils.path


class BufferClip(GObject.GObject):

    __gsignals__ = {
        'list-changed': (GObject.SIGNAL_RUN_FIRST, None, tuple())
    }

    def __init__(self, main_window):

        self.buffers = []
        self.main_window = main_window

        super().__init__()

        return

    def add(self, buff):

        if not isinstance(buff, org.wayround.pyeditor.buffer.Buffer):
            raise Exception(
                "`buff' must be an instance of "
                "org.wayround.pyeditor.buffer.Buffer"
                )

        self.buffers.append(buff)

        self.buffers.sort(key=lambda x: x.get_filename())

        self.save_config()

        buff.connect('changed', self.on_buffer_changed)

        self.emit('list-changed')

        return

    def remove(self, buff):

        if not isinstance(buff, org.wayround.pyeditor.buffer.Buffer):
            raise Exception(
                "`buff' must be an instance of "
                "org.wayround.pyeditor.buffer.Buffer"
                )

        ret = 0

        if buff in self.buffers:
            del self.buffers[self.buffers.index(buff)]
            buff.destroy()
            self.save_config()
            self.emit('list-changed')

        return ret

    def save_config(self):

        cfg = collections.OrderedDict()

        for i in self.buffers:

            setting_name = org.wayround.utils.path.realpath(i.get_filename())

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

            for i in list(cfg.keys()):
                res = self.main_window.open_file(i, False)

                if res != 1:
                    res.set_config(cfg[i])

        return

    def on_buffer_changed(self, widg):
        self.emit('list-changed')
        return
