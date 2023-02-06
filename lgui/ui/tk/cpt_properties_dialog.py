from ...components import Capacitor, Inductor, VCVS
from tkinter import Tk, Button
from .labelentries import LabelEntry, LabelEntries


class CptPropertiesDialog:

    def __init__(self, ui, cpt, update=None, title=''):

        self.cpt = cpt
        self.update = update

        self.master = Tk()
        self.master.title(title)

        entries = []
        if cpt.kind is not None:
            entries.append(LabelEntry(
                'kind', 'Kind', cpt.kind, *cpt.kinds.keys()))

        entries.append(LabelEntry('name', 'Name', cpt.cname))
        entries.append(LabelEntry('value', 'Value', cpt.value))

        if isinstance(cpt, Capacitor):
            entries.append(LabelEntry(
                'initial_value', 'v0', cpt.initial_value))
        elif isinstance(cpt, Inductor):
            entries.append(LabelEntry(
                'initial_value', 'i0', cpt.initial_value))
        elif isinstance(cpt, VCVS):
            names = [cpt.cname for cpt in ui.model.components]
            entries.append(LabelEntry('control', 'Control',
                                      cpt.control, names))

        entries.append(LabelEntry('attrs', 'Attributes', cpt.attrs))

        self.labelentries = LabelEntries(self.master, ui, entries)

        button = Button(self.master, text="OK", command=self.on_update)
        button.grid(row=self.labelentries.row)

    def on_update(self):

        self.cpt.cname = self.labelentries.get('name')
        self.cpt.value = self.labelentries.get('value')
        try:
            self.cpt.initial_value = self.labelentries.get('initial_value')
        except KeyError:
            pass

        try:
            self.cpt.control = self.labelentries.get('control')
        except KeyError:
            pass

        self.cpt.attrs = self.labelentries.get('attrs')

        self.master.destroy()

        if self.update:
            self.update(self.cpt)
