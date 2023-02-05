from tkinter import Canvas, Tk, Menu, Frame, TOP, BOTH
from tkinter.ttk import Notebook
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy import arange
from os.path import basename
from ..uimodelmph import UIModelMPH
from .layer import Layer


class LcapyTk(Tk):

    XSIZE = 30
    YSIZE = 30
    SCALE = 0.01

    def __init__(self, filename=None, uimodel_class=None, debug=0):

        super().__init__()
        self.debug = debug
        self.model = None
        self.canvas = None

        if uimodel_class is None:
            uimodel_class = UIModelMPH
        self.uimodel_class = uimodel_class

        # Title and size of the window
        self.title('Lcapy-tk')
        self.geometry('1200x800')

        # Create the drop down menus
        self.menu = Menu(self, bg='lightgrey', fg='black')

        # File menu
        self.file_menu = Menu(self.menu, tearoff=0,
                              bg='lightgrey', fg='black')

        self.file_menu.add_command(label='New', command=self.on_new,
                                   underline=0, accelerator='Ctrl+n')
        self.file_menu.add_command(label='Open', command=self.on_load,
                                   underline=0, accelerator='Ctrl+o')
        self.file_menu.add_command(label='Save', command=self.on_save,
                                   underline=0, accelerator='Ctrl+s')
        self.file_menu.add_command(label='Export', command=self.on_export,
                                   underline=0, accelerator='Ctrl+e')
        self.file_menu.add_command(label='Quit', command=self.on_quit,
                                   underline=0, accelerator='Ctrl+q')

        self.menu.add_cascade(
            label='File', underline=0, menu=self.file_menu)

        # Edit menu
        self.edit_menu = Menu(self.menu, tearoff=0,
                              bg='lightgrey', fg='black')

        self.edit_menu.add_command(label='Preferences',
                                   command=self.on_preferences,
                                   underline=0)
        self.edit_menu.add_command(label='Undo', command=self.on_undo,
                                   accelerator='Ctrl+z')
        self.edit_menu.add_command(label='Cut',
                                   command=self.on_cut,
                                   accelerator='Ctrl+x')
        self.edit_menu.add_command(label='Copy',
                                   command=self.on_copy,
                                   accelerator='Ctrl+c')
        self.edit_menu.add_command(label='Paste',
                                   command=self.on_paste,
                                   accelerator='Ctrl+v')

        self.menu.add_cascade(label='Edit', underline=0, menu=self.edit_menu)

        # View menu
        self.view_menu = Menu(self.menu, tearoff=0,
                              bg='lightgrey', fg='black')

        self.view_menu.add_command(label='Circuitikz', command=self.on_view,
                                   accelerator='Ctrl+u')
        self.view_menu.add_command(label='Netlist',
                                   command=self.on_netlist)

        self.menu.add_cascade(label='View', underline=0, menu=self.view_menu)

        # Inspect menu
        self.inspect_menu = Menu(self.menu, tearoff=0,
                                 bg='lightgrey', fg='black')
        inspect_menu = self.inspect_menu

        inspect_menu.add_command(label='Voltage', underline=0,
                                 command=self.on_inspect_voltage)
        inspect_menu.add_command(label='Current', underline=0,
                                 command=self.on_inspect_current)
        inspect_menu.add_command(label='Thevenin impedance',
                                 underline=0,
                                 command=self.on_inspect_thevenin_impedance)
        inspect_menu.add_command(label='Norton admittance',
                                 underline=0,
                                 command=self.on_inspect_norton_admittance)

        self.menu.add_cascade(label='Inspect', underline=0,
                              menu=self.inspect_menu)

        # Component menu
        self.component_menu = Menu(self.menu, tearoff=0,
                                   bg='lightgrey', fg='black')
        component_menu = self.component_menu

        for key, val in self.uimodel_class.component_map.items():
            component_menu.add_command(label=val[0],
                                       command=lambda foo=key: self.on_add_cpt(
                                           foo),
                                       accelerator=key)
            # Callback called twice for some mysterious reason
            # self.component_menu.bind(key,
            #                         lambda arg, foo=key: self.on_add_cpt(foo))

        self.menu.add_cascade(label='Component', underline=0,
                              menu=self.component_menu)

        # Help menu
        self.help_menu = Menu(self.menu, tearoff=0,
                              bg='lightgrey', fg='black')

        self.help_menu.add_command(label='Help',
                                   command=self.on_help, accelerator='Ctrl+h')

        self.menu.add_cascade(label='Help', underline=0,
                              menu=self.help_menu)

        self.config(menu=self.menu)

        # Notebook tabs
        self.notebook = Notebook(self)

        self.canvases = []

        self.canvas = None

        self.load(filename)

    def clear(self):

        self.component_layer.clear()
        self.canvas.drawing.draw_grid()

    def display(self):

        self.mainloop()

    def enter(self, canvas):

        self.canvas = canvas
        self.model = canvas.model
        self.layer = canvas.layer

        # TODO, resolve with JH
        self.cursor_layer = self.layer
        self.active_layer = self.layer
        self.component_layer = self.layer
        self.grid_layer = self.layer

        if self.debug:
            print(self.notebook.tab(self.notebook.select(), "text"))

    def load(self, filename):

        model = self.new()

        if filename is None:
            return

        model.load(filename)
        self.set_filename(filename)

    def set_filename(self, filename):

        name = basename(filename)
        self.set_canvas_title(name)

    def create_canvas(self, name):

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
        canvas.layer = Layer(canvas.drawing.ax)

        tab.canvas = canvas

        self.canvases.append(canvas)

        self.notebook.select(len(self.canvases) - 1)

        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_selected)

        return canvas

    def bind_canvas(self, canvas, model):

        canvas.model = model

        figure = canvas.drawing.fig
        canvas.bp_id = figure.canvas.mpl_connect('button_press_event',
                                                 self.on_click_event)

        canvas.kp_id = figure.canvas.mpl_connect('key_press_event',
                                                 self.on_key_press_event)

        self.enter(canvas)

    def new(self):

        model = self.uimodel_class(self)
        canvas = self.create_canvas('Untitled')
        self.bind_canvas(canvas, model)
        self.model = model
        return model

    def on_add_cpt(self, cptname):

        if self.debug:
            print('Adding component ' + cptname)

        self.model.on_add_cpt(cptname)

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

    def on_copy(self, *args):

        self.model.on_copy()

    def on_cut(self, *args):

        self.model.on_cut()

    def on_enter(self, event):

        # TODO, determine tab from mouse x, y
        if self.debug:
            print('Enter %s, %s' % (event.x, event.y))

        self.enter(self.canvases[0])

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

    def on_help(self, *args):

        self.model.on_help()

    def on_inspect_current(self, *args):

        self.model.on_inspect_current()

    def on_inspect_norton_admittance(self, *args):

        self.model.on_inspect_norton_admittance()

    def on_inspect_thevenin_impedance(self, *args):

        self.model.on_inspect_thevenin_impedance()

    def on_inspect_voltage(self, *args):

        self.model.on_inspect_voltage()

    def on_load(self, *args):

        self.model.on_load()

    def on_netlist(self, *args):

        self.model.on_netlist()

    def on_new(self, *args):

        self.model.on_new()

    def on_preferences(self, *args):

        self.model.on_preferences()

    def on_paste(self, *args):

        self.model.on_paste()

    def on_quit(self, *args):

        if self.debug:
            print('Quit')
        self.model.on_quit()

    def on_save(self, *args):

        if self.debug:
            print('Save')
        self.model.on_save()

    def on_tab_selected(self, event):

        notebook = event.widget
        tab_id = notebook.select()
        index = notebook.index(tab_id)

        # TODO: rethink if destroy a tab/canvas
        canvas = self.canvases[index]
        self.enter(canvas)

    def on_undo(self, *args):

        self.model.on_undo()

    def on_view(self, *args):

        self.model.on_view()

    def refresh(self):

        self.canvas.drawing.fig.canvas.draw()

    def quit(self):

        exit()

    def save(self, filename):

        name = basename(filename)
        self.set_canvas_title(name)

    def set_canvas_title(self, name):

        self.notebook.tab('current', text=name)

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

        self.draw_grid()

    def draw_grid(self):

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
