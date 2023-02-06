from tkinter import Tk, Button, Label
from lcapy.system import tmpfilename, LatexRunner, PDFConverter
from lcapy import Expr
from PIL import Image, ImageTk
from .labelentries import LabelEntry, LabelEntries


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

        entries = [LabelEntry('operation', 'Operation', self.operation,
                              None, self.on_operation),
                   LabelEntry('domain', 'Domain', self.domain,
                              list(self.domains.keys()), self.on_domain),
                   LabelEntry('format', 'Format', self.format,
                              list(self.formats.keys()), self.on_format)]

        self.labelentries = LabelEntries(self.master, ui, entries)

        self.expr_label = Label(self.master, text='')
        self.expr_label.grid(row=self.labelentries.row, columnspan=4)

        button = Button(self.master, text="Plot", command=self.on_plot)
        button.grid(row=self.labelentries.row + 1, sticky='w')

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

        self.operation = self.labelentries.get_text('operation')
        self.update()

    def update(self):

        operation = self.operation
        format = self.format
        domain = self.domain

        command = '(' + operation + ')'
        if domain != '':
            command += '.' + self.domains[domain] + '()'
        if format != '':
            command += '.' + self.formats[format] + '()'

        globals = {'result': self.expr}
        try:
            # Perhaps evaluate domain and transform steps
            # separately if operation is not an Lcapy Expr?
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

        if not isinstance(self.expr_tweak, Expr):
            self.ui.info_dialog('Cannot plot expression')
            return

        self.ui.show_plot_properties_dialog(self.expr_tweak)
