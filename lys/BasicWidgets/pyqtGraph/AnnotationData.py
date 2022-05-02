import pyqtgraph as pg
import numpy as np
from LysQt.QtCore import Qt, pyqtSignal, QRectF
from LysQt.QtGui import QColor, QTransform
from ..CanvasInterface import CanvasAnnotation, LineAnnotation, InfiniteLineAnnotation, RectAnnotation, RegionAnnotation, CrossAnnotation, FreeRegionAnnotation

_styles = {'solid': Qt.SolidLine, 'dashed': Qt.DashLine, 'dashdot': Qt.DashDotLine, 'dotted': Qt.DotLine, 'None': Qt.NoPen}


class _PyqtgraphLineAnnotation(LineAnnotation):
    """Implementation of LineAnnotation for pyqtgraph"""

    def _initialize(self, pos, axis):
        self._obj = pg.LineSegmentROI(pos)
        self._obj.setPen(pg.mkPen(color='#000000'))
        self._obj.sigRegionChanged.connect(lambda obj: self.setPosition([[obj.pos()[0] + obj.listPoints()[0][0], obj.pos()[1] + obj.listPoints()[0][1]], [obj.pos()[0] + obj.listPoints()[1][0], obj.pos()[1] + obj.listPoints()[1][1]]]))
        self.canvas().getAxes(axis).addItem(self._obj)

    def _setPosition(self, pos):
        self._obj.setPos(0, 0)
        self._obj.getHandles()[0].setPos(*pos[0])
        self._obj.getHandles()[1].setPos(*pos[1])

    def _setLineColor(self, color):
        self._obj.pen.setColor(QColor(color))

    def _setLineStyle(self, style):
        self._obj.pen.setStyle(_styles[style])

    def _setLineWidth(self, width):
        self._obj.pen.setWidth(width)

    def _setZOrder(self, z):
        self._obj.setZValue(z)

    def _setVisible(self, visible):
        self._obj.setVisible(visible)


class _PyqtgraphInfiniteLineAnnotation(InfiniteLineAnnotation):
    """Implementation of InfiniteLineAnnotation for pyqtgraph"""

    def _initialize(self, pos, orientation, axis):
        if orientation == 'vertical':
            self._obj = pg.InfiniteLine(pos, 90)
        else:
            self._obj = pg.InfiniteLine(pos, 0)
        self._obj.setMovable(True)
        self._obj.setPen(pg.mkPen(color='#000000'))
        self._obj.setVisible(True)
        self._obj.sigPositionChanged.connect(self._posChanged)
        self.canvas().getAxes(axis).addItem(self._obj)

    def _posChanged(self, line):
        self.setPosition(line.value())

    def _setPosition(self, pos):
        self._obj.setValue(pos)

    def _setLineColor(self, color):
        self._obj.pen.setColor(QColor(color))

    def _setLineStyle(self, style):
        self._obj.pen.setStyle(_styles[style])

    def _setLineWidth(self, width):
        self._obj.pen.setWidth(width)

    def _setZOrder(self, z):
        self._obj.setZValue(z)

    def _setVisible(self, visible):
        self._obj.setVisible(visible)


class _PyqtgraphRectAnnotation(RectAnnotation):
    """Implementation of RectAnnotation for pyqtgraph"""

    def _initialize(self, pos, size, axis):
        self._obj = pg.RectROI(pos, size)
        self._obj.setPen(pg.mkPen(color='#000000'))
        self._obj.sigRegionChanged.connect(lambda roi: self.setRegion([[roi.pos()[0], roi.pos()[0] + roi.size()[0]], [roi.pos()[1], roi.pos()[1] + roi.size()[1]]]))
        self.canvas().getAxes(axis).addItem(self._obj)

    def _setRegion(self, region):
        self._obj.setPos((region[0][0], region[1][0]))
        self._obj.setSize((region[0][1] - region[0][0], region[1][1] - region[1][0]))

    def _setLineColor(self, color):
        self._obj.pen.setColor(QColor(color))

    def _setLineStyle(self, style):
        self._obj.pen.setStyle(_styles[style])

    def _setLineWidth(self, width):
        self._obj.pen.setWidth(width)

    def _setZOrder(self, z):
        self._obj.setZValue(z)

    def _setVisible(self, visible):
        self._obj.setVisible(visible)


class _PyqtgraphRegionAnnotation(RegionAnnotation):
    """Implementation of RegionAnnotation for pyqtgraph"""

    __list = {"horizontal": pg.LinearRegionItem.Horizontal, "vertical": pg.LinearRegionItem.Vertical}

    def _initialize(self, region, orientation, axis):
        self._obj = pg.LinearRegionItem(region, orientation=self.__list[orientation])
        self._obj.sigRegionChanged.connect(lambda roi: self.setRegion(roi.getRegion()))
        self.canvas().getAxes(axis).addItem(self._obj)

    def _setRegion(self, region):
        self._obj.setRegion(region)

    def _setLineColor(self, color):
        self._obj.lines[0].pen.setColor(QColor(color))
        self._obj.lines[1].pen.setColor(QColor(color))

    def _setLineStyle(self, style):
        self._obj.lines[0].pen.setStyle(_styles[style])
        self._obj.lines[1].pen.setStyle(_styles[style])

    def _setLineWidth(self, width):
        self._obj.lines[0].pen.setWidth(width)
        self._obj.lines[1].pen.setWidth(width)

    def _setZOrder(self, z):
        self._obj.setZValue(z)

    def _setVisible(self, visible):
        self._obj.setVisible(visible)


class _PyqtgraphFreeRegionAnnotation(FreeRegionAnnotation):
    """Implementation of FreeRegionAnnotation for pyqtgraph"""

    def _initialize(self, region, width, axis):
        self.__flg = False
        pos1, pos2 = np.array(region[0]), np.array(region[1])
        d = pos2 - pos1
        v = np.array([-d[1], d[0]])
        pos = pos1 - width * v / np.linalg.norm(v) / 2
        self._obj = pg.RectROI(pos, size=(np.linalg.norm(d), width), angle=np.angle(d[0] + 1j * d[1], deg=True), movable=True, rotatable=True)
        handles = self._obj.getHandles()
        for h in handles:
            h.hide()
        self._obj.addScaleRotateHandle((0, 0.5), (1, 0.5))
        self._obj.addScaleRotateHandle((1, 0.5), (0, 0.5))
        self._obj.sigRegionChanged.connect(self._regionChanged)
        self.canvas().getAxes(axis).addItem(self._obj)

    def _regionChanged(self, roi):
        if self.__flg:
            return
        self.__flg = True
        p = np.array([roi.pos()[0], roi.pos()[1]])
        d = np.array((np.cos(roi.angle() / 180 * np.pi), np.sin(roi.angle() / 180 * np.pi)))
        v = np.array((-d[1], d[0]))
        self.setRegion([tuple(p + v * roi.size()[1] / 2), tuple(p + roi.size()[0] * d + v * roi.size()[1] / 2)])
        self.__flg = False

    def _setRegion(self, region):
        pos1, pos2 = np.array(region[0]), np.array(region[1])
        d = pos2 - pos1
        v = np.array([-d[1], d[0]])
        pos = pos1 - self.getWidth() * v / np.linalg.norm(v) / 2
        self._obj.setPos(pos)
        self._obj.setSize((np.linalg.norm(d), self.getWidth()))
        self._obj.setAngle(np.angle(d[0] + 1j * d[1], deg=True))

    def _setWidth(self, width):
        self._obj.setSize((self._obj.size()[0], width))

    def _setLineColor(self, color):
        self._obj.pen.setColor(QColor(color))

    def _setLineStyle(self, style):
        self._obj.pen.setStyle(_styles[style])

    def _setLineWidth(self, width):
        self._obj.pen.setWidth(width)

    def _setZOrder(self, z):
        self._obj.setZValue(z)

    def _setVisible(self, visible):
        self._obj.setVisible(visible)


class _PyqtgraphCrossAnnotation(CrossAnnotation):
    """Implementation of CrossAnnotation for pyqtgraph"""

    def _initialize(self, position, axis):
        self._obj = _CrosshairItem(position)
        self._obj.sigRegionChanged.connect(lambda roi: self.setPosition(roi.getPosition()))
        self.canvas().getAxes(axis).addItem(self._obj)

    def _setPosition(self, pos):
        self._obj.lines[0].setValue(pos[1])
        self._obj.lines[1].setValue(pos[0])

    def _setLineColor(self, color):
        self._obj.lines[0].pen.setColor(QColor(color))
        self._obj.lines[1].pen.setColor(QColor(color))

    def _setLineStyle(self, style):
        self._obj.lines[0].pen.setStyle(_styles[style])
        self._obj.lines[1].pen.setStyle(_styles[style])

    def _setLineWidth(self, width):
        self._obj.lines[0].pen.setWidth(width)
        self._obj.lines[1].pen.setWidth(width)

    def _setZOrder(self, z):
        self._obj.setZValue(z)

    def _setVisible(self, visible):
        self._obj.setVisible(visible)


class _CrosshairItem(pg.GraphicsObject):
    sigRegionChangeFinished = pyqtSignal(object)
    sigRegionChanged = pyqtSignal(object)

    def __init__(self, values=(0, 1), pen=None):
        super().__init__()
        self.bounds = QRectF()
        self.blockLineSignal = False
        self.moving = False
        self.mouseHovering = False
        self._bounds = None
        self.lines = [pg.InfiniteLine(angle=0), pg.InfiniteLine(angle=90)]
        tr = QTransform()
        tr.scale(1, -1)
        self.lines[0].setTransform(tr)
        self.lines[1].setTransform(tr)
        for line in self.lines:
            line.setParentItem(self)
            line.sigPositionChangeFinished.connect(self.lineMoveFinished)
        self.lines[0].sigPositionChanged.connect(lambda: self.lineMoved(0))
        self.lines[1].sigPositionChanged.connect(lambda: self.lineMoved(1))
        self.setMovable(True)
        self.setPosition(values)

    def getPosition(self):
        r = (self.lines[1].value(), self.lines[0].value())
        return r

    def setPosition(self, pos):
        if self.lines[0].value() == pos[0] and self.lines[1].value() == pos[1]:
            return
        self.blockLineSignal = True
        self.lines[0].setValue(pos[0])
        self.blockLineSignal = False
        self.lines[1].setValue(pos[1])
        self.lineMoved(0)
        self.lineMoved(1)
        self.lineMoveFinished()

    def setMovable(self, m):
        for l in self.lines:
            l.setMovable(m)
        self.movable = m
        self.setAcceptHoverEvents(m)

    def boundingRect(self):
        br = self.viewRect()  # bounds of containing ViewBox mapped to local coords.
        br = self.lines[0].boundingRect() & self.lines[1].boundingRect()
        br = br.normalized()

        if self._bounds != br:
            self._bounds = br
            self.prepareGeometryChange()

        return br

    def paint(self, p, *args):
        # p.drawEllipse(self.boundCircle())
        pass

    def lineMoved(self, i):
        if self.blockLineSignal:
            return
        self.prepareGeometryChange()
        self.sigRegionChanged.emit(self)

    def lineMoveFinished(self):
        self.sigRegionChangeFinished.emit(self)


class _PyqtgraphAnnotation(CanvasAnnotation):
    """Implementation of CanvasAnnotation for pyqtgraph"""

    def _addLineAnnotation(self, pos, axis):
        return _PyqtgraphLineAnnotation(self.canvas(), pos, axis)

    def _addInfiniteLineAnnotation(self, pos, type, axis):
        return _PyqtgraphInfiniteLineAnnotation(self.canvas(), pos, type, axis)

    def _addRectAnnotation(self, *args, **kwargs):
        return _PyqtgraphRectAnnotation(self.canvas(), *args, **kwargs)

    def _addRegionAnnotation(self, *args, **kwargs):
        return _PyqtgraphRegionAnnotation(self.canvas(), *args, **kwargs)

    def _addFreeRegionAnnotation(self, *args, **kwargs):
        return _PyqtgraphFreeRegionAnnotation(self.canvas(), *args, **kwargs)

    def _addCrossAnnotation(self, *args, **kwargs):
        return _PyqtgraphCrossAnnotation(self.canvas(), *args, **kwargs)


"""


class TextAnnotationCanvas(AnnotatableCanvas, TextAnnotationCanvasBase):
    def __init__(self, dpi):
        super().__init__(dpi)
        TextAnnotationCanvasBase.__init__(self)

    def _makeObject(self, text, axis, appearance, id, x, y, box, size, picker):
        return pg.TextItem(text=text)

    def _setText(self, obj, txt):
        obj.setText(txt)

    def _getText(self, obj):
        return obj.textItem.toPlainText()

    def SaveAsDictionary(self, dictionary, path):
        AnnotatableCanvas.SaveAsDictionary(self, dictionary, path)
        TextAnnotationCanvasBase.SaveAsDictionary(self, dictionary, path)

    def LoadFromDictionary(self, dictionary, path):
        TextAnnotationCanvasBase.LoadFromDictionary(self, dictionary, path)
        super().LoadFromDictionary(dictionary, path)


class AnnotationEditableCanvas(TextAnnotationCanvas):
    def __init__(self, dpi):
        super().__init__(dpi)
        self.fontChanged.connect(self.__onFontChanged)

    def loadAnnotAppearance(self):
        super().loadAnnotAppearance()
        data = self.getAnnotations('text')
        for d in data:
            if 'Font' in d.appearance:
                self._setFont(d, FontInfo.FromDict(d.appearance['Font']))

    def __onFontChanged(self, name):
        list = self.getAnnotations('text')
        for l in list:
            if 'Font_def' in l.appearance:
                if l.appearance['Font_def'] is not None and name in [l.appearance['Font_def'], 'Default']:
                    f = self.getCanvasFont(name)
                    l.obj.set_family(f.family)
                    l.obj.set_size(f.size)
                    l.obj.set_color(f.color)
        self.draw()

    def _setFont(self, annot, font):
        if not isinstance(font, FontInfo):
            f = self.getCanvasFont(font)
        else:
            f = font
        annot.obj.set_family(f.family)
        annot.obj.set_size(f.size)
        annot.obj.set_color(f.color)
        annot.appearance['Font'] = f.ToDict()

    @saveCanvas
    def setAnnotationFont(self, indexes, font='Default', default=False):
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            self._setFont(l, font)
            if default and not isinstance(font, FontInfo):
                l.appearance['Font_def'] = font
            else:
                l.appearance['Font_def'] = None

    def getAnnotationFontDefault(self, indexes):
        res = []
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            if 'Font_def' in l.appearance:
                if l.appearance['Font_def'] is not None:
                    res.append(True)
                else:
                    res.append(False)
            else:
                res.append(False)
        return res

    def getAnnotationFont(self, indexes):
        res = []
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            res.append(FontInfo(l.obj.get_family()[0], l.obj.get_size(), l.obj.get_color()))
        return res


class AnnotationMovableCanvas(AnnotationEditableCanvas):
    def saveAnnotAppearance(self):
        super().saveAnnotAppearance()
        data = self.getAnnotations('text')
        for d in data:
            t = d.obj.get_transform()
            if t == d.obj.axes.transData:
                d.appearance['PositionMode'] = 'Relative'
            else:
                d.appearance['PositionMode'] = 'Absolute'
            d.appearance['Position'] = d.obj.get_position()

    def loadAnnotAppearance(self):
        super().loadAnnotAppearance()
        data = self.getAnnotations('text')
        for d in data:
            if 'PositionMode' in d.appearance:
                self.setAnnotPositionMode([d.id], d.appearance['PositionMode'])
                self.setAnnotPosition([d.id], d.appearance['Position'])

    @saveCanvas
    def setAnnotPosition(self, indexes, xy):
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            l.obj.set_position(xy)
        self._emitAnnotationSelected()

    def getAnnotPosition(self, indexes):
        res = []
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            res.append(l.obj.get_position())
        return res

    @saveCanvas
    def setAnnotPositionMode(self, indexes, mode):
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            old_p = l.obj.get_position()
            old_t = l.obj.get_transform()
            ax = l.obj.axes
            ylim = ax.get_ylim()
            xlim = ax.get_xlim()
            if mode == 'Absolute':
                l.obj.set_transform(self.axes.transAxes)
                if old_t == self.axes.transData:
                    l.obj.set_position(((old_p[0] - xlim[0]) / (xlim[1] - xlim[0]), (old_p[1] - ylim[0]) / (ylim[1] - ylim[0])))
            elif mode == 'Relative':
                l.obj.set_transform(self.axes.transData)
                if old_t == self.axes.transAxes:
                    l.obj.set_position((xlim[0] + old_p[0] * (xlim[1] - xlim[0]), ylim[0] + old_p[1] * (ylim[1] - ylim[0])))

    def getAnnotPositionMode(self, indexes):
        res = []
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            t = l.obj.get_transform()
            if t == self.axes.transAxes:
                res.append('Absolute')
            else:
                res.append('Relative')
        return res


class AnnotationBoxAdjustableCanvas(AnnotationMovableCanvas):
    def saveAnnotAppearance(self):
        super().saveAnnotAppearance()
        data = self.getAnnotations('text')
        for d in data:
            d.appearance['BoxStyle'] = self.getAnnotBoxStyle([d.id])[0]
            d.appearance['BoxFaceColor'] = self.getAnnotBoxColor([d.id])[0]
            d.appearance['BoxEdgeColor'] = self.getAnnotBoxEdgeColor([d.id])[0]

    def loadAnnotAppearance(self):
        super().loadAnnotAppearance()
        data = self.getAnnotations('text')
        for d in data:
            if 'BoxStyle' in d.appearance:
                self.setAnnotBoxStyle([d.id], d.appearance['BoxStyle'])
                self.setAnnotBoxColor([d.id], d.appearance['BoxFaceColor'])
                self.setAnnotBoxEdgeColor([d.id], d.appearance['BoxEdgeColor'])

    @saveCanvas
    def setAnnotBoxStyle(self, indexes, style):
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            box = l.obj.get_bbox_patch()
            if style == 'none':
                if box is not None:
                    box.set_visible(False)
            else:
                l.obj.set_bbox(dict(boxstyle=style))
                self.setAnnotBoxColor([l.id], 'w')
                self.setAnnotBoxEdgeColor([l.id], 'k')

    def _checkBoxStyle(self, box):
        if isinstance(box, BoxStyle.Square):
            return 'square'
        elif isinstance(box, BoxStyle.Circle):
            return 'circle'
        elif isinstance(box, BoxStyle.DArrow):
            return 'darrow'
        elif isinstance(box, BoxStyle.RArrow):
            return 'rarrow'
        elif isinstance(box, BoxStyle.LArrow):
            return 'larrow'
        elif isinstance(box, BoxStyle.Round):
            return 'round'
        elif isinstance(box, BoxStyle.Round4):
            return 'round4'
        elif isinstance(box, BoxStyle.Roundtooth):
            return 'roundtooth'
        elif isinstance(box, BoxStyle.Sawtooth):
            return 'sawtooth'
        return 'none'

    def getAnnotBoxStyle(self, indexes):
        res = []
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            box = l.obj.get_bbox_patch()
            if box is None:
                res.append('none')
                continue
            if not box.get_visible():
                res.append('none')
                continue
            else:
                res.append(self._checkBoxStyle(box.get_boxstyle()))
                continue
        return res

    @saveCanvas
    def setAnnotBoxColor(self, indexes, color):
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            box = l.obj.get_bbox_patch()
            if box is not None:
                box.set_facecolor(color)

    def getAnnotBoxColor(self, indexes):
        res = []
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            box = l.obj.get_bbox_patch()
            if box is None:
                res.append('w')
            else:
                res.append(box.get_facecolor())
        return res

    @saveCanvas
    def setAnnotBoxEdgeColor(self, indexes, color):
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            box = l.obj.get_bbox_patch()
            if box is not None:
                box.set_edgecolor(color)

    def getAnnotBoxEdgeColor(self, indexes):
        res = []
        list = self.getAnnotationFromIndexes(indexes)
        for l in list:
            box = l.obj.get_bbox_patch()
            if box is None:
                res.append('k')
            else:
                res.append(box.get_edgecolor())
        return res

"""
