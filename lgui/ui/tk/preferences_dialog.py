from tkinter import Tk, Button
from .labelentries import LabelEntry, LabelEntries


class PreferencesDialog:

    def __init__(self, ui, update):

        self.model = ui.model
        self.update = update

        self.master = Tk()
        self.master.title('Preferences')

        entries = [LabelEntry('label_nodes', 'Node labels', 'none',
                              ('all', 'none', 'alpha', 'pins', 'primary')),
                   LabelEntry('draw_nodes', 'Nodes', 'connections',
                              ('all', 'none', 'connections', 'primary')),
                   LabelEntry('label_cpts', 'Component labels', 'name',
                              ('none', 'name', 'value', 'name+value')),
                   LabelEntry('style', 'Style', 'american',
                              ('american', 'british', 'european'))]

        self.labelentries = LabelEntries(self.master, ui, entries)

        button = Button(self.master, text="OK", command=self.on_ok)
        button.grid(row=self.labelentries.row)

    def on_ok(self):

        self.model.preferences.label_nodes = self.labelentries.get(
            'label_nodes')
        self.model.preferences.draw_nodes = self.labelentries.get('draw_nodes')
        self.model.preferences.label_cpts = self.labelentries.get('label_cpts')
        self.model.preferences.style = self.labelentries.get('style')

        self.master.destroy()

        if self.update:
            # Could check for changes
            self.update()
