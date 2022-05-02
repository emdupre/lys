import warnings
from LysQt.QtCore import pyqtSignal
from lys.errors import NotImplementedWarning

from .CanvasBase import saveCanvas
from .AnnotationData import AnnotationWithLine


class RectAnnotation(AnnotationWithLine):
    """
    Interface to access rectangle annotations in canvas.

    *RectAnnotation* is usually generated by addRectAnnotation method in canvas.

    Several methods related to the appearance of line is inherited from :class:`.AnnotationData.AnnotationWithLine`

    Args:
        canvas(Canvas): canvas to which the line annotation is added.
        pos(length 2 sequence): The position of the rect annotation in the form of (x, y).
        size(length 2 sequence): The size of the rect annotation in the form of (width, height).
        axis('BottomLeft', 'BottomRight', 'TopLeft', or 'TopRight'): The axis to which the line annotation is added.

    Example::

        from lys import display
        g = display()
        rect = g.canvas.addRectAnnotation()
        rect.setLineColor("#ff0000")
    """
    regionChanged = pyqtSignal(list)
    """PyqtSignal that is emitted when the rectangle is changed."""

    def __init__(self, canvas, pos, size, axis):
        super().__init__(canvas, "test", axis)
        self._initialize(pos, size, axis)
        self._pos = pos
        self._size = size

    @saveCanvas
    def setRegion(self, region):
        """
        Set region of the rectangle.

        Args:
            region(2*2 sequence): The region of rectangle in the form of [(x1, x2), (y1, y2)]
        """
        if [tuple(region[0]), tuple(region[1])] != self.getRegion():
            x, y = min(*region[0]), min(*region[1])
            w, h = max(*region[0]) - min(*region[0]), max(*region[1]) - min(*region[1])
            self._pos = (x, y)
            self._size = (w, h)
            self._setRegion([(x, x + w), (y, y + h)])
            self.regionChanged.emit(self.getRegion())

    def getPosition(self):
        """
        Get position of the rectangle.

        Return:
            length 2 sequence: The position of rectangle in the form of (x, y)
        """
        return self._pos

    def getSize(self):
        """
        Get size of the rectangle.

        Return:
            length 2 sequence: The size of rectangle in the form of (width, height)
        """
        return self._size

    def getRegion(self):
        """
        Get region of the rectangle.

        Return:
            2*2 sequence: The region of rectangle in the form of [(x1, x2), (y1, y2)]
        """
        return [(self._pos[0], self._pos[0] + self._size[0]), (self._pos[1], self._pos[1] + self._size[1])]

    def _initialize(self, pos, size, axis):
        warnings.warn(str(type(self)) + " does not implement _initialize(pos, size, axis) method.", NotImplementedWarning)

    def _setRegion(self, region):
        warnings.warn(str(type(self)) + " does not implement _setRegion(pos) method.", NotImplementedWarning)
