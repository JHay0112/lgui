import sys
from matplotlib.pyplot import subplots, rcParams, show
import matplotlib.patches as patches
from matplotlib.backend_tools import ToolBase
from numpy import arange
from .components import Capacitor, Inductor, Resistor, Wire
from math import sqrt, degrees, atan2


class Tool(ToolBase):

    def __init__(self, toolmanager, name, func):
        super(Tool, self).__init__(toolmanager, name)
        self.func = func

    def trigger(self, sender, event, data=None):
        self.func()


class QuitTool(Tool):
    # default_keymap = 'q'
    description = 'Quit'
    #  Can define image to point to a file to use for the icon


class Components(list):

    def add(self, cpt):

        self.append(cpt)

    def debug(self):

        for cpt in self:
            print(cpt)

    def as_sch(self, step):

        nodes = {}
        kinds = {}

        node_count = 0

        elts = []
        for cpt in self:
            # Enumerate nodes (FIXME for node 0)
            for port in cpt.ports:
                if port.position not in nodes:
                    nodes[port.position] = node_count
                    node_count += 1

            # Enumerate components by type
            if cpt.TYPE not in kinds:
                kinds[cpt.TYPE] = 0
            kinds[cpt.TYPE] += 1

            parts = [cpt.TYPE + '%d' % kinds[cpt.TYPE]]
            for port in cpt.ports:
                parts.append('%d' % nodes[port.position])

            x1, y1 = cpt.ports[0].position
            x2, y2 = cpt.ports[1].position
            r = sqrt((x1 - x2)**2 + (y1 - y2)**2) / step
            if y1 == y2:
                if r == 1:
                    size = ''
                else:
                    size = '=%s' % r
                if x1 > x2:
                    attr = 'left' + size
                else:
                    attr = 'right' + size
            elif x1 == x2:
                if y1 > y2:
                    attr = 'up' + size
                else:
                    attr = 'down' + size
            else:
                angle = degrees(atan2(y2 - y1, x2 - x1))
                attr = 'rotate=%s' % angle
            parts.append('; ' + attr)

            elts.append(' '.join(parts))
        return '\n'.join(elts)


class Cursor:

    def __init__(self, ui, x, y):

        self.layer = ui.cursor_layer
        self.patch = None
        self.x = x
        self.y = y

    def draw(self, color='red'):

        self.patch = self.layer.stroke_filled_circle(self.x, self.y,
                                                     color, alpha=0.5)

    def remove(self):

        self.patch.remove()


class Cursors(list):

    def debug(self):

        for cursor in self:
            print('%s, %s' % (cursor.x, cursor.y))

    def remove(self):

        while self != []:
            cursor = self.pop()
            cursor.remove()


class Layer:

    def __init__(self, ax):

        self.ax = ax
        self.color = 'black'

    def stroke_line(self, xstart, ystart, xend, yend):

        self.ax.plot((xstart, xend), (ystart, yend), '-', color=self.color)

    def stroke_arc(self, xstart, ystart, foo, r, theta):
        pass

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

    def stroke_filled_circle(self, x, y, color='black', alpha=0.5):

        patch = patches.Circle((x, y), 0.5, fc=color, alpha=alpha)
        self.ax.add_patch(patch)
        return patch

    def remove(self, patch):

        self.ax.remove(patch)


class History(list):

    def add(self, cptname, x1, y1, x2, y2):

        self.append('A %s %s %s %s %s' % (cptname, x1, y1, x2, y2))

    def add_node(self, x, y):

        self.append('N %s %s' % (x, y))

    def debug(self):

        for elt in self:
            print(elt)

    def load(self, filename):

        for _ in range(len(self)):
            self.pop()

        with open(filename, 'r') as fhandle:
            lines = fhandle.read_lines(self)

        for line in lines:
            self.append(line)

    def play(self, ui):

        for action in self:
            parts = action.split(' ')
            if parts[0] == 'A':
                ui.add(parts[1], float(parts[2]), float(parts[3]),
                       float(parts[4]))
            elif parts[0] == 'M':
                ui.move(float(parts[1]), float(parts[2]))
            elif parts[0] == 'R':
                ui.rotate(float(parts[1]))
            elif parts[0] == 'S':
                ui.select(parts[1])
            else:
                raise RuntimeError('Unknown command ' + action)

    def move(self, xshift, yshift):

        self.append('M %f %f' % (xshift, yshift))

    def rotate(self, angle):

        self.append('R %f' % angle)

    def save(self, filename):

        with open(filename, 'w') as fhandle:
            fhandle.write_lines(self)

    def select(self, cptname):

        self.append('S %s' % cptname)

    def unselect(self):

        self.append('U')


class ModelBase:

    def __init__(self, ui):

        self.components = Components()
        self.history = History()
        self.ui = ui

    # Drawing commands
    def add(self, cptname, x1, y1, x2, y2):
        # Create component from name

        if cptname == 'C':
            cpt = Capacitor(0)
        elif cptname == 'L':
            cpt = Inductor(0)
        elif cptname == 'R':
            cpt = Resistor(0)
        elif cptname == 'W':
            cpt = Wire()
        else:
            # TODO
            return

        cpt.ports[0].position = (x1, y1)
        cpt.ports[1].position = (x2, y2)

        self.components.add(cpt)

        cpt.__draw_on__(self, self.ui.component_layer)
        self.ui.refresh()

        self.select(cptname)

    def draw(self, cptname, **kwargs):
        if cptname is None:
            return
        cptname.draw(**kwargs)

    def move(self, xshift, yshift):
        # TODO
        pass

    def rotate(self, angle):
        # TODO
        pass

    def select(self, cptname):
        pass

    def unselect(self):
        pass


class ModelMPH(ModelBase):

    def __init__(self, ui, step):

        super(ModelMPH, self).__init__(ui)

        self.cursors = Cursors()
        self.step = step

    def unselect(self):

        self.cursors.remove()
        self.ui.refresh()

    def draw_cursor(self, x, y):

        step = self.step
        x = (x + 0.5 * step) // step * step
        y = (y + 0.5 * step) // step * step

        cursor = Cursor(self.ui, x, y)

        if len(self.cursors) == 0:
            cursor.draw('red')
            self.cursors.append(cursor)

        elif len(self.cursors) == 1:
            cursor.draw('blue')
            self.cursors.append(cursor)

        elif len(self.cursors) == 2:
            self.cursors[0].remove()
            self.cursors[1].remove()

            r1 = (x - self.cursors[0].x)**2 + (y - self.cursors[0].y)**2
            r2 = (x - self.cursors[1].x)**2 + (y - self.cursors[1].y)**2

            if r2 > r1:
                self.cursors[1] = cursor
                self.cursors[0].draw('red')
            else:
                self.cursors[0] = self.cursors[1]
                self.cursors[1] = cursor
                self.cursors[1].draw('red')
            cursor.draw('blue')

        self.ui.refresh()

    # User interface commands
    def on_select(self, cptname):
        self.select(cptname)

    def on_unselect(self):
        self.history.unselect()
        self.unselect()

    def on_add_node(self, x, y):

        self.draw_cursor(x, y)
        self.history.add_node(x, y)

    def on_add_cpt(self, cptname):

        if len(self.cursors) < 2:
            # TODO
            return
        x1 = self.cursors[0].x
        y1 = self.cursors[0].y
        x2 = self.cursors[1].x
        y2 = self.cursors[1].y

        self.history.add(cptname, x1, y1, x2, y2)
        self.add(cptname, x1, y1, x2, y2)

    def on_move(self, xshift, yshift):
        self.history.move(xshift, yshift)
        self.move(xshift, yshift)

    def on_rotate(self, angle):
        self.history.rotate(angle)
        self.rotate(angle)

    def on_undo(self):
        command = self.history.pop()
        print(command)
        # TODO, undo...

    def on_debug(self):

        print('Netlist.........')
        print(self.components.as_sch(self.step))
        print('Cursors.........')
        self.cursors.debug()
        print('Components......')
        self.components.debug()
        print('History.........')
        self.history.debug()

    def on_key(self, key):

        if key == 'ctrl+c':
            self.ui.quit()
        elif key == 'ctrl+d':
            self.on_debug()
        elif key == 'escape':
            self.on_unselect()
        elif key in ('c', 'l', 'r', 'w'):
            self.on_add_cpt(key.upper())

    def on_left_click(self, x, y):

        self.on_add_node(x, y)

    def on_right_click(self, x, y):

        pass

    def on_close(self):

        self.ui.quit()


class EditorBase:
    pass


class MatplotlibEditor(EditorBase):

    FIG_WIDTH = 6
    FIG_HEIGHT = 4

    XSIZE = 60
    YSIZE = 40

    STEP = 2
    SCALE = 0.25

    def __init__(self):

        super(MatplotlibEditor, self).__init__()
        self.model = ModelMPH(self, self.STEP)

        rcParams['keymap.xscale'].remove('L')
        rcParams['keymap.xscale'].remove('k')
        rcParams['keymap.yscale'].remove('l')

        rcParams['toolbar'] = 'toolmanager'
        self.fig, self.ax = subplots(1, figsize=(self.FIG_WIDTH,
                                                 self.FIG_HEIGHT))
        self.fig.subplots_adjust(left=0.1, top=0.9, bottom=0.1, right=0.9)
        self.ax.axis('equal')

        # Tools to add to the toolbar
        tools = [
            # ['Annotate', AnnotateTool, self.comment],
            # ['Play', PlayTool, self.play],
            # ['Extract', ExtractTool, self.extract],
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

        sys.exit()
