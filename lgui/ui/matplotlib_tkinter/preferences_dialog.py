from tkinter import Tk, Button
from .labelentries import LabelEntry, LabelEntries


class PreferencesDialog:

    def __init__(self, ui):

        self.model = ui.model

        self.master = Tk()
        self.master.title('Preferences')

        entries = [LabelEntry('label_nodes', 'Node labels', 'none',
                              ('all', 'none', 'alpha', 'pins', 'primary')),
                   LabelEntry('draw_nodes', 'Nodes', 'connections',
                              ('all', 'none', 'connections', 'primary')),
                   LabelEntry('label_ids', 'Component names', 'true',
                              ('true', 'false')),
                   LabelEntry('label_values', 'Component values', 'true',
                              ('true', 'false')),
                   LabelEntry('style', 'Style', 'american',
                              ('american', 'british', 'european'))]

        self.labelentries = LabelEntries(self.master, ui, entries)

        button = Button(self.master, text="OK", command=self.on_ok)
        button.grid(row=self.labelentries.row)

    def on_ok(self):

        self.model.preferences.label_nodes = self.labelentries.get(
            'label_nodes')
        self.model.preferences.draw_nodes = self.labelentries.get('draw_nodes')
        self.model.preferences.label_ids = self.labelentries.get('label_ids')
        self.model.preferences.label_values = self.labelentries.get(
            'label_values')
        self.model.preferences.style = self.labelentries.get('style')

        self.master.destroy()
