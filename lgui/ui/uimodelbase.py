from ..components import Capacitor, Component, CurrentSupply, Inductor, \
    Resistor, VoltageSupply, Wire
from math import sqrt, degrees, atan2


class Annotation:

    def __init__(self, ui, x, y, text):

        self.layer = ui.cursor_layer
        self.x = x
        self.y = y
        self.text = text
        self.patch = None

    @property
    def position(self):

        return self.x, self.y

    def draw(self, **kwargs):

        self.patch = self.layer.text(self.x, self.y, self.text, **kwargs)

    def remove(self):

        if self.patch:
            self.patch.remove()


class Annotations(list):

    def __init__(self):

        super(Annotations, self).__init__(self)

    def add(self, annotation):

        self.append(annotation)

    def remove(self):

        while self != []:
            self.pop().remove()


class Node:

    def __init__(self, x, y, name):

        self.x = x
        self.y = y
        self.name = name

    @property
    def position(self):

        return self.x, self.y

    def __str__(self):

        return '%s@(%s, %s)' % (self.name, self.x, self.y)


class Nodes(list):

    def __init__(self):

        super(Nodes, self).__init__(self)

    def add(self, node):

        if not isinstance(node, Node):
            raise TypeError('Not a Node object')
        if node not in self:
            self.append(node)

    def by_name(self, name):

        for node in self:
            if node.name == name:
                return node
        return None

    def by_position(self, position):

        x, y = position

        for node in self:
            if node.x == x and node.y == y:
                return node
        return None

    def clear(self):

        while self != []:
            self.pop()

    def closest(self, x, y):

        for node in self:
            x1, y1 = node.position
            rsq = (x1 - x)**2 + (y1 - y)**2
            if rsq < 0.1:
                return node
        return None

    def debug(self):

        for node in self:
            print(node)

    def make(self, x, y, name=None):

        node = self.by_position((x, y))
        if node is not None:
            if name is not None and node.name != name:
                raise ValueError('Node name conflict %s and %s' %
                                 (node.name, name))
            return node

        if name is None:
            # Ensure there is a 0 node; later on let user define it
            num = 0
            while True:
                name = str(num)
                if not self.by_name(name):
                    break
                num += 1

        node = Node(x, y, name)
        return node


class Components(list):

    def __init__(self):

        super(Components, self).__init__(self)
        self.kinds = {}

    def add(self, cpt, *nodes):

        if cpt.TYPE not in self.kinds:
            self.kinds[cpt.TYPE] = 0
        self.kinds[cpt.TYPE] += 1

        # Hack, update component class to have this attribute
        cpt.cname = cpt.TYPE + '%d' % self.kinds[cpt.TYPE]

        # Hack for drawing
        cpt.nodes = nodes
        cpt.ports[0].position = nodes[0].position
        cpt.ports[1].position = nodes[1].position

        self.append(cpt)

    def clear(self):

        while self != []:
            # TODO erase component
            self.pop()

    def debug(self):

        for cpt in self:
            # Need to redow Component class to show node names as well.
            print(cpt)

    def as_sch(self, step):

        elts = []
        for cpt in self:
            parts = [cpt.cname]
            for node in cpt.nodes:
                parts.append(node.name)

            # Later need to handle schematic kind attributes.
            if cpt.kind is not None:
                parts.append(cpt.kinds[cpt.kind])

            if cpt.value is not None:
                parts.append(cpt.value)

            if cpt.initial_value is not None:
                parts.append(cpt.initial_value)

            x1, y1 = cpt.nodes[0].position
            x2, y2 = cpt.nodes[1].position
            r = sqrt((x1 - x2)**2 + (y1 - y2)**2) / step

            if r == 1:
                size = ''
            else:
                size = '=%s' % r

            if y1 == y2:
                if x1 > x2:
                    attr = 'left' + size
                else:
                    attr = 'right' + size
            elif x1 == x2:
                if y1 > y2:
                    attr = 'down' + size
                else:
                    attr = 'up' + size
            else:
                angle = degrees(atan2(y2 - y1, x2 - x1))
                attr = 'rotate=%s' % angle
            parts.append('; ' + attr)

            elts.append(' '.join(parts))
        return '\n'.join(elts)

    def closest(self, x, y):

        for cpt in self:
            x1, y1 = cpt.nodes[0].position
            x2, y2 = cpt.nodes[1].position
            xmid = (x1 + x2) / 2
            ymid = (y1 + y2) / 2
            rsq = (xmid - x)**2 + (ymid - y)**2
            ssq = (x2 - x1)**2 + (y2 - y1)**2
            if rsq < 0.1 * ssq:
                return cpt
        return None


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

    @property
    def cpt_selected(self):

        return isinstance(self.selected, Component)

    # Drawing commands
    def add(self, cptname, x1, y1, x2, y2):

        # Create component from name
        if cptname == 'C':
            cpt = Capacitor(None)
        elif cptname == 'I':
            cpt = CurrentSupply(None)
        elif cptname == 'L':
            cpt = Inductor(None)
        elif cptname == 'R':
            cpt = Resistor(None)
        elif cptname == 'V':
            cpt = VoltageSupply(None)
        elif cptname == 'W':
            cpt = Wire()
        else:
            # TODO
            return

        node1 = self.nodes.make(x1, y1)
        self.nodes.add(node1)

        node2 = self.nodes.make(x2, y2)
        self.nodes.add(node2)

        self.components.add(cpt, node1, node2)

        cpt.__draw_on__(self, self.ui.component_layer)
        self.ui.refresh()

        self.select(cptname)

    def circuit(self):

        from lcapy import Circuit

        s = self.components.as_sch(self.STEP)
        # Note, need a newline so string treated as a netlist string
        s += '\n; draw_nodes=connections'
        cct = Circuit(s)
        return cct

    def analyze(self):

        self.cct = self.circuit()
        try:
            self.cct[0]
        except (AttributeError, ValueError) as e:
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

        # TODO: handle wails of protest if something wrong
        sch._positions_calculate()

        width, height = sch.width * self.STEP,  sch.height * self.STEP
        offsetx, offsety = self.snap((self.ui.XSIZE - width) / 2,
                                     (self.ui.YSIZE - height) / 2)

        elements = sch.elements
        for elt in elements.values():
            # TODO: allow component name and value
            self.add(elt.type, elt.nodes[0].pos.x + offsetx,
                     elt.nodes[0].pos.y + offsety,
                     elt.nodes[-1].pos.x + offsetx,
                     elt.nodes[-1].pos.y + offsety)

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
