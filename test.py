import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class AppWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title = "Battery Monitor")
        grid = Gtk.Grid()
        self.add(grid)

        label = Gtk.Label(label = "hello world!")
        button1 = Gtk.Button(label = "button1")
        button = Gtk.Button(label = "click")
        button.connect("clicked", self.on_button_clicked)
        grid.attach(label, 0, 0, 5, 1)
        grid.attach(button1, 0, 1, 2, 1)
        grid.attach_next_to(button, button1, Gtk.PositionType.BOTTOM, 1, 1)
        

    def on_button_clicked(self, widget):
        print("hello")
    
win = AppWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()