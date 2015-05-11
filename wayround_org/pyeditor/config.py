
import collections
import configparser
import os.path

import wayround_org.utils.path


class Config:

    def __init__(self, main_window, cfg_file=None):
        self.cfg = configparser.ConfigParser()

        if cfg_file is None:
            cfg_file = wayround_org.utils.path.join(
                os.path.expanduser('~')
                )
            cfg_file = wayround_org.utils.path.join(
                cfg_file, '.config', 'PyEditor', 'config.ini'
                )

        self._cfg_file = cfg_file

        return

    def load(self):

        if os.path.isfile(self._cfg_file):
            self.cfg.read(self._cfg_file)
        else:
            self.cfg.read_dict(
                collections.OrderedDict([
                    ('general',
                     collections.OrderedDict([
                         ('projects', '[]')
                         ])
                     ),
                    ])
                )

        return

    def save(self):

        ret = 0

        filename = wayround_org.utils.path.abspath(self._cfg_file)

        d = os.path.dirname(filename)

        if not os.path.isdir(d):
            try:
                os.makedirs(d)
            except:
                pass

            if not os.path.isdir(d):
                ret = 1

        with open(filename, 'w') as f:
            self.cfg.write(f)

        return ret
