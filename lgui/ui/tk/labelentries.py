from tkinter import StringVar, Label, Entry, OptionMenu


class LabelEntry:

    def __init__(self, name, text, default, options=None, command=None):

        self.name = name
        self.text = text
        if default is None:
            default = 'None'
        self.default = default
        self.cls = default.__class__
        self.options = options
        self.command = command


class LabelEntries(dict):

    def __init__(self, master, ui, entries):

        self.row = 0
        self.ui = ui

        for labelentry in entries:

            var = StringVar(master)
            var.set(labelentry.default)
            self[labelentry.name] = (var, labelentry.cls)

            label = Label(master, text=labelentry.text + ': ', anchor='w')
            if isinstance(labelentry.options, (tuple, list)):
                entry = OptionMenu(
                    master, var, *labelentry.options,
                    command=labelentry.command)
            else:
                if labelentry.command:
                    var.trace_add('write', labelentry.command)
                entry = Entry(master, textvariable=var)

            label.grid(row=self.row, sticky='w')
            entry.grid(row=self.row, column=1, sticky='w')

            self.row += 1

    def get_var(self, name):

        return self[name][0]

    def get_cls(self, name):

        return self[name][1]

    def get_text(self, name):

        return self.get_var(name).get()

    def get(self, name):

        val = self.get_text(name)
        cls = self.get_cls(name)
        try:
            return cls(val)
        except Exception:
            self.ui.show_error_dialog('Invalid value %s for %s' % (val, name))
