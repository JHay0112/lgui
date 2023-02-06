from ..components import Capacitor, Component, CurrentSource, Inductor, \
    Port, Resistor, VoltageSource, Wire, VCVS, CCVS, VCCS, CCCS
from ..annotation import Annotation
from ..annotations import Annotations
from ..nodes import Nodes
from ..components import Components
from .preferences import Preferences
from lgui import __version__
from copy import copy
from numpy import array


class UIModelBase:

    STEP = 2
    SCALE = 0.25

    component_map = {
        'c': ('Capacitor', Capacitor),
        'i': ('Current source', CurrentSource),
        'l': ('Inductor', Inductor),
        'r': ('Resistor', Resistor),
        'v': ('Voltage source', VoltageSource),
        'w': ('Wire', Wire),
        'e': ('VCVS', VCVS),
        'f': ('CCCS', CCCS),
        'g': ('VCCS', VCCS),
        'h': ('CCVS', CCVS),
        'p': ('Port', Port)
    }

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
        self.history = []
        self.clipped = None

    @ property
    def cct(self):

        if self._cct is not None:
            return self._cct

        from lcapy import Circuit

        if len(self.components) == 0:
            self.exception('No circuit defined')

        try:
            sch = self.components.as_sch(self.STEP)
        except Exception as e:
            self.exception(e)

        if self.ground_node is None:
            # Add dummy ground node
            sch += 'W %s 0\n' % self.nodes[0].name

        self._cct = Circuit(sch)

        try:
            self._cct[0]
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

        return self._cct

    @ property
    def cpt_selected(self):

        return isinstance(self.selected, Component)

    def cpt_delete(self, cpt):

        self.select(None)

        redraw = True
        try:
            # This should also delete the annotations.
            cpt.undraw()
            redraw = False
        except AttributeError:
            pass

        self.components.remove(cpt)
        for node in cpt.nodes:
            self.nodes.remove(node, cpt)

        if redraw:
            self.ui.clear()
            self.redraw()

    def cpt_draw(self, cpt):

        cpt.__draw_on__(self, self.ui.component_layer)

        label_cpts = self.preferences.label_cpts

        if cpt.TYPE in ('O', 'P', 'W'):
            label_cpts = 'none'

        name = cpt.cname
        value = cpt.value
        if value is None:
            value = ''

        if label_cpts == 'name+value':
            if name != value:
                label = name + '=' + value
            else:
                label = name
        elif label_cpts == 'value':
            if value != '':
                label = value
            else:
                label = name
        elif label_cpts == 'name':
            label = name
        elif label_cpts == 'none':
            label = ''
        else:
            raise RuntimeError('Unhandled label_cpts=' + label_cpts)

        if label != '':
            ann = Annotation(self.ui, *cpt.label_position, label)
            ann.draw(fontsize=18)
            cpt.annotations.append(ann)

        draw_nodes = self.preferences.draw_nodes
        if draw_nodes != 'none':
            for node in cpt.nodes:
                if node.port:
                    self.node_draw(node)
                    continue

                if draw_nodes == 'connections' and node.count < 3:
                    continue
                if draw_nodes == 'alpha' and not node.name[0].isalpha():
                    continue
                if draw_nodes == 'primary' and not node.is_primary:
                    continue
                self.node_draw(node)

        label_nodes = self.preferences.label_nodes
        if label_nodes != 'none':
            for node in cpt.nodes:
                pos = array(node.position)
                pos[0] += 0.3
                pos[1] += 0.3
                ann = Annotation(self.ui, *pos, node.name)
                ann.draw(fontsize=18)
                cpt.annotations.append(ann)

    def cpt_make(self, cptname):

        cptname = cptname.lower()

        try:
            cpt_class = self.component_map[cptname][1]
        except IndexError:
            self.exception('Unhandled component ' + cptname)
            return None

        if cpt_class is None:
            self.exception('Unimplemented component ' +
                           self.component_map[cptname][0])
            return None

        if cptname in ('p', 'w'):
            cpt = cpt_class()
        else:
            cpt = cpt_class(None)
        self.invalidate()
        return cpt

    def cpt_create(self, cpt, x1, y1, x2, y2):

        node1 = self.nodes.make(x1, y1, None, cpt)
        self.nodes.add(node1)

        node2 = self.nodes.make(x2, y2, None, cpt)
        self.nodes.add(node2)

        self.components.add_auto(cpt, node1, node2)

        self.cpt_draw(cpt)

        self.select(cpt)
        self.dirty = True

        self.history.append((cpt, 'A'))

    def cpt_find(self, n1, n2):

        cpt2 = None
        for cpt in self.components:
            if (cpt.nodes[0].name == n1 and cpt.nodes[1].name == n2):
                cpt2 = cpt
                break
        if cpt2 is None:
            self.exception(
                'Cannot find a component with nodes %s and %s' % (n1, n2))
        return cpt2

    def create(self, cptname, x1, y1, x2, y2):

        cpt = self.cpt_make(cptname)
        if cpt is None:
            return
        self.cpt_create(cpt, x1, y1, x2, y2)

    def circuit(self):

        from lcapy import Circuit

        s = self.schematic()

        cct = Circuit(s)
        return cct

    def cut(self, cpt):

        self.delete(cpt)
        self.clipped = cpt

    def delete(self, cpt):

        self.cpt_delete(cpt)
        self.history.append((cpt, 'D'))

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

        vcs = []
        elements = cct.elements
        for elt in elements.values():
            if elt.type == 'XX':
                # Ignore directives
                continue

            cpt = self.cpt_make(elt.type)
            nodes = []
            for m, node1 in enumerate(elt.nodes[0:2]):

                x1 = sch.nodes[node1.name].pos.x + offsetx
                y1 = sch.nodes[node1.name].pos.y + offsety
                node = self.nodes.make(x1, y1, node1.name, cpt)
                self.nodes.add(node)
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
            elif elt.type in ('E', 'G'):
                # TODO, handle opamp keyword
                cpt.value = elt.args[0]
                vcs.append((cpt, elt.nodes[2].name, elt.nodes[3].name))
            elif elt.type in ('F', 'H'):
                cpt.value = elt.args[0]
                cpt.control = elt.args[1]

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
            self.cpt_draw(cpt)

        for cpt, n1, n2 in vcs:
            cpt.control = self.cpt_find(n1, n2)

    def move(self, xshift, yshift):
        # TODO
        pass

    def paste(self, x1, y1, x2, y2):

        if self.clipped is None:
            return
        cpt = copy(self.clipped)
        self.cpt_create(cpt, x1, y1, x2, y2)

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

        try:
            s += self.components.as_sch(self.STEP)
        except Exception as e:
            self.exception(e)

        # Note, need a newline so string treated as a netlist string
        s += ';' + self.preferences.schematic_preferences() + '\n'
        return s

    def inspect_admittance(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].Y
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s admittance' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def inspect_current(self, cpt):

        # TODO: FIXME for wire current
        try:
            self.last_expr = self.cct[cpt.cname].i
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s current' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def inspect_impedance(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].Z
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s impe' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def inspect_norton_admittance(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].dpY
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s Norton admittance' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def inspect_thevenin_impedance(self, cpt):

        try:
            self.last_expr = self.cct[cpt.cname].dpZ
            self.ui.show_expr_dialog(self.last_expr,
                                     '%s Thevenin impedance' % cpt.cname)
        except (AttributeError, ValueError, RuntimeError) as e:
            self.exception(e)

    def inspect_voltage(self, cpt):

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

    @ property
    def ground_node(self):

        return self.node_find('0')

    def node_draw(self, node):

        if node.port:
            self.ui.component_layer.stroke_circle(
                *node.position, self.preferences.node_size,
                color=self.preferences.node_color, alpha=1)
        else:
            self.ui.component_layer.stroke_filled_circle(
                *node.position, self.preferences.node_size,
                color=self.preferences.node_color, alpha=1)

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
            self.cpt_draw(cpt)

    def undo(self):

        if self.history == []:
            return
        cpt, op = self.history.pop()
        if op == 'D':
            self.components.add(cpt, cpt.cname, *cpt.nodes)
            self.cpt_draw(cpt)
            self.select(cpt)
        else:
            self.cpt_delete(cpt)
