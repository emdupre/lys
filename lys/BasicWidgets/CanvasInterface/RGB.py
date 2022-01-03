import warnings
import numpy as np
from lys.errors import NotImplementedWarning

from .SaveCanvas import saveCanvas
from .WaveData import WaveData


class RGBData(WaveData):
    """
    Interface to access rgb data in the canvas.

    Instance of RGBData is automatically generated by display or append methods.
    """

    def __init__(self, canvas, obj):
        super().__init__(canvas, obj)
        self.appearanceSet.connect(self._loadAppearance)

    def __setAppearance(self, key, value):
        self.appearance[key] = value

    def __getAppearance(self, key, default=None):
        return self.appearance.get(key, default)

    @saveCanvas
    def setColorRange(self, min='auto', max='auto'):
        """
        Set the color range of the image.

        Args:
            min(float or 'auto'): The minimum value of the range.
            max(float or 'auto'): The maximum value of the range.
        """
        self.__setAppearance('Range', (min, max))
        self.modified.emit(self)

    def getColorRange(self):
        """
        Get the color range of the image.

        Return:
            tuple of length 2: minimum and maximum value of the range.
        """
        return self.__getAppearance('Range')

    def getAutoColorRange(self):
        """
        Get the automarically-calculated color range of the image, which is used by :meth:`setColorRange` method.

        Return:
            tuple of length 2: minimum and maximum value of the range.
        """
        return (0, np.max(np.abs(self.wave.data)))

    @saveCanvas
    def setColorRotation(self, rot):
        """
        Rotate color map of the RGB image.

        Args:
            rot(float): The rotation.
        """
        self.__setAppearance('ColorRotation', rot)
        self.modified.emit(self)

    def getColorRotation(self):
        """
        Get color rotation of the RGB image.

        Return:
            float: The rotation.
        """
        return self.__getAppearance('ColorRotation')

    def _loadAppearance(self, appearance):
        self.setColorRange(*appearance.get('Range', self.getAutoColorRange()))
        self.setColorRotation(appearance.get('ColorRotation', 0))
