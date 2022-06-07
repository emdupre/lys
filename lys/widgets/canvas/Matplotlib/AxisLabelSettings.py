from ..interface import CanvasAxisLabel, CanvasTickLabel


class _MatplotlibAxisLabel(CanvasAxisLabel):
    def _setAxisLabel(self, axis, text):
        axes = self.canvas().getAxes(axis)
        if axis in ['Left', 'Right']:
            axes.get_yaxis().get_label().set_text(text)
        else:
            axes.get_xaxis().get_label().set_text(text)

    def _setAxisLabelVisible(self, axis, b):
        axes = self.canvas().getAxes(axis)
        if axis in ['Left', 'Right']:
            axes.get_yaxis().get_label().set_visible(b)
        else:
            axes.get_xaxis().get_label().set_visible(b)

    def _setAxisLabelCoords(self, axis, pos):
        axes = self.canvas().getAxes(axis)
        if axis in ['Left', 'Right']:
            axes.get_yaxis().set_label_coords(pos, 0.5)
        else:
            axes.get_xaxis().set_label_coords(0.5, pos)

    def _setAxisLabelFont(self, axis, family, size, color):
        axes = self.canvas().getAxes(axis)
        if axis in ['Left', 'Right']:
            axes.get_yaxis().get_label().set_family(family)
            axes.get_yaxis().get_label().set_size(size)
            axes.get_yaxis().get_label().set_color(color)
        else:
            axes.get_xaxis().get_label().set_family(family)
            axes.get_xaxis().get_label().set_size(size)
            axes.get_xaxis().get_label().set_color(color)


class _MatplotlibTickLabel(CanvasTickLabel):
    def _setTickLabelVisible(self, axis, tf, mirror=False):
        axes = self.canvas().getAxes(axis)
        if (axis == 'Right' and not mirror) or (axis == 'Left' and mirror):
            axes.get_yaxis().set_tick_params(labelright=tf)
        if (axis == 'Left' and not mirror) or (axis == 'Right' and mirror):
            axes.get_yaxis().set_tick_params(labelleft=tf)
        if (axis == 'Top' and not mirror) or (axis == 'Bottom' and mirror):
            axes.get_xaxis().set_tick_params(labeltop=tf)
        if (axis == 'Bottom' and not mirror) or (axis == 'Top' and mirror):
            axes.get_xaxis().set_tick_params(labelbottom=tf)

    def _setTickLabelFont(self, axis, family, size, color):
        axes = self.canvas().getAxes(axis)
        if axis in ['Left', 'Right']:
            for tick in axes.get_xticklabels():
                tick.set_fontname(family)
            axis = 'x'
        else:
            for tick in axes.get_yticklabels():
                tick.set_fontname(family)
            axis = 'y'
        axes.tick_params(which='major', labelsize=size, labelcolor=color, axis=axis)
