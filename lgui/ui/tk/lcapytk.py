from tkinter import Canvas, Tk, Menu, Frame, TOP, BOTH
from tkinter.ttk import Notebook
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy import arange
from ..uimodelmph import UIModelMPH
from .layer import Layer


class LcapyTk(Tk):

    XSIZE = 30
    YSIZE = 30
    SCALE = 0.01

    def __init__(self, filename=None, uimodel_class=None, debug=0):

        super().__init__()
        self.debug = debug

        if uimodel_class is None:
            uimodel_class = UIModelMPH

        self.model = uimodel_class(self)
        model = self.model

        # Title and size of the window
        self.title('Lcapy-tk')
        self.geometry('1200x800')

        # Create the drop down menus
        self.menu = Menu(self, bg='lightgrey', fg='black')

        # File menu
        self.file_menu = Menu(self.menu, tearoff=0,
                              bg='lightgrey', fg='black')

        self.file_menu.add_command(label='New', command=self.on_new)

        self.file_menu.add_command(label='Load', command=self.on_load)

        self.file_menu.add_command(label='Save', command=self.on_save)

        self.file_menu.add_command(label='Export', command=self.on_export)

        self.file_menu.add_command(label='Quit', command=self.on_quit)

        self.menu.add_cascade(label='File', menu=self.file_menu)

        # Edit menu
        self.edit_menu = Menu(self.menu, tearoff=0,
                              bg='lightgrey', fg='black')

        self.edit_menu.add_command(label='Preferences',
                                   command=model.on_preferences)

        self.menu.add_cascade(label='Edit', menu=self.edit_menu)

        # View menu
        self.view_menu = Menu(self.menu, tearoff=0,
                              bg='lightgrey', fg='black')

        self.view_menu.add_command(label='View', command=model.on_view)

        self.menu.add_cascade(label='View', menu=self.view_menu)

        # Inspect menu
        self.inspect_menu = Menu(self.menu, tearoff=0,
                                 bg='lightgrey', fg='black')

        self.inspect_menu.add_command(label='Voltage',
                                      command=model.on_inspect_voltage)

        self.inspect_menu.add_command(label='Current',
                                      command=model.on_inspect_current)

        self.menu.add_cascade(label='Inspect', menu=self.inspect_menu)

        # Help menu
        self.help_menu = Menu(self.menu, tearoff=0,
                              bg='lightgrey', fg='black')

        self.help_menu.add_command(label='Help',
                                   command=model.on_help)

        self.menu.add_cascade(label='Help', menu=self.help_menu)

        self.config(menu=self.menu)

        # Notebook tabs
        self.notebook = Notebook(self)

        self.canvas = None
        self.canvases = []

        if filename is not None:
            self.model.load(filename)
        else:
            self.new_canvas('Untitled')

        figure = self.canvas.drawing.fig
        self.bp_id = figure.canvas.mpl_connect('button_press_event',
                                               self.on_click_event)

        self.kp_id = figure.canvas.mpl_connect('key_press_event',
                                               self.on_key_press_event)

    def display(self):

        self.mainloop()

    def enter(self, canvas):

        self.canvas = canvas

        layer = Layer(canvas.drawing.ax)

        self.cursor_layer = layer
        self.active_layer = layer
        self.component_layer = layer
        self.grid_layer = layer

    def load(self, filename):

        self.new_canvas(filename)

    def new_canvas(self, name):

        tab = Frame(self.notebook)

        canvas = Canvas(tab)
        canvas.pack(side=TOP, expand=1)

        self.notebook.add(tab, text=name)
        self.notebook.pack(fill=BOTH, expand=1)

        # Add the figure to the graph tab
        fig = Figure(figsize=(12, 8))
        graph = FigureCanvasTkAgg(fig, canvas)
        graph.get_tk_widget().pack(side='top', fill='both', expand=True)

        drawing = Drawing(self, fig)
        canvas.drawing = drawing
        canvas.tab = tab
        self.canvases.append(canvas)

        tab.bind('<Enter>', self.on_enter)

        self.enter(self.canvases[0])
        return canvas

    def new(self):
        self.new_canvas('Untitled')

    def on_enter(self, event):

        # TODO, determine tab from mouse x, y
        if self.debug:
            print('Enter %s, %s' % (event.x, event.y))

        self.enter(self.canvases[0])

    def on_click_event(self, event):

        if self.debug:
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))

        if event.xdata is None or event.ydata is None:
            return

        if event.dblclick:
            if event.button == 1:
                self.model.on_left_double_click(event.xdata, event.ydata)
            elif event.button == 3:
                self.model.on_right_double_click(event.xdata, event.ydata)
        else:
            if event.button == 1:
                self.model.on_left_click(event.xdata, event.ydata)
            elif event.button == 3:
                self.model.on_right_click(event.xdata, event.ydata)

    def on_key_press_event(self, event):

        key = event.key
        if self.debug:
            print(key)

        if key in self.model.key_bindings:
            self.model.key_bindings[key]()
        elif key in self.model.key_bindings_with_key:
            self.model.key_bindings_with_key[key](key)

    def on_key(self, event):

        key = event.char

        if self.debug:
            print('Key %s %s, %s, %s' % (key, event.keycode, event.x, event.y))
            print(event)

        if key in self.model.key_bindings_with_key:
            self.model.key_bindings_with_key[key](key)

    def on_key2(self, event, func):

        if self.debug:
            print('Key2', event, func)
        func()

    def on_export(self, *args):

        self.model.on_export()

    def on_load(self, *args):

        self.model.on_load()

    def on_new(self, *args):

        self.model.on_new()

    def on_quit(self, *args):

        print('Quit')
        self.model.on_quit()

    def on_save(self, *args):

        self.model.on_save()

    def refresh(self):

        self.canvas.drawing.fig.canvas.draw()

    def set_tab_title(self, name):

        self.notebook.tabs('current', text=name)

    def show_expr_dialog(self, expr, title=''):

        from .expr_dialog import ExprDialog

        self.expr_dialog = ExprDialog(expr, self, title)

    def show_inspect_dialog(self, cpt, title=''):

        from .inspect_dialog import InspectDialog

        self.inspect_dialog = InspectDialog(self.model, cpt, title)

    def inspect_properties_dialog(self, cpt, on_changed=None, title=''):

        from .cpt_properties_dialog import CptPropertiesDialog

        self.cpt_properties_dialog = CptPropertiesDialog(cpt,
                                                         on_changed, title)

    def show_node_properties_dialog(self, node, on_changed=None, title=''):

        from .node_properties_dialog import NodePropertiesDialog

        self.node_properties_dialog = NodePropertiesDialog(node,
                                                           on_changed, title)

    def show_plot_properties_dialog(self, expr):

        from .plot_properties_dialog import PlotPropertiesDialog

        self.plot_properties_dialog = PlotPropertiesDialog(expr, self)

    def show_preferences_dialog(self, on_changed=None):

        from .preferences_dialog import PreferencesDialog

        self.preferences_dialog = PreferencesDialog(self, on_changed)

    def show_info_dialog(self, message):

        from tkinter.messagebox import showinfo
        showinfo('', message)

    def show_error_dialog(self, message):

        from tkinter.messagebox import showerror
        showerror('', message)

    def show_message_dialog(self, message, title=''):

        from .message_dialog import MessageDialog

        self.message_dialog = MessageDialog(message, title)

    def open_file_dialog(self, initialdir='.'):

        from tkinter.filedialog import askopenfilename

        filename = askopenfilename(initialdir=initialdir,
                                   title="Select file",
                                   filetypes=(("Lcapy netlist", "*.sch"),))
        return filename

    def save_file_dialog(self, filename):

        from tkinter.filedialog import asksaveasfilename
        from os.path import dirname, splitext, basename

        dirname = dirname(filename)
        basename, ext = splitext(basename(filename))

        options = {}
        options['defaultextension'] = ext
        options['filetypes'] = (("Lcapy netlist", "*.sch"),)
        options['initialdir'] = dirname
        options['initialfile'] = filename
        options['title'] = "Save file"

        return asksaveasfilename(**options)

    def export_file_dialog(self, filename):

        from tkinter.filedialog import asksaveasfilename
        from os.path import dirname, splitext, basename

        dirname = dirname(filename)
        basename, ext = splitext(basename(filename))

        options = {}
        options['defaultextension'] = ext
        options['filetypes'] = (("Embeddable LaTeX", "*.schtex"),
                                ("Standalone LaTeX", "*.tex"),
                                ("PNG image", "*.png"),
                                ("SVG image", "*.svg"),
                                ("PDF", "*.pdf"))
        options['initialdir'] = dirname
        options['initialfile'] = basename + '.pdf'
        options['title'] = "Export file"

        return asksaveasfilename(**options)


class Drawing():

    def __init__(self, ui, fig):

        self.ui = ui
        self.fig = fig
        self.ax = self.fig.add_subplot(111)

        xticks = arange(self.ui.XSIZE)
        yticks = arange(self.ui.YSIZE)

        self.ax.axis('equal')
        self.ax.set_xlim(0, self.ui.XSIZE)
        self.ax.set_ylim(0, self.ui.YSIZE)
        self.ax.set_xticks(xticks)
        self.ax.set_yticks(yticks)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.grid(color='lightblue')

        self.ax.tick_params(which='both', left=False, bottom=False,
                            top=False, labelbottom=False)
