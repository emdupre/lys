import warnings
import numpy as np
from lys.errors import NotImplementedWarning

from .SaveCanvas import saveCanvas
from .WaveData import WaveData


class VectorData(WaveData):
    """
    Interface to access vector data in the canvas.

    Instance of VectorData is automatically generated by display or append methods.
    """

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self.appearanceSet.connect(self._loadAppearance)

    def __setAppearance(self, key, value):
        self.appearance[key] = value

    def __getAppearance(self, key, default=None):
        return self.appearance.get(key, default)

    @saveCanvas
    def setPivot(self, pivot):
        """
        Set pivot point of the vector plot.

        Args:
            pivot('tail' or 'middle' or 'tip'): The pivot point
        """
        self._setPivot(pivot)
        self.__setAppearance('VectorPivot', pivot)

    def getPivot(self):
        """
        Get pivot point of the vector plot.

        Return:
            str: string that indicate pivot point.
        """
        return self.__getAppearance('VectorPivot')

    @saveCanvas
    def setScale(self, scale='auto'):
        """
        Set the scale of the vector.

        Args:
            scale(float or 'auto'): The scale of the vector.
        """
        if scale == 'auto':
            scale = self.getAutoScale()
        self._setScale(scale)
        self.__setAppearance('VectorScale', scale)

    def getScale(self):
        """
        Get the scale of the vector.

        Return:
            float: The scale of the vector.
        """
        return self.__getAppearance('VectorScale')

    def getAutoScale(self):
        """
        Get the automatically-calculated scale of the vector.

        Return:
            float: The scale of the vector.
        """
        return np.max(np.abs(self.filteredWave.data)) * 10

    @saveCanvas
    def setWidth(self, width):
        """
        Set the width of the vector.

        Args:
            width(float): The width of the vector.
        """
        self._setWidth(width)
        self.__setAppearance('VectorWidth', width)

    def getWidth(self):
        """
        Get the width of the vector.

        Return:
            float: The width of the vector.
        """
        return self.__getAppearance('VectorWidth')

    @saveCanvas
    def setColor(self, color):
        """
        Set the color of the vector.

        Args:
            color(str): The color of the vector such as '#ff0000'.
        """
        self._setColor(color)
        self.__setAppearance('VectorColor', color)

    def getColor(self):
        """
        Get the color of the vector.

        Args:
            str: The color of the vector such as '#ff0000'.
        """
        return self.__getAppearance('VectorColor')

    def _loadAppearance(self, appearance):
        self.setColor(appearance.get('VectorColor', '#000000'))
        self.setScale(appearance.get('VectorScale', 'auto'))
        self.setWidth(appearance.get('VectorWidth', 3))
        self.setPivot(appearance.get('VectorPivot', 'tail'))

    def _setPivot(self, pivot):
        warnings.warn(str(type(self)) + " does not implement _setPivot(pivot) method.", NotImplementedWarning)

    def _setScale(self, scale):
        warnings.warn(str(type(self)) + " does not implement _setScale(scale) method.", NotImplementedWarning)

    def _setWidth(self, width):
        warnings.warn(str(type(self)) + " does not implement _setWidth(width) method.", NotImplementedWarning)

    def _setColor(self, color):
        warnings.warn(str(type(self)) + " does not implement _setColor(color) method.", NotImplementedWarning)
