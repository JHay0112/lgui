from ..components import Capacitor, Component, CurrentSource, Inductor, \
    Resistor, VoltageSource, Wire
from ..annotation import Annotation
from ..annotations import Annotations
from ..nodes import Nodes
from ..components import Components
from .preferences import Preferences
from lgui import __version__


class UIModelBase:

    STEP = 2
    SCALE = 0.25

    def __init__(self, ui):

        self.components = Components()
        self.nodes = Nodes()
        self.ui = ui
        self._cct = None
        self.filename = ''
        self.voltage_annotations = Annotations()
        self.selected = None
        self.last_expr = None
        self.preferences = Preferences()
        self.dirty = False
        self.discard_buffer = []

    @property
    def cct(self):

        if self._cct is not None:
            return self._cct

        from lcapy import Circuit

        if len(self.components) == 0:
            self.exception('No circuit defined')

        sch = self.components.as_sch(self.STEP)
        if self.ground_node is None:
            # Add dummy ground node
            sch += 'W %s 0\n' % self.nodes[0].name

        self._cct = Circuit(sch)

        try:
            self._cct[0]
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

        return self._cct

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
        self.invalidate()
        return cpt

    def create(self, cptname, x1, y1, x2, y2):

        cpt = self.cpt_make(cptname)

        node1 = self.nodes.make(x1, y1)
        self.nodes.add(node1)

        node2 = self.nodes.make(x2, y2)
        self.nodes.add(node2)

        self.components.add_auto(cpt, node1, node2)

        cpt.__draw_on__(self, self.ui.component_layer)

        self.select(cpt)
        self.dirty = True

    def circuit(self):

        from lcapy import Circuit

        s = self.schematic()

        cct = Circuit(s)
        return cct

    def delete(self, cpt):

        redraw = True
        try:
            cpt.undraw()
            redraw = False
        except AttributeError:
            pass

        self.components.remove(cpt)
        self.discard_buffer.append(cpt)

        if redraw:
            self.ui.clear()
            self.redraw()

    def draw(self, cpt, **kwargs):

        if cpt is None:
            return
        cpt.draw(**kwargs)

    def export(self, filename):

        cct = self.circuit()
        cct.draw(filename)

    def invalidate(self):

        self._cct = None

    def load(self, filename):

        from lcapy import Circuit

        self.filename = filename

        self.components.clear()

        cct = Circuit(filename)
        sch = cct.sch

        try:
            # This will fail if have detached circuits.
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
            if elt.type == 'XX':
                # Ignore directives
                continue

            cpt = self.cpt_make(elt.type)
            nodes = []
            for m, node in enumerate(elt.nodes):
                node = self.node_find(node.name)
                nodes.append(node)
                # Hack
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

            attrs = []
            for opt, val in elt.opts.items():
                if opt in ('left', 'right', 'up', 'down', 'rotate'):
                    continue

                def fmt(key, val):
                    if val == '':
                        return key
                    return '%s=%s' % (key, val)

                attrs.append(fmt(opt, val))
            cpt.attrs = ', '.join(attrs)
            cpt.opts = elt.opts

            self.components.add(cpt, elt.name, *nodes)
            cpt.__draw_on__(self, self.ui.component_layer)

    def move(self, xshift, yshift):
        # TODO
        pass

    def rotate(self, angle):
        # TODO
        pass

    def save(self, filename):

        s = self.schematic()

        with open(filename, 'w') as fhandle:
            fhandle.write(s)
        self.dirty = False

    def schematic(self):

        s = '# Created by lcapy-gui ' + __version__ + '\n'
        # TODO: save node positions
        s += self.components.as_sch(self.STEP)
        # Note, need a newline so string treated as a netlist string
        s += ';' + self.preferences.schematic_preferences() + '\n'
        return s

    def show_cpt_admittance(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].Y
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s admittance' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def show_cpt_current(self, cpt):

        # TODO: FIXME for wire current
        try:
            self.last_expr = self.cct[cpt.cname].i
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s current' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def show_cpt_impedance(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].Z
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s impe' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def show_cpt_norton_admittance(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].dpY
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s Norton admittance' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def show_cpt_thevenin_impedance(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].dpZ
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s Thevenin impedance' % cpt.cname)
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

    @property
    def ground_node(self):

        return self.node_find('0')

    def node_find(self, nodename):

        for node in self.nodes:
            if node.name == nodename:
                return node
        return None

    def redo(self):

        # TODO
        pass

    def redraw(self):

        for cpt in self.components:
            cpt.__draw_on__(self, self.ui.component_layer)

    def undo(self):

        if self.discard_buffer == []:
            return
        cpt = self.discard_buffer.pop()
        self.components.add(cpt, cpt.cname, *cpt.nodes)
        cpt.__draw_on__(self, self.ui.component_layer)
