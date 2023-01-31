from ..components import Capacitor, Component, CurrentSource, Inductor, \
    Resistor, VoltageSource, Wire
from ..annotation import Annotation
from ..annotations import Annotations
from ..nodes import Nodes
from ..components import Components


class History(list):

    def add(self, cptname, x1, y1, x2, y2):

        self.append('A %s %s %s %s %s' % (cptname, x1, y1, x2, y2))

    def add_node(self, x, y):

        self.append('N %s %s' % (x, y))

    def debug(self):

        s = ''
        for elt in self:
            s += str(elt) + '\n'
        return s

    def load(self, filename):

        for _ in range(len(self)):
            self.pop()

        with open(filename, 'r') as fhandle:
            lines = fhandle.read_lines(self)

        for line in lines:
            self.append(line)

    def play(self, ui):

        # for action in self:
        #     parts = action.split(' ')
        #     if parts[0] == 'A':
        #         ui.add(parts[1], float(parts[2]), float(parts[3]),
        #                float(parts[4]))
        #     elif parts[0] == 'M':
        #         ui.move(float(parts[1]), float(parts[2]))
        #     elif parts[0] == 'R':
        #         ui.rotate(float(parts[1]))
        #     elif parts[0] == 'S':
        #         ui.select(parts[1])   # FIXME, pass x, y
        #     else:
        #         raise RuntimeError('Unknown command ' + action)
        pass

    def move(self, xshift, yshift):

        self.append('M %f %f' % (xshift, yshift))

    def rotate(self, angle):

        self.append('R %f' % angle)

    def save(self, filename):

        with open(filename, 'w') as fhandle:
            fhandle.write_lines(self)

    def select(self, thing):

        self.append('S %s' % thing)

    def unselect(self):

        self.append('U')


class UIModelBase:

    STEP = 2
    SCALE = 0.25

    def __init__(self, ui):

        self.components = Components()
        self.nodes = Nodes()
        self.history = History()
        self.ui = ui
        self.edit_mode = True
        self.cct = None
        self.filename = ''
        self.voltage_annotations = Annotations()
        self.selected = None
        self.last_expr = None

    @property
    def cpt_selected(self):

        return isinstance(self.selected, Component)

    def cpt_make(self, cptname):

        # Create component from name
        if cptname == 'C':
            cpt = Capacitor(None)
        elif cptname == 'I':
            cpt = CurrentSource(None)
        elif cptname == 'L':
            cpt = Inductor(None)
        elif cptname == 'R':
            cpt = Resistor(None)
        elif cptname == 'V':
            cpt = VoltageSource(None)
        elif cptname == 'W':
            cpt = Wire()
        else:
            self.exception('Unhandled component ' + cptname)
        return cpt

    # Drawing commands
    def cpt_add(self, cptname, x1, y1, x2, y2):

        cpt = self.cpt_make(cptname)

        node1 = self.nodes.make(x1, y1)
        self.nodes.add(node1)

        node2 = self.nodes.make(x2, y2)
        self.nodes.add(node2)

        self.components.add_auto(cpt, node1, node2)

        cpt.__draw_on__(self, self.ui.component_layer)
        self.ui.refresh()

        self.select(cpt)

    def circuit(self):

        from lcapy import Circuit

        s = self.components.as_sch(self.STEP)
        # Note, need a newline so string treated as a netlist string
        s += '\n; draw_nodes=connections'
        cct = Circuit(s)
        return cct

    def analyze(self):

        from lcapy import Circuit

        if len(self.components) == 0:
            self.exception('No circuit defined')

        sch = self.components.as_sch(self.STEP)
        if self.ground_node is None:
            # Add dummy ground node
            sch += 'W %s 0\n' % self.nodes[0].name

        self.cct = Circuit(sch)

        try:
            self.cct[0]
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def draw(self, cpt, **kwargs):

        if cpt is None:
            return
        cpt.draw(**kwargs)

    def export(self, filename):

        cct = self.circuit()
        cct.draw(filename)

    def load(self, filename):

        from lcapy import Circuit

        self.filename = filename

        # TODO: FIXME
        # self.ui.component_layer.clear()
        self.components.clear()

        cct = Circuit(filename)
        sch = cct.sch

        try:
            sch._positions_calculate()
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

        width, height = sch.width * self.STEP,  sch.height * self.STEP
        offsetx, offsety = self.snap((self.ui.XSIZE - width) / 2,
                                     (self.ui.YSIZE - height) / 2)

        for node in sch.nodes.values():
            x1 = node.pos.x + offsetx
            y1 = node.pos.y + offsety
            node1 = self.nodes.make(x1, y1, node.name)
            self.nodes.add(node1)

        elements = cct.elements
        for elt in elements.values():
            cpt = self.cpt_make(elt.type)
            cpt.cname = elt.name
            cpt.nodes = []
            for m, node in enumerate(elt.nodes):
                node = self.node_find(node.name)
                cpt.nodes.append(node)
                cpt.ports[m].position = node.position
            if elt.type == 'R':
                cpt.value = elt.args[0]
            elif elt.type in ('C', 'L'):
                cpt.value = elt.args[0]
                cpt.initial_value = elt.args[1]
            elif elt.type in ('V', 'I'):
                cpt.value = elt.args[0]
                if elt.keyword[0] is not None:
                    for key, val in cpt.kinds.items():
                        if val == elt.keyword[1]:
                            cpt.kind = key

            elif elt.type in ('W', 'O', 'P'):
                pass
            else:
                self.exception('Unhandled component ' + elt)

            self.components.add(cpt)
            cpt.__draw_on__(self, self.ui.component_layer)
        self.ui.refresh()

    def move(self, xshift, yshift):
        # TODO
        pass

    def rotate(self, angle):
        # TODO
        pass

    def save(self, filename):

        s = self.components.as_sch(self.STEP)

        with open(filename, 'w') as fhandle:
            fhandle.write(s)

    def show_cpt_current(self, cpt):

        # TODO: FIXME for wire current
        try:
            self.last_expr = self.cct[cpt.cname].i
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s current' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def show_cpt_voltage(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].v
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s potential difference' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def show_node_voltage(self, node):

        try:
            self.last_expr = self.cct[node.name].v
            self.ui.show_expr_dialog(self.last_expr,
                                     'Node %s potential' % node.name)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def select(self, thing):

        self.selected = thing

    def snap(self, x, y):

        step = self.STEP
        x = (x + 0.5 * step) // step * step
        y = (y + 0.5 * step) // step * step
        return x, y

    def unselect(self):
        pass

    def view(self):

        cct = self.circuit()
        cct.draw()

    def voltage_annotate(self, cpt):

        ann1 = Annotation(self.ui, *cpt.nodes[0].position, '+')
        ann2 = Annotation(self.ui, *cpt.nodes[1].position, '-')

        self.voltage_annotations.add(ann1)
        self.voltage_annotations.add(ann2)
        ann1.draw(color='red', fontsize=40)
        ann2.draw(color='blue', fontsize=40)
        self.ui.refresh()

    @property
    def ground_node(self):

        return self.node_find('0')

    def node_find(self, nodename):

        for node in self.nodes:
            if node.name == nodename:
                return node
        return None
