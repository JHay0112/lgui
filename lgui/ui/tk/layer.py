import matplotlib.patches as patches
from math import degrees


class Layer:

    def __init__(self, ax):

        self.ax = ax
        self.color = 'black'

    def stroke_line(self, xstart, ystart, xend, yend):

        return self.ax.plot((xstart, xend), (ystart, yend), '-',
                            color=self.color)

    def stroke_arc(self, x, y, r, theta1, theta2):

        r *= 2
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
