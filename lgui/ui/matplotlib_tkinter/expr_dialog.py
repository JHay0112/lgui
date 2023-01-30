from tkinter import Tk, StringVar, Label, OptionMenu
from lcapy.system import tmpfilename, LatexRunner, PDFConverter
from PIL import Image, ImageTk


class ExprDialog:

    def __init__(self, expr, title=''):

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

        self.master = Tk()
        self.master.title(title)

        format_var = StringVar(self.master)
        format_var.set(self.format)

        domain_var = StringVar(self.master)
        domain_var.set(self.domain)

        format_label = Label(self.master, text='Format: ')
        format_option = OptionMenu(self.master, format_var,
                                   *self.formats.keys(),
                                   command=self.on_format)

        format_label.grid(row=0)
        format_option.grid(row=0, column=1)

        domain_label = Label(self.master, text='Domain: ')
        domain_option = OptionMenu(self.master, domain_var,
                                   *self.domains.keys(),
                                   command=self.on_domain)

        domain_label.grid(row=1)
        domain_option.grid(row=1, column=1)

        expr_label1 = Label(self.master, text='Expr: ')
        expr_label2 = Label(self.master, text='')
        expr_label1.grid(row=2, column=0)
        expr_label2.grid(row=2, column=1)

        self.expr_label = expr_label2
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

    def update(self):

        domain = self.domains[self.domain]
        format = self.formats[self.format]

        globals = {'result': self.expr}
        try:
            e = eval('result.%s().%s()' % (domain, format), globals)
            # self.show_pretty(e)
            self.show_img(e)
        except (AttributeError, ValueError) as e:
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
