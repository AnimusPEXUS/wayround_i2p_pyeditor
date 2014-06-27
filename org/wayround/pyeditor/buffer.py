
import os.path

from gi.repository import GtkSource


class Buffer:

    def __init__(self, filename=None):

        self.filename = filename
        self._b = None

        if filename is not None:
            self.open(filename)

        return

    def open(self, filename):

        if os.path.exists(filename):

            with open(filename, 'r') as f:
                t = f.read()

            b = GtkSource.Buffer()
            b.set_text(t)

            self.filename = filename

    def save(self, filename=None):

        ret = 0

        if filename is None:
            filename = self.filename

        t = self._b.get_text(
            self._b.get_start_iter(),
            self._b.get_end_iter(),
            False
            )

        with open(filename, 'w') as f:
            f.write(t)

        if ret == 0:
            self.changed = False

        return ret

    def get_buffer(self):
        return self._b

    def destroy(self):
        if self._b:
            self._b.destroy()
        return
