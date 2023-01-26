from ..components import Capacitor, CurrentSupply, Inductor, \
    Resistor, VoltageSupply, Wire
from math import sqrt, degrees, atan2


class Nodes(list):

    def __init__(self):

        super(Nodes, self).__init__(self)

    def add(self, *nodes):

        for node in nodes:
            if node not in self:
                self.append(node)

    def clear(self):

        while self != []:
            self.pop()

    def debug(self):

        for node in self:
            print(node)

    def closest(self, x, y):

        for node in self:
            x1, y1 = node
            rsq = (x1 - x)**2 + (y1 - y)**2
            if rsq < 0.1:
                return node
        return None


class Components(list):

    def __init__(self):

        super(Components, self).__init__(self)
        self.kinds = {}

    def add(self, cpt):

        if cpt.TYPE not in self.kinds:
            self.kinds[cpt.TYPE] = 0
        self.kinds[cpt.TYPE] += 1
        # Hack, update component class to have this attribute
        cpt.cname = cpt.TYPE + '%d' % self.kinds[cpt.TYPE]
        self.append(cpt)

    def clear(self):

        while self != []:
            # TODO erase component
            self.pop()

    def debug(self):

        for cpt in self:
            print(cpt)

    def as_sch(self, step):

        nodes = {}

        node_count = 0

        elts = []
        for cpt in self:
            # Enumerate nodes (FIXME for node 0)
            for port in cpt.ports:
                if port.position not in nodes:
                    nodes[port.position] = node_count
                    node_count += 1

            parts = [cpt.cname]

            for port in cpt.ports:
                parts.append('%d' % nodes[port.position])

            if cpt.value is not None:
                parts.append(cpt.value)

            x1, y1 = cpt.ports[0].position
            x2, y2 = cpt.ports[1].position
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
            x1, y1 = cpt.ports[0].position
            x2, y2 = cpt.ports[1].position
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

    def select(self, cptname):

        self.append('S %s' % cptname)

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

        cpt.ports[0].position = x1, y1
        cpt.ports[1].position = x2, y2

        self.components.add(cpt)
        self.nodes.add(cpt.ports[0].position, cpt.ports[0].position)

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

        # TODO: centre nicely
        offsetx, offsety = self.snap(self.ui.XSIZE / 2, self.ui.YSIZE / 2)

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

    def select(self, cptname):
        pass

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
