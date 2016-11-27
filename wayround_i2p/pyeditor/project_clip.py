
import collections
import os.path
import json

from gi.repository import GObject


class ProjectClip(GObject.GObject):

    __gsignals__ = {
        'list-changed': (GObject.SIGNAL_RUN_FIRST, None, tuple())
    }

    def __init__(self, main_window):

        self.projects = collections.OrderedDict()
        self.main_window = main_window

        super().__init__()

        return

    def add(self, name, path):

        if not os.path.isdir(path):
            raise TypeError("`proj' must be existing dir")

        if name not in self.projects:
            self.projects[name] = path
            self.main_window.cfg.cfg.set(
                'general',
                'projects',
                json.dumps(list(self.to_items()))
                )
            self.main_window.cfg.save()
            self.emit('list-changed')

        return

    def rm(self, name):
        ret = 0
        if name in self.projects:
            del self.projects[name]
            self.main_window.cfg.cfg.set(
                'general',
                'projects',
                json.dumps(list(self.to_items()))
                )
            self.main_window.cfg.save()
            self.emit('list-changed')
        return ret

    def load_config(self):

        res = self.main_window.cfg.cfg.get(
            'general',
            'projects'
            )

        if res is not None:
            self.projects = collections.OrderedDict(json.loads(res))

        self.emit('list-changed')

        return

    def get(self, name):
        ret = None

        if name in self.projects:
            ret = self.projects[name]

        return ret

    def get_dict(self):
        return self.projects

    def get_list(self):
        return sorted(list(self.projects.keys()))

    def to_items(self):
        return self.projects.items()

    def from_items(self, items):
        self.projects = collections.OrderedDict(items)
        return
