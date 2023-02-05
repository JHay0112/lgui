from .uimodelbase import UIModelBase


class Cursor:

    def __init__(self, ui, x, y):

        self.layer = ui.cursor_layer
        self.patch = None
        self.x = x
        self.y = y

    @property
    def position(self):

        return self.x, self.y

    def draw(self, color='red', radius=0.3):

        self.patch = self.layer.stroke_filled_circle(self.x, self.y,
                                                     radius,
                                                     color=color,
                                                     alpha=0.5)

    def remove(self):

        self.patch.remove()


class Cursors(list):

    def debug(self):

        s = ''
        for cursor in self:
            s += '%s, %s' % (cursor.x, cursor.y) + '\n'
        return s

    def remove(self):

        while self != []:
            self.pop().remove()

    def draw(self):

        if len(self) > 0:
            self[0].draw('red')
        if len(self) > 1:
            self[1].draw('blue')


class UIModelMPH(UIModelBase):

    def __init__(self, ui):

        super(UIModelMPH, self).__init__(ui)

        self.cursors = Cursors()
        self.node_cursor = None

        self.key_bindings = {
            'ctrl+c': self.on_copy,
            'ctrl+d': self.on_debug,
            'ctrl+e': self.on_export,
            'ctrl+h': self.on_help,
            'ctrl+i': self.on_inspect,
            'ctrl+n': self.on_new,
            'ctrl+o': self.on_load,
            'ctrl+s': self.on_save,
            'ctrl+u': self.on_view,
            'ctrl+v': self.on_paste,
            'ctrl+w': self.on_quit,
            'ctrl+x': self.on_cut,
            'ctrl+y': self.on_redo,
            'ctrl+z': self.on_undo,
            'escape': self.on_unselect,
            'delete': self.on_delete,
            'backspace': self.on_delete,
            '0': self.on_add_ground}

        self.key_bindings_with_key = {
            'c': self.on_add_cpt,
            'i': self.on_add_cpt,
            'l': self.on_add_cpt,
            'r': self.on_add_cpt,
            'v': self.on_add_cpt,
            'w': self.on_add_cpt}

    def draw_cursor(self, x, y):

        x, y = self.snap(x, y)

        cursor = Cursor(self.ui, x, y)

        if len(self.cursors) == 0:
            cursor.draw('red')
            self.cursors.append(cursor)

        elif len(self.cursors) == 1:
            cursor.draw('blue')
            self.cursors.append(cursor)

        elif len(self.cursors) == 2:

            rp = (x - self.cursors[0].x)**2 + (y - self.cursors[0].y)**2
            rm = (x - self.cursors[1].x)**2 + (y - self.cursors[1].y)**2

            if rm > rp:
                # Close to plus cursor so add new minus cursor
                self.cursors[1].remove()
                self.cursors[1] = cursor
                self.cursors[1].draw('blue')
            else:
                # Close to minus cursor so change minus cursor to plus cursor
                # and add new minus cursor
                self.cursors[0].remove()
                self.cursors[1].remove()
                self.cursors[0] = self.cursors[1]
                self.cursors[0].draw('red')
                self.cursors[1] = cursor
                self.cursors[1].draw('blue')

        self.ui.refresh()

    def draw_node_select(self, x, y):

        x, y = self.snap(x, y)

        if self.node_cursor is not None:
            self.node_cursor.remove()

        cursor = Cursor(self.ui, x, y)
        cursor.draw('black', 0.2)
        self.node_cursor = cursor
        self.ui.refresh()

    def exception(self, message):
        self.ui.show_info_dialog(message)

    def unselect(self):

        self.cursors.remove()
        self.ui.refresh()

    def on_add_node(self, x, y):

        self.draw_cursor(x, y)

    def on_add_cpt(self, cptname):

        cptname = cptname.upper()

        if len(self.cursors) < 2:
            # TODO
            return
        x1 = self.cursors[0].x
        y1 = self.cursors[0].y
        x2 = self.cursors[1].x
        y2 = self.cursors[1].y

        self.create(cptname, x1, y1, x2, y2)
        self.ui.refresh()

    def on_add_ground(self):

        if self.ground_node is not None:
            # Perhaps could rename old ground?
            self.exception('Ground node already defined')

        if len(self.cursors) == 0:
            return
        cursor = self.cursors[-1]
        x, y = cursor.position
        node = self.nodes.closest(x, y)
        if node is None:
            return
        node.name = '0'

        # TODO: annotate ground

    def on_close(self):

        self.ui.quit()

    def on_copy(self):

        pass

    def on_cpt_changed(self, cpt):

        self.invalidate()

    def on_debug(self):

        s = ''
        s += 'Netlist.........\n'
        s += self.schematic() + '\n'
        s += 'Nodes...........\n'
        s += self.nodes.debug() + '\n'
        s += 'Cursors.........\n'
        s += self.cursors.debug() + '\n'
        s += 'Selected.........\n'
        s += str(self.selected) + '\n'
        self.ui.show_message_dialog(s, 'Debug')

    def on_cut(self):

        if self.selected is None:
            return
        if not self.cpt_selected:
            return

        self.cut(self.selected)

        self.cursors.draw()

        self.ui.refresh()

    def on_delete(self):

        if self.selected is None:
            return
        if not self.cpt_selected:
            # Handle node deletion later
            return

        self.delete(self.selected)

        self.cursors.draw()

        self.ui.refresh()

    def on_describe(self):

        self.ui.show_message_dialog(self.cct.description(),
                                    title='Description')

    def on_export(self):

        filename = self.ui.export_file_dialog(self.filename)
        if filename == '':
            return
        self.export(filename)

    def on_help(self):

        self.ui.show_message_dialog("""
Click on the grid to place a red positive cursor then
click elsewhere to place a blue negative cursor.  Then enter c for a
capacitor, i for a current source, l for an inductor, r for a
resistor, v for a voltage source, etc.  The escape key will remove the
last defined cursor.

The attributes of a component (name, value, etc.) can be edited by
right clicking on a component.

The attributes of a node can be edited by right clicking on a
node.

Use Inspect (ctrl+i) to find the voltage across a component or the
current through a component.

A ground node to be defined by typing the 0 key; the ground node is
placed at the negative cursor.""", 'Help')

    def on_inspect(self):

        if not self.selected:
            return

        if not self.cpt_selected:
            return

        self.ui.show_inspect_dialog(self.selected,
                                    title=self.selected.cname)

    def on_inspect_current(self):

        if not self.selected or not self.cpt_selected:
            return

        self.inspect_current(self.selected)

    def on_inspect_norton_admittance(self):

        if not self.selected or not self.cpt_selected:
            return

        self.inspect_norton_admittance(self.selected)

    def on_inspect_thevenin_impedance(self):

        if not self.selected or not self.cpt_selected:
            return

        self.inspect_thevenin_impedance(self.selected)

    def on_inspect_voltage(self):

        if not self.selected or not self.cpt_selected:
            return

        self.inspect_voltage(self.selected)

    def on_left_click(self, x, y):

        self.on_select(x, y)

        if self.cpt_selected:
            cpt = self.selected
            if self.ui.debug:
                print('Selected ' + cpt.cname)
            self.cursors.remove()
            self.draw_cursor(*cpt.nodes[0].position)
            self.draw_cursor(*cpt.nodes[-1].position)
        else:
            if self.ui.debug:
                print('Add node at (%s, %s)' % (x, y))
            self.on_add_node(x, y)

    def on_left_double_click(self, x, y):

        self.on_right_click(x, y)

    def on_load(self):

        filename = self.ui.open_file_dialog()
        if filename == '':
            return

        model = self.ui.new()
        model.load(filename)
        self.ui.set_filename(filename)
        self.ui.refresh()

    def on_move(self, xshift, yshift):

        self.move(xshift, yshift)

    def on_netlist(self):

        netlist = []
        lines = self.circuit().netlist().split('\n')
        for line in lines:
            parts = line.split(';')
            netlist.append(parts[0].strip())
        s = '\n'.join(netlist)
        self.ui.show_message_dialog(s, 'Netlist')

    def on_new(self):

        self.ui.new()

    def on_right_click(self, x, y):

        self.on_select(x, y)
        if not self.selected:
            return

        if self.cpt_selected:
            self.ui.inspect_properties_dialog(self.selected,
                                              self.on_cpt_changed,
                                              title=self.selected.cname)
        else:
            self.ui.show_node_properties_dialog(self.selected,
                                                self.on_cpt_changed,
                                                title='Node ' +
                                                self.selected.name)

    def on_right_double_click(self, x, y):
        pass

    def on_rotate(self, angle):

        self.rotate(angle)

    def on_select(self, x, y):

        cpt = self.components.closest(x, y)
        node = self.nodes.closest(x, y)

        if cpt and node:
            self.ui.show_error(
                'Selected both node %s and cpt %s' % (node, cpt))
            return

        if cpt:
            self.select(cpt)
        elif node:
            self.select(node)
        else:
            self.select(None)

    def on_paste(self):

        if len(self.cursors) < 2:
            # TODO, place cpt where mouse is...
            return
        x1 = self.cursors[0].x
        y1 = self.cursors[0].y
        x2 = self.cursors[1].x
        y2 = self.cursors[1].y

        self.paste(x1, y1, x2, y2)
        self.ui.refresh()

    def on_preferences(self):

        self.ui.show_preferences_dialog(self.on_redraw)

    def on_redo(self):

        self.redo()
        self.ui.refresh()

    def on_redraw(self):

        self.ui.clear()
        self.redraw()
        self.ui.refresh()

    def on_quit(self):

        if self.dirty:
            self.ui.show_info_dialog('Schematic not saved')
        else:
            self.ui.quit()

    def on_save(self):

        filename = self.ui.save_file_dialog(self.filename)
        if filename == '':
            return
        self.save(filename)
        self.ui.save(filename)

    def on_undo(self):

        self.undo()
        self.ui.refresh()

    def on_unselect(self):

        self.unselect()

    def on_view(self):

        self.view()
