#!/usr/bin/python3

def main():
    import gi

    gi.require_version('Gtk', '3.0')
    gi.require_version('GtkSource', '3.0')

    from gi.repository import Gtk

    import wayround_i2p.pyeditor.main_window

    w = wayround_i2p.pyeditor.main_window.MainWindow()

    w.show()
    w.install_mode('dummy')
    w.projects.load_config()
    w.buffer_clip.load_config()

    Gtk.main()
    return

if __name__ == '__main__':
    exit(main())
