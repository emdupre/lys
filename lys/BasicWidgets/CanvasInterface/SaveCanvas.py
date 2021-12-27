import functools
import weakref
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


def saveCanvas(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], CanvasPart):
            canvas = args[0]._canvas
        else:
            canvas = args[0]
        if canvas.saveflg:
            res = func(*args, **kwargs)
        else:
            canvas.saveflg = True
            res = func(*args, **kwargs)
            canvas.Save()
            canvas.draw()
            canvas.saveflg = False
        return res
    return wrapper


def notSaveCanvas(func):
    @ functools.wraps(func)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], CanvasPart):
            canvas = args[0]._canvas
        else:
            canvas = args[0]
        saved = canvas.saveflg
        canvas.saveflg = True
        res = func(*args, **kwargs)
        canvas.saveflg = saved
        return res
    return wrapper


class CanvasPart(QObject):
    def __init__(self, canvas):
        super().__init__()
        self._canvas = canvas

    def canvas(self):
        return self._canvas


class BasicEventCanvasBase(object):
    deleted = pyqtSignal(object)

    def emitCloseEvent(self):
        self.deleted.emit(self)


class SavableCanvasBase(BasicEventCanvasBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saveflg = False
        self.savef = None

    def setSaveFunction(self, func):
        self.savef = weakref.WeakMethod(func)

    def Save(self):
        if self.savef is not None:
            self.savef()()

    def SaveAsDictionary(self, dictionary, path):
        pass

    def LoadFromDictionary(self, dictionary, path):
        pass

    def saveAppearance(self):
        pass

    def loadAppearance(self):
        pass


class DrawableCanvasBase(SavableCanvasBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self):
        try:
            self._draw()
        except Exception:
            pass

    def _draw(self):
        pass
