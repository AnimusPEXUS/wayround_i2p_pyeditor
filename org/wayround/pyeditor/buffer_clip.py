
import collections

from gi.repository import GtkSource
from gi.repository import GObject

import org.wayround.pyeditor.buffer


class BufferClip(GObject.GObject):

    __gsignals__ = {
        'list-changed': (GObject.SIGNAL_RUN_FIRST, None, tuple())
    }

    def __init__(self, main_window):

        self.buffers = collections.OrderedDict()
        self.main_window = main_window

        return

    def add(self, name, buff=None):

        if buff is None:
            buff = GtkSource.Buffer()
        else:
            if not isinstance(buff, org.wayround.pyeditor.buffer.Buffer):
                raise TypeError("`buff' must be None or buffer.Buffer")

        if self.rm(name) == 0:
            self.buffers[name] = buff
            self.emit('list-changed')

        return

    def rm(self, name):
        ret = 0
        if name in self.buffers:
            self.buffers[name].destroy()
            del self.buffers[name]
            self.emit('list-changed')
        return ret

    def set(self, name):
        ret = 0
        if name not in self.buffers:
            ret = 1
        else:
            self.main_window.source_view.set_buffer(self.buffers[name])
        return ret

    def list(self):
        return list(self.buffers.keys())
