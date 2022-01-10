#!/usr/bin/env python
import weakref
from PyQt5.QtGui import *

from lys.widgets import LysSubWindow

from .CanvasBase import *


class ExtendCanvas(FigureCanvasBase):
    keyPressed = pyqtSignal(QKeyEvent)
    clicked = pyqtSignal(float, float)
    savedDict = {}

    def __init__(self, dpi=100):
        super().__init__(dpi=dpi)
        self.setFocusPolicy(Qt.StrongFocus)
        self.modf = weakref.WeakMethod(self.defModFunc)
        self.moveText = False
        self.textPosStart = None
        self.cursorPosStart = None
        self.initCanvas.emit()

    def __GlobalToAxis(self, x, y, ax):
        loc = self.__GlobalToRatio(x, y, ax)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_ax = xlim[0] + (xlim[1] - xlim[0]) * loc[0]
        y_ax = ylim[0] + (ylim[1] - ylim[0]) * loc[1]
        return [x_ax, y_ax]

    def __GlobalToRatio(self, x, y, ax):
        ran = ax.get_position()
        x_loc = (x - ran.x0 * self.width()) / ((ran.x1 - ran.x0) * self.width())
        y_loc = (y - ran.y0 * self.height()) / ((ran.y1 - ran.y0) * self.height())
        return [x_loc, y_loc]

    def OnMouseUp(self, event):
        if self.moveText == True and event.button == 1:
            self.moveText = False
        return super().OnMouseUp(event)

    def OnMouseMove(self, event):
        if self.moveText == True:
            mode = self.getAnnotPositionMode(self.annotindex)[0]
            if mode == 'Absolute':
                d = self.__GlobalToRatio(event.x, event.y, self.axes)
            elif mode == 'Relative':
                d = self.__GlobalToAxis(event.x, event.y, self.axes)
            self.setAnnotPosition(self.annotindex, (self.textPosStart[0] + d[0] - self.cursorPosStart[0], self.textPosStart[1] + d[1] - self.cursorPosStart[1]))
            self.draw()
        else:
            return super().OnMouseMove(event)

    def OnMouseDown(self, event):
        if event.dblclick:
            self.modf()(self)
            return super().OnMouseDown(event)
            self.annot = self.getPickedAnnotation()
            if self.annot is not None:
                self.modf()(self, 'Annot.')
                self.setSelectedAnnotations(self.annot.get_zorder())
                return super().OnMouseDown(event)
            axis = self.getPickedAxis()
            if axis is not None:
                self.modf()(self, 'Axis')
                # self.setSelectedAxis(self.__findAxis(axis))
                return super().OnMouseDown(event)
            line = self.getPickedLine()
            if line is not None:
                self.modf()(self, 'Lines')
                w = self.getWaveDataFromArtist(line)
                self.setSelectedIndexes(1, w.id)
                return super().OnMouseDown(event)
            image = self.getPickedImage()
            if image is not None:
                self.modf()(self, 'Images')
                w = self.getWaveDataFromArtist(image)
                self.setSelectedIndexes(2, w.id)
                return super().OnMouseDown(event)
        elif event.button == 1:
            self.clicked.emit(*self.__GlobalToAxis(event.x, event.y, self.getAxes("BottomLeft")))
            return super().OnMouseDown(event)
            self.annot = self.getPickedAnnotation()
            if self.annot is not None:
                self.annotindex = self.annot.get_zorder()
                self.moveText = True
                mode = self.getAnnotPositionMode(self.annotindex)[0]
                if mode == 'Absolute':
                    self.cursorPosStart = self.__GlobalToRatio(event.x, event.y, self.axes)
                elif mode == 'Relative':
                    self.cursorPosStart = self.__GlobalToAxis(event.x, event.y, self.axes)
                self.textPosStart = self.getAnnotPosition(self.annotindex)[0]
                return
            else:
                return super().OnMouseDown(event)
        else:
            return super().OnMouseDown(event)

    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        if e.key() == Qt.Key_A:
            for i in self.getRGBs():
                i.setColorRange()
            for i in self.getImages():
                i.setColorRange()
        self.keyPressed.emit(e)

    def defModFunc(self, canvas, tab='Axis'):
        from lys import ModifyWindow, Graph
        parent = self.parentWidget()
        while(parent is not None):
            if isinstance(parent, LysSubWindow):
                mod = ModifyWindow(self, parent, showArea=isinstance(parent, Graph))
                mod.selectTab(tab)
                break
            parent = parent.parentWidget()

    def SaveSetting(self, type):
        dict = {}
        self.SaveAsDictionary(dict)
        ExtendCanvas.savedDict[type] = dict[type]
        return dict[type]

    def LoadSetting(self, type, obj=None):
        if obj is not None:
            d = {}
            d[type] = obj
            self.LoadFromDictionary(d)
        elif type in ExtendCanvas.savedDict:
            d = {}
            d[type] = ExtendCanvas.savedDict[type]
            self.LoadFromDictionary(d)
