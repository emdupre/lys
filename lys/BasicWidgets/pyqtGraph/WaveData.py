import copy
import warnings
import numpy as np
from matplotlib import cm
import pyqtgraph as pg

from LysQt.QtCore import Qt
from LysQt.QtGui import QColor, QTransform
from lys.errors import NotSupportedWarning
from ..CanvasInterface import LineData, ImageData, RGBData, VectorData, ContourData


class _PyqtgraphLine(LineData):
    """Implementation of LineData for pyqtgraph"""
    __styles = {'solid': Qt.SolidLine, 'dashed': Qt.DashLine, 'dashdot': Qt.DashDotLine, 'dotted': Qt.DotLine, 'None': Qt.NoPen}
    __symbols = {"circle": "o", "cross": "x", "tri_down": "t", "tri_up": "t1", "tri_right": "t2", "tri_left": "t3", "square": "s", "pentagon": "p", "hexagon": "h", "star": "star", "plus": "+", "diamond": "d", "None": None}

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self._obj = pg.PlotDataItem(x=wave.x, y=wave.data)
        canvas.getAxes(axis).addItem(self._obj)

    def _updateData(self):
        self._obj.setData(x=self.filteredWave.x, y=self.filteredWave.data)

    def _setVisible(self, visible):
        self._obj.setVisible(visible)

    def _setZ(self, z):
        self._obj.setZValue(z)

    def _getLinePen(self):
        p = self._obj.opts['pen']
        if isinstance(p, tuple):
            return pg.mkPen(color=p)
        else:
            return p

    def _getSymbolPen(self):
        p = self._obj.opts['symbolPen']
        if isinstance(p, tuple):
            return pg.mkPen(color=p)
        else:
            return p

    def _getSymbolBrush(self):
        p = self._obj.opts['symbolBrush']
        if isinstance(p, tuple):
            return pg.mkBrush(color=p)
        else:
            return p

    def _setColor(self, color):
        p = self._getSymbolPen()
        p.setColor(QColor(color))
        self._obj.setSymbolPen(p)
        self._obj.setPen(pg.mkPen(color=QColor(color)))

    def _setStyle(self, style):
        p = self._getLinePen()
        p.setStyle(self.__styles[style])
        self._obj.setPen(p)

    def _setWidth(self, width):
        p = self._getLinePen()
        p.setWidth(width)
        self._obj.setPen(p)

    def _setMarker(self, marker):
        if marker in self.__symbols:
            self._obj.setSymbol(self.__symbols[marker])
        else:
            warnings.warn("pyqtGraph does not support marker [" + marker + "]", NotSupportedWarning)

    def _setMarkerSize(self, size):
        self._obj.setSymbolSize(size * 2)

    def _setMarkerThick(self, thick):
        warnings.warn("pyqtGraph does not support set marker thick", NotSupportedWarning)
        # p = self._getSymbolPen()
        # p.setWidth(thick)
        # self._obj.setSymbolPen(p)
        # for refresh
        # p = self._getLinePen()
        # self._obj.setPen(p)

    def _setMarkerFilling(self, filling):
        if filling in ["filled", "full"]:
            c = self._getLinePen().color()
            b = pg.mkBrush(c)
            self._obj.setSymbolBrush(b)
        elif filling == "none":
            self._obj.setSymbolBrush(None)
        else:
            warnings.warn("pyqtGraph does not support filling [" + filling + "]", NotSupportedWarning)

    def _setZ(self, z):
        self._obj.setZValue(z)


def _calcExtent2D(wav):
    xstart = wav.x[0]
    xend = wav.x[len(wav.x) - 1]
    ystart = wav.y[0]
    yend = wav.y[len(wav.y) - 1]

    dx = (xend - xstart) / (len(wav.x) - 1)
    dy = (yend - ystart) / (len(wav.y) - 1)

    xstart = xstart - dx / 2
    xend = xend + dx / 2
    ystart = ystart - dy / 2
    yend = yend + dy / 2

    xmag = (xend - xstart) / len(wav.x)
    ymag = (yend - ystart) / len(wav.y)
    xshift = xstart
    yshift = ystart
    tr = QTransform()
    tr.scale(xmag, ymag)
    tr.translate(xshift / xmag, yshift / ymag)
    return tr


class _PyqtgraphImage(ImageData):
    """Implementation of LineData for pyqtgraph"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self._obj = pg.ImageItem(image=wave.data)
        self._obj.setTransform(_calcExtent2D(wave))
        canvas.getAxes(axis).addItem(self._obj)

    def _updateData(self):
        self._obj.setImage(self.filteredWave.data)
        self._obj.setTransform(_calcExtent2D(self.filteredWave))

    def _setVisible(self, visible):
        self._obj.setVisible(visible)

    def _setZ(self, z):
        self._obj.setZValue(z)

    def _setColormap(self, cmap):
        lut = self.__getColorLut(cmap, self.getGamma())
        self.__setColor(lut, self.getColorRange(), self.isLog())

    def _setGamma(self, gam):
        lut = self.__getColorLut(self.getColormap(), gam)
        self.__setColor(lut, self.getColorRange(), self.isLog())

    def _setColorRange(self, min, max):
        lut = self.__getColorLut(self.getColormap(), self.getGamma())
        self.__setColor(lut, (min, max), self.isLog())

    def _setLog(self, log):
        lut = self.__getColorLut(self.getColormap(), self.getGamma())
        self.__setColor(lut, self.getColorRange(), log)

    def __getColorLut(self, cmap, gamma):
        colormap = copy.deepcopy(cm.get_cmap(cmap))
        if hasattr(colormap, "set_gamma"):
            colormap.set_gamma(gamma)
        lut = np.array(colormap._lut * 255)
        return lut[0:lut.shape[0] - 3, :]

    def __setColor(self, lut, levels, log):
        if log:
            self._obj.setImage(np.log(self.filteredWave.data), lut=lut, levels=tuple(np.log(levels)))
        else:
            self._obj.setImage(self.filteredWave.data, lut=lut, levels=levels)

    def _setOpacity(self, opacity):
        self._obj.setOpacity(opacity)


class _PyqtgraphRGB(RGBData):
    """Implementation of RGBData for pyqtgraph"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self._obj = pg.ImageItem(image=wave.data, levels=(0, 1))
        self._obj.setTransform(_calcExtent2D(wave))
        canvas.getAxes(axis).addItem(self._obj)

    def _updateData(self):
        self._obj.setImage(self.filteredWave.data)
        self._obj.setTransform(_calcExtent2D(self.filteredWave))

    def _setVisible(self, visible):
        self._obj.setVisible(visible)

    def _setZ(self, z):
        self._obj.setZValue(z)


class _PyqtgraphContour(ContourData):
    """Implementation of ContourData for pyqtgraph"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self._obj = pg.IsocurveItem(data=wave.data, level=0.5, pen='r')
        self._obj.setTransform(_calcExtent2D(wave))
        canvas.getAxes(axis).addItem(self._obj)

    def _setVisible(self, visible):
        self._obj.setVisible(visible)

    def _setZ(self, z):
        self._obj.setZValue(z)
