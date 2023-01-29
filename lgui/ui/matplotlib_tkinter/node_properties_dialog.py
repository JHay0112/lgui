from ...components import Capacitor, Inductor
from tkinter import Tk, StringVar, Label, OptionMenu, Entry, Button


class NodePropertiesDialog:

    def __init__(self, node, update=None):

        self.node = node
        self.update = update

        self.master = Tk()

        row = 0

        button = Button(self.master, text="OK", command=self.on_update)
        button.grid(row=row)

    def on_update(self):

        self.master.destroy()

        if self.update:
            self.update(self.node
                        )
