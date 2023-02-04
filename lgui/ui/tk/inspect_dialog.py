from tkinter import Tk, Button


class InspectDialog:

    def __init__(self, uimodel, cpt, title=''):

        self.uimodel = uimodel
        self.cpt = cpt

        self.master = Tk()
        self.master.title(title)

        buttons = [('Voltage', self.on_voltage),
                   ('Current', self.on_current),
                   ('Component impedance', self.on_impedance),
                   ('Component admittance', self.on_admittance),
                   ('Thevenin impedance', self.on_thevenin_impedance),
                   ('Norton admittance', self.on_norton_admittance)]
        for b in buttons:
            button = Button(self.master, text=b[0], command=b[1])
            button.pack()

    def on_voltage(self):

        self.uimodel.inspect_voltage(self.cpt)

    def on_current(self):

        self.uimodel.inspect_current(self.cpt)

    def on_impedance(self):

        self.uimodel.inspect_impedance(self.cpt)

    def on_admittance(self):

        self.uimodel.inspect_admittance(self.cpt)

    def on_thevenin_impedance(self):

        self.uimodel.inspect_thevenin_impedance(self.cpt)

    def on_norton_admittance(self):

        self.uimodel.inspect_norton_admittance(self.cpt)
