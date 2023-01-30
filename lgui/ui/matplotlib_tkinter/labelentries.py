from tkinter import StringVar, Label, Entry, OptionMenu


class LabelEntry:

    def __init__(self, name, text, default, options=None):

        self.name = name
        self.text = text
        self.default = default
        self.cls = default.__class__
        self.options = options


class LabelEntries(dict):

    def __init__(self, master, ui, entries):

        self.row = 0
        self.ui = ui
        for labelentry in entries:

            var = StringVar(master)
            var.set(labelentry.default)
            self[labelentry.name] = (var, labelentry.cls)

            label = Label(master, text=labelentry.text + ': ')
            if isinstance(labelentry.options, (tuple, list)):
                entry = OptionMenu(master, var, *labelentry.options)
            else:
                entry = Entry(master, textvariable=var)

            label.grid(row=self.row)
            entry.grid(row=self.row, column=1)

            self.row += 1

    def get_text(self, name):

        return self[name][0].get()

    def get(self, name):

        val = self.get_text(name)
        cls = self[name][1]
        try:
            return cls(val)
        except Exception:
            self.ui.show_error_dialog('Invalid value %s for %s' % (val, name))
