from tkinter import StringVar, Label, Entry


class LabelEntry:

    def __init__(self, name, text, default, cls):

        self.name = name
        self.text = text
        self.default = default
        self.cls = cls


class LabelEntries(dict):

    def __init__(self, master, entries):

        self.row = 0
        for labelentry in entries:

            var = StringVar(master)
            var.set(labelentry.default)
            self[labelentry.name] = (var, labelentry.cls)

            label = Label(master, text=labelentry.text + ': ')
            entry = Entry(master, textvariable=var)

            label.grid(row=self.row)
            entry.grid(row=self.row, column=1)

            self.row += 1

    def get_text(self, name):

        return self[name][0].get()

    def get(self, name):

        # Add error checking
        cls = self[name][1]
        return cls(self.get_text(name))
