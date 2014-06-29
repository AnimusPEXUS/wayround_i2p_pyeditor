
from gi.repository import Gtk

import org.wayround.pyeditor.main_window


w = org.wayround.pyeditor.main_window.MainWindow()
w.cfg.load()
w.show()
w.install_mode('dummy')
w.projects.load_config()

Gtk.main()
