from tkinter import Tk, StringVar, Label, OptionMenu


class ExprDialog:

    def __init__(self, expr):

        self.expr = expr

        domain_map = {'time': 'Time', 'laplace': 'Laplace',
                      'fourier': 'Fourier', 'frequency': 'Frequency',
                      'angular fourier': 'Angular Fourier',
                      'angular frequency': 'Angular Frequency'}
        self.domain = domain_map[expr.domain]

        self.formats = {'Canonical': 'canonical',
                        'Standard': 'standard',
                        'ZPK': 'ZPK',
                        'Partial fraction': 'partfrac',
                        'Time constant': 'timeconst'}

        self.format = 'Canonical'

        self.domains = {'Time': 'time', 'Laplace': 'laplace',
                        'Fourier': 'fourier', 'Frequency': 'frequency',
                        'Angular Fourier': 'angular_fourier',
                        'Angular Frequency': 'angular_frequency'}

        format_var = StringVar(master)
        format_var.set(self.format)

        domain_var = StringVar(master)
        domain_var.set(self.domain)

        master = Tk()

        format_label = Label(master, text='Format: ')
        format_option = OptionMenu(master, format_var,
                                   *self.formats.keys(),
                                   command=self.on_format)

        format_label.grid(row=0)
        format_option.grid(row=0, column=1)

        domain_label = Label(master, text='Domain: ')
        domain_option = OptionMenu(master, domain_var,
                                   *self.domains.keys(),
                                   command=self.on_domain)

        domain_label.grid(row=1)
        domain_option.grid(row=1, column=1)

        expr_label1 = Label(master, text='Expr: ')
        expr_label2 = Label(master, text=expr.pretty())
        expr_label1.grid(row=2, column=0)
        expr_label2.grid(row=2, column=1)

        self.expr_label = expr_label2

    def on_format(self, format):
        if format == self.format:
            return
        self.format = format
        self.update()

    def on_domain(self, domain):
        if domain == self.domain:
            return
        self.domain = domain
        self.update()

    def update(self):

        domain = self.domains[self.domain]
        format = self.formats[self.format]

        globals = {'result': self.expr}
        try:
            e = eval('result.%s().%s()' % (domain, format), globals)
            self.expr_label.config(text=e.pretty())
        except (AttributeError, ValueError) as e:
            self.expr_label.config(text=e)
