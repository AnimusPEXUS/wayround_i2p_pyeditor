
from gi.repository import Gtk

import wayround_org.pyeditor.main_window

w = wayround_org.pyeditor.main_window.MainWindow()

w.show()
w.install_mode('dummy')
w.projects.load_config()
w.buffer_clip.load_config()

Gtk.main()
