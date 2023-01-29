from ...components import Capacitor, Inductor
from tkinter import Tk, StringVar, Label, OptionMenu, Entry, Button


class CptPropertiesDialog:

    def __init__(self, cpt, update=None):

        self.cpt = cpt
        self.update = update

        self.master = Tk()

        row = 0

        self.kind_var = None
        if cpt.kind is not None:
            self.kind_var = StringVar(self.master)
            self.kind_var.set(cpt.kind)

            kind_label = Label(self.master, text='Kind: ')
            kind_option = OptionMenu(self.master, self.kind_var,
                                     *cpt.kinds.keys())

            kind_label.grid(row=row)
            kind_option.grid(row=row, column=1)
            row += 1

        self.name_var = StringVar(self.master)
        self.name_var.set(cpt.cname)

        name_label = Label(self.master, text='Name: ')
        name_entry = Entry(self.master, textvariable=self.name_var)

        name_label.grid(row=row)
        name_entry.grid(row=row, column=1)
        row += 1

        self.value_var = StringVar(self.master)
        value = cpt.value
        if value is None:
            value = cpt.cname
        self.value_var.set(value)

        value_label = Label(self.master, text='Value: ')
        value_entry = Entry(self.master, textvariable=self.value_var)

        value_label.grid(row=row)
        value_entry.grid(row=row, column=1)
        row += 1

        self.initial_value_var = None
        if isinstance(cpt, (Capacitor, Inductor)):

            ivlabel = 'v0'
            if isinstance(cpt, Inductor):
                ivlabel = 'i0'

            self.initial_value_var = StringVar(self.master)

            initial_value_label = Label(self.master, text=ivlabel + ': ')
            initial_value_entry = Entry(
                self.master, textvariable=self.initial_value_var)
            initial_value_label.grid(row=row)
            initial_value_entry.grid(row=row, column=1)
            row += 1

        button = Button(self.master, text="OK", command=self.on_update)
        button.grid(row=row)

    def on_update(self):

        if self.kind_var is not None:
            kind = self.kind_var.get()
            if kind == '':
                kind = None
            self.cpt.kind = kind

        self.cpt.cname = self.name_var.get()

        value = self.value_var.get()
        if value == '':
            value = None
        self.cpt.value = value

        if self.initial_value_var is not None:
            value = self.initial_value_var.get()
            if value == '':
                value = None
            self.cpt.initial_value = value

        self.master.destroy()

        if self.update:
            self.update(self.cpt)
