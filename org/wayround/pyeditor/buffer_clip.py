

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
            buff.destroy()
            del self.buffers[name]
            self.emit('list-changed')

        return ret
