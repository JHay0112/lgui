from tkinter import Tk, Button
from numpy import linspace
from .labelentries import LabelEntry, LabelEntries


class PlotPropertiesDialog:

    def __init__(self, expr, ui):

        self.expr = expr
        self.ui = ui

        self.master = Tk()
        self.master.title('Plot properties')

        entries = [LabelEntry('min', 'Min', 0.0),
                   LabelEntry('max', 'Max', 1.0),
                   LabelEntry('points', 'Points', 200)]

        self.symbols = []
        for key in expr.symbols:
            # Ignore domain variable
            if key != expr.var.name:
                entries.append(LabelEntry(key, key, 0.0))
                self.symbols.append(key)

        plots = {'Plot': 'plot', 'Bode': 'bode_plot',
                 'Pole-zero': 'pole_zero_plot', 'Nichols': 'nichols_plot',
                 'Nyquist': 'nyquist_plot'}

        kinds = []
        for key, val in plots.items():
            if hasattr(expr, val):
                kinds.append(key)

        entries.append(LabelEntry('kind', 'Plot type', 'Plot', kinds))
        self.labelentries = LabelEntries(self.master, ui, entries)

        button = Button(self.master, text="Plot", command=self.on_update)
        button.grid(row=self.labelentries.row)

    def on_update(self):

        points = linspace(self.labelentries.get('min'),
                          self.labelentries.get('max'),
                          self.labelentries.get('points'))

        defs = {}
        for key in self.symbols:
            val = self.labelentries.get_text(key)
            if val == '':
                self.ui.show_error_dialog('Undefined symbol ' + key)
                return
            val = self.labelentries.get(key)
            defs[key] = val

        expr = self.expr.subs(defs)

        kind = self.labelentries.get('kind')
        if kind == 'Plot':
            im = expr.plot(points)
        elif kind == 'Bode':
            im = expr.bode_plot(points)
        elif kind == 'Pole-zero':
            im = expr.pole_zero_plot()
        elif kind == 'Nichols':
            im = expr.nichols_plot(points)
        elif kind == 'Nyquist':
            im = expr.nyquist_plot(points)
        else:
            raise RuntimeError('Unexpected case')

        if isinstance(im, tuple):
            im = im[0]

        im.figure.show()
