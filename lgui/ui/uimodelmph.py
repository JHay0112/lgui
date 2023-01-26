from .uimodelbase import UIModelBase


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


class UIModelMPH(UIModelBase):

    def __init__(self, ui):

        super(UIModelMPH, self).__init__(ui)

        self.cursors = Cursors()

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

    def unselect(self):

        self.cursors.remove()
        self.ui.refresh()

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

    def on_analyze(self):

        if self.edit_mode:
            self.edit_mode = False
            self.cursors.remove()
            self.ui.refresh()

        self.analyze()

    def on_close(self):

        self.ui.quit()

    def on_debug(self):

        print('Netlist.........')
        print(self.components.as_sch(self.STEP))
        print('Cursors.........')
        self.cursors.debug()
        print('Components......')
        self.components.debug()
        print('Nodes...........')
        self.nodes.debug()
        print('History.........')
        self.history.debug()

    def on_edit(self):

        self.edit_mode = True

    def on_export(self):

        filename = self.ui.export_file_dialog(self.filename)
        if filename == '':
            return
        self.export(filename)

    def on_move(self, xshift, yshift):
        self.history.move(xshift, yshift)
        self.move(xshift, yshift)

    def on_rotate(self, angle):
        self.history.rotate(angle)
        self.rotate(angle)

    def on_select(self, cptname):
        self.select(cptname)

    def on_unselect(self):
        self.history.unselect()
        self.unselect()

    def on_key(self, key):

        if key == 'ctrl+c':
            self.ui.quit()
        elif key == 'ctrl+d':
            self.on_debug()
        elif key == 'ctrl+l':
            self.on_load()
        elif key == 'ctrl+s':
            self.on_save()
        elif key == 'ctrl+v':
            self.on_view()
        elif key == 'escape':
            self.on_unselect()
        elif key in ('c', 'i', 'l', 'r', 'v', 'w'):
            self.on_add_cpt(key.upper())

    def on_left_click(self, x, y):

        cpt = self.components.closest(x, y)
        node = self.nodes.closest(x, y)

        # TODO: in future want to be able to edit node attributes as
        # well as place cursor on node.  Perhaps have an inspect mode?
        # The easiest option is to use a different mouse button but
        # this not available in browser implementations.

        if node:
            print(node)

        if cpt and node:
            print('Selected both node %s and cpt %s' % (node, cpt))

        if cpt is None:
            if self.edit_mode:
                self.on_add_node(x, y)
        else:
            # TODO, select component
            print(cpt.cname)
            if not self.edit_mode:
                # Better to have a tooltip
                self.ui.show_message_dialog(str(self.cct[cpt.cname].v))

    def on_load(self):

        filename = self.ui.open_file_dialog()
        if filename == '':
            return
        self.load(filename)

    def on_right_click(self, x, y):

        pass

    def on_save(self):

        filename = self.ui.save_file_dialog(self.filename)
        if filename == '':
            return
        self.save(filename)

    def on_undo(self):
        command = self.history.pop()
        print(command)
        # TODO, undo...

    def on_view(self):

        self.view()
