from ..editorbase import EditorBase
from matplotlib.pyplot import subplots, rcParams, show
import matplotlib.patches as patches
from matplotlib.backend_tools import ToolBase
from math import degrees
from numpy import arange
from sys import exit


class Tool(ToolBase):

    def __init__(self, toolmanager, name, func):
        super(Tool, self).__init__(toolmanager, name)
        self.func = func

    def trigger(self, sender, event, data=None):
        self.func()


class AnalyzeTool(Tool):
    # default_keymap = 'ctrl+a'
    description = 'Analyze'


class EditTool(Tool):
    # default_keymap = 'ctrl+e'
    description = 'Edit'


class ExportTool(Tool):
    # default_keymap = 'ctrl+x'
    description = 'Export'


class LoadTool(Tool):
    # default_keymap = 'ctrl+l'
    description = 'Load'


class QuitTool(Tool):
    # default_keymap = 'q'
    description = 'Quit'


class SaveTool(Tool):
    # default_keymap = 'ctrl+s'
    description = 'Save'


class ViewTool(Tool):
    # default_keymap = 'ctrl+v'
    description = 'View'


class Layer:

    def __init__(self, ax):

        self.ax = ax
        self.color = 'black'

    def stroke_line(self, xstart, ystart, xend, yend):

        return self.ax.plot((xstart, xend), (ystart, yend), '-',
                            color=self.color)

    def stroke_arc(self, x, y, r, theta1, theta2):

        patch = patches.Arc((x, y), r, r, 0, degrees(theta1), degrees(theta2))
        self.ax.add_patch(patch)
        return patch

    def clear(self):

        self.ax.clear()

    def stroke_rect(self, xstart, ystart, width, height):
        # xstart, ystart top left corner

        xend = xstart + width
        yend = ystart + height

        self.stroke_line(xstart, ystart, xstart, yend)
        self.stroke_line(xstart, yend, xend, yend)
        self.stroke_line(xend, yend, xend, ystart)
        self.stroke_line(xend, ystart, xstart, ystart)

    def stroke_filled_circle(self, x, y, radius=0.5, color='black', alpha=0.5):

        patch = patches.Circle((x, y), radius, fc=color, alpha=alpha)
        self.ax.add_patch(patch)
        return patch

    def text(self, x, y, text, **kwargs):

        return self.ax.annotate(text, (x, y), **kwargs)

    def remove(self, patch):

        self.ax.remove(patch)


class Editor(EditorBase):

    FIG_WIDTH = 6
    FIG_HEIGHT = 4

    XSIZE = 30
    YSIZE = 20

    def __init__(self, filename=None, uimodel_class=None, debug=0):

        self.debug = debug

        # Default Linux backend was TkAgg now QtAgg
        # Default Windows backend Qt4Agg
        import matplotlib.pyplot as p
        if self.debug:
            print(p.get_backend())
        # Need TkAgg if using Tkinter file dialogs
        p.switch_backend('TkAgg')

        super(Editor, self).__init__()

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
            ['Edit', EditTool, self.model.on_edit],
            ['Analyze', AnalyzeTool, self.model.on_analyze],
            ['Quit', QuitTool, self.quit]]

        for tool in tools:
            self.fig.canvas.manager.toolmanager.add_tool(tool[0],
                                                         tool[1],
                                                         func=tool[2])
            self.fig.canvas.manager.toolbar.add_tool(tool[0], 'toolgroup')

        self.fig.canvas.mpl_connect('close_event', self.on_close)

        xticks = arange(self.XSIZE)
        yticks = arange(self.YSIZE)
        self.ax.set_xlim(0, self.XSIZE)
        self.ax.set_ylim(0, self.YSIZE)
        self.ax.set_xticks(xticks)
        self.ax.set_yticks(yticks)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.grid()

        # TODO: matplotlib uses on layer
        layer = Layer(self.ax)

        self.cursor_layer = layer
        self.active_layer = layer
        self.component_layer = layer
        self.grid_layer = layer

        # self.ax.spines['left'].set_color('none')
        # self.ax.spines['right'].set_color('none')
        # self.ax.spines['bottom'].set_color('none')
        # self.ax.spines['top'].set_color('none')

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

    def refresh(self):

        self.fig.canvas.draw()

    def on_key_press_event(self, event):

        # Might be in the textboxes...
        if event.inaxes != self.ax:
            return

        key = event.key
        self.model.on_key(key)

    def on_click_event(self, event):

        if self.debug:
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))

        if event.button == 1:
            self.model.on_left_click(event.xdata, event.ydata)
        elif event.button == 3:
            self.model.on_right_click(event.xdata, event.ydata)

    def on_close(self, event):

        self.model.on_close()

    def quit(self):

        exit()

    def show_message_dialog(self, message):

        from tkinter.messagebox import showinfo
        showinfo('', message)

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
