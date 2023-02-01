from tkinter import Tk, StringVar, Label, OptionMenu, Button, Entry
from lcapy.system import tmpfilename, LatexRunner, PDFConverter
from PIL import Image, ImageTk


class ExprDialog:

    def __init__(self, expr, ui, title=''):

        self.expr = expr
        self.expr_tweak = expr
        self.ui = ui

        self.operation = 'result'

        self.format = ''

        self.formats = {'': '',
                        'Canonical': 'canonical',
                        'Standard': 'standard',
                        'ZPK': 'ZPK',
                        'Partial fraction': 'partfrac',
                        'Time constant': 'timeconst'}

        self.domain = ''

        self.domains = {'': '',
                        'Time': 'time',
                        'Phasor': 'phasor',
                        'Laplace': 'laplace',
                        'Fourier': 'fourier',
                        'Frequency': 'frequency_response',
                        'Angular Fourier': 'angular_fourier',
                        'Angular Frequency': 'angular_frequency_response'}

        self.master = Tk()
        self.master.title(title)

        self.operation_var = StringVar(self.master)
        self.operation_var.set(self.operation)

        operation_label = Label(self.master, text='Operation: ')
        operation_entry = Entry(self.master, textvariable=self.operation_var)
        self.operation_var.trace_add('write', self.on_operation)

        operation_label.grid(row=0)
        operation_entry.grid(row=0, column=1)

        format_var = StringVar(self.master)
        format_var.set(self.format)

        format_label = Label(self.master, text='Format: ')
        format_option = OptionMenu(self.master, format_var,
                                   *self.formats.keys(),
                                   command=self.on_format)

        format_label.grid(row=1)
        format_option.grid(row=1, column=1)

        domain_var = StringVar(self.master)
        domain_var.set(self.domain)

        domain_label = Label(self.master, text='Domain: ')
        domain_option = OptionMenu(self.master, domain_var,
                                   *self.domains.keys(),
                                   command=self.on_domain)

        domain_label.grid(row=2)
        domain_option.grid(row=2, column=1)

        expr_label1 = Label(self.master, text='Expr: ')
        expr_label2 = Label(self.master, text='')
        expr_label1.grid(row=3, column=0)
        expr_label2.grid(row=3, column=1)

        self.expr_label = expr_label2

        button = Button(self.master, text="Plot", command=self.on_plot)
        button.grid(row=4)

        self.update()

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

    def on_operation(self, *args):

        self.operation = self.operation_var.get()
        self.update()

    def update(self):

        operation = self.operation
        format = self.format
        domain = self.domain

        command = operation
        if format != '':
            command += '.' + self.formats[format] + '()'
        if domain != '':
            command += '.' + self.domains[domain] + '()'

        globals = {'result': self.expr}
        try:
            self.expr_tweak = eval(command, globals)
            # self.show_pretty(e)
            self.show_img(self.expr_tweak)
        except Exception as e:
            self.expr_label.config(text=e)

    def show_pretty(self, e):

        self.expr_label.config(text=e.pretty())

    def make_img(self, e):

        tex_filename = tmpfilename('.tex')

        # Need amsmath for operatorname
        template = ('\\documentclass[a4paper]{standalone}\n'
                    '\\usepackage{amsmath}\n'
                    '\\begin{document}\n$%s$\n'
                    '\\end{document}\n')
        content = template % e.latex()

        open(tex_filename, 'w').write(content)
        pdf_filename = tex_filename.replace('.tex', '.pdf')
        latexrunner = LatexRunner()
        latexrunner.run(tex_filename)

        png_filename = tex_filename.replace('.tex', '.png')
        pdfconverter = PDFConverter()
        pdfconverter.to_png(pdf_filename, png_filename, dpi=300)

        img = ImageTk.PhotoImage(Image.open(png_filename), master=self.master)
        return img

    def show_img(self, e):

        img = self.make_img(e)
        self.expr_label.config(image=img)
        self.expr_label.photo = img

    def on_plot(self):

        self.ui.show_plot_properties_dialog(self.expr_tweak)
