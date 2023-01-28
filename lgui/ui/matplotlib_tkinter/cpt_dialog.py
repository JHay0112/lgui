from tkinter import Tk, StringVar, Label, OptionMenu, Entry, Button


class CptDialog:

    def __init__(self, cpt):

        self.cpt = cpt

        self.master = Tk()

        self.kind_var = StringVar(self.master)
        self.kind_var.set(cpt.kind)

        if cpt.kind is not None:
            kind_label = Label(self.master, text='Kind: ')
            kind_option = OptionMenu(self.master, self.kind_var,
                                     *cpt.kinds.keys())

            kind_label.grid(row=0)
            kind_option.grid(row=0, column=1)

        self.name_var = StringVar(self.master)
        self.name_var.set(cpt.cname)

        name_label = Label(self.master, text='Name: ')
        name_option = Entry(self.master, textvariable=self.name_var)

        name_label.grid(row=1)
        name_option.grid(row=1, column=1)

        self.value_var = StringVar(self.master)
        value = cpt.value
        if value is None:
            value = cpt.cname
        self.value_var.set(value)

        value_label = Label(self.master, text='Value: ')
        value_option = Entry(self.master, textvariable=self.value_var)

        value_label.grid(row=2)
        value_option.grid(row=2, column=1)

        button = Button(self.master, text="OK", command=self.on_update)
        button.grid(row=3)

    def on_update(self):

        self.cpt.kind = self.kind_var.get()
        self.cpt.cname = self.name_var.get()
        self.cpt.value = self.value_var.get()
        self.master.destroy()
