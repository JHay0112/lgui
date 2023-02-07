from matplotlib.pyplot import subplots, rcParams, show
from matplotlib.backend_tools import ToolBase
from numpy import arange
from sys import exit
from .layer import Layer


class Tool(ToolBase):

    def __init__(self, toolmanager, name, func):
        super(Tool, self).__init__(toolmanager, name)
        self.func = func

    def trigger(self, sender, event, data=None):
        self.func()


class DescribeTool(Tool):
    # default_keymap = 'ctrl+?'
    description = 'Describe'


class ExportTool(Tool):
    # default_keymap = 'ctrl+x'
    description = 'Export'


class HelpTool(Tool):
    # default_keymap = 'ctrl+h'
    description = 'Help'


class InspectTool(Tool):
    # default_keymap = 'ctrl+i'
    description = 'Inspect'


class LoadTool(Tool):
    # default_keymap = 'ctrl+l'
    description = 'Load'


class PreferencesTool(Tool):
    # default_keymap = 'ctrl+e'
    description = 'Preferences'


class QuitTool(Tool):
    # default_keymap = 'q'
    description = 'Quit'


class SaveTool(Tool):
    # default_keymap = 'ctrl+s'
    description = 'Save'


class ViewTool(Tool):
    # default_keymap = 'ctrl+v'
    description = 'View'


class LcapyTkM:

    FIG_WIDTH = 6
    FIG_HEIGHT = 4

    XSIZE = 30
    YSIZE = 20
    SCALE = 0.01

    def __init__(self, filename=None, uimodel_class=None, debug=0):

        self.debug = debug

        # Default Linux backend was TkAgg now QtAgg
        # Default Windows backend Qt4Agg
        import matplotlib.pyplot as p
        if self.debug:
            print(p.get_backend())
        # Need TkAgg if using Tkinter file dialogs
        p.switch_backend('TkAgg')

        super(LcapyTkM, self).__init__()

        from ..uimodelmph import UIModelMPH

        if uimodel_class is None:
            uimodel_class = UIModelMPH

        self.model = uimodel_class(self)

        rcParams['keymap.xscale'].remove('L')
        rcParams['keymap.xscale'].remove('k')
        rcParams['keymap.yscale'].remove('l')
        rcParams['keymap.save'].remove('s')
        rcParams['keymap.save'].remove('ctrl+s')

        rcParams['toolbar'] = 'toolmanager'
        self.fig, self.ax = subplots(1, figsize=(self.FIG_WIDTH,
                                                 self.FIG_HEIGHT))
        self.fig.subplots_adjust(
            left=0.1, top=0.9, bottom=0.1, right=0.9)
        self.ax.axis('equal')

        # Tools to add to the toolbar
        tools = [
            ['Load', LoadTool, self.model.on_load],
            ['Save', SaveTool, self.model.on_save],
            ['Export', ExportTool, self.model.on_export],
            ['View', ViewTool, self.model.on_view],
            ['Inspect', InspectTool, self.model.on_inspect],
            ['Describe', DescribeTool, self.model.on_describe],
            ['Preferences', ExportTool, self.model.on_preferences],
            ['Help', ExportTool, self.model.on_help],
            ['Quit', QuitTool, self.quit]]

        for tool in tools:
            self.fig.canvas.manager.toolmanager.add_tool(tool[0],
                                                         tool[1],
                                                         func=tool[2])
            self.fig.canvas.manager.toolbar.add_tool(tool[0], 'toolgroup')

        self.fig.canvas.mpl_connect('close_event', self.on_close)

        self.draw_grid()

        layer = Layer(self.ax)

        self.cursor_layer = layer
        self.active_layer = layer
        self.component_layer = layer
        self.grid_layer = layer

        self.cid = self.fig.canvas.mpl_connect('button_press_event',
                                               self.on_click_event)

        self.kp_cid = self.fig.canvas.mpl_connect('key_press_event',
                                                  self.on_key_press_event)

        self.fig.canvas.mpl_connect('close_event', self.on_close)

        # Make fullscreen
        self.fig.canvas.manager.full_screen_toggle()

        # self.set_title()

        if filename is not None:
            self.model.load(filename)

    def display(self):

        show()

    def draw_grid(self):

        xticks = arange(self.XSIZE)
        yticks = arange(self.YSIZE)
        self.ax.set_xlim(0, self.XSIZE)
        self.ax.set_ylim(0, self.YSIZE)
        self.ax.set_xticks(xticks)
        self.ax.set_yticks(yticks)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.grid(color='lightblue')

        self.ax.tick_params(which='both', left=False, bottom=False,
                            top=False, labelbottom=False)

    def clear(self):

        self.component_layer.clear()
        self.draw_grid()

    def refresh(self):

        self.fig.canvas.draw()

    def on_key_press_event(self, event):

        # Might be in the textboxes...
        if event.inaxes != self.ax:
            return

        key = event.key
        if self.debug:
            print(key)

        if key in self.model.key_bindings:
            self.model.key_bindings[key]()
        elif key in self.mmodel.key_bindings_with_key:
            self.model.key_bindings_with_key[key](key)

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

    def on_close(self, event):

        self.model.on_close()

    def new(self):

        pass

    def quit(self):

        exit()

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

    def load(self, filename):
        pass
