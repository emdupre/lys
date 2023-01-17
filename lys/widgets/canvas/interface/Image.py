import numpy as np
import warnings

from lys.errors import NotImplementedWarning

from .CanvasBase import saveCanvas
from .WaveData import WaveData


class ImageData(WaveData):
    """
    Interface to access image data in the canvas.

    Instance of ImageData is automatically generated by display or append methods.

    Example::

        from lys import display
        im = display([[1,2,3],[4,5,6]])
        im.setColormap('gray')
    """

    def __setAppearance(self, key, value):
        self._appearance[key] = value

    def __getAppearance(self, key, default=None):
        return self._appearance.get(key, default)

    @saveCanvas
    def setColormap(self, cmap):
        """
        Set colormap of the image.

        Args:
            colormap(str): colormap string such as 'gray'.
        """
        self._setColormap(cmap)
        self.__setAppearance('Colormap', cmap)

    def getColormap(self):
        """
        Get colormap of the image.

        Return:
            str: colormap string such as 'gray'
        """
        return self.__getAppearance('Colormap')

    @saveCanvas
    def setGamma(self, gamma):
        """
        Set gamma value of the image.

        Args:
            gamma(float): The gamma value.
        """
        self._setGamma(gamma)
        self.__setAppearance('ColorGamma', gamma)

    def getGamma(self):
        """
        Get the gamma value of the image.

        Return:
            float: The gamma value.
        """
        return self.__getAppearance('ColorGamma', 1.0)

    @saveCanvas
    def setOpacity(self, opacity):
        """
        Set the opacity of the image.

        Args:
            opacity(float): The opacity.
        """
        self._setOpacity(opacity)
        self.__setAppearance('Opacity', opacity)

    def getOpacity(self):
        """
        Get the opacity of the image.

        Return:
            float: The opacity.
        """
        return self.__getAppearance('Opacity', 1)

    @saveCanvas
    def setColorRange(self, min='auto', max='auto'):
        """
        Set the color range of the image.

        Args:
            min(float or 'auto'): The minimum value of the range.
            max(float or 'auto'): The maximum value of the range.
        """
        automin, automax = self.getAutoColorRange()
        if max == 'auto':
            max = automax
        if min == 'auto':
            min = automin
        if max < min:
            max = min
        if self.isLog() and (min <= 0 or max <= 0):
            warnings.warn('[Image.setColorRange] Values must all be positive to use log plot. Log is disabled.', RuntimeWarning)
            self.setLog(True)
        self._setColorRange(min, max)
        self.__setAppearance('Range', (min, max))

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
        dat = np.nan_to_num(self.getFilteredWave().data)
        ma, mi = np.percentile(dat, [95, 5])
        dat = np.clip(dat, mi, ma)
        var = np.sqrt(dat.var()) * 3
        if var == 0:
            var = 1
        mean = dat.mean()
        if np.min(dat) >= 0 and mean - var < 0:
            return (0, mean + var)
        else:
            return (mean - var, mean + var)

    @saveCanvas
    def setLog(self, log):
        """
        Set the color scale to be logarithmic.

        Args:
            log(bool): If *log* is True, logarithmic scale is enabled.
        """
        self._setLog(log)
        self.__setAppearance('Log', log)

    def isLog(self):
        """
        Return true if the color scale is logarithmic.

        Return:
            bool: If True, logarithmic scale is enabled.
        """
        return self.__getAppearance('Log')

    @saveCanvas
    def setColorbarVisible(self, visible):
        """
        Set the visibility of the colorbar.

        Args:
            visible(bool): The visibility.
        """
        self._setColorbarVisible(visible)
        self.__setAppearance("colorbarVisible", visible)
        self.canvas().refreshCanvasSize()
        self.canvas().refreshMargin()

    def getColorbarVisible(self):
        """
        Get the visibility of the colorbar.

        Returns:
            bool: The visibility.
        """
        return self.__getAppearance('colorbarVisible', False)

    @saveCanvas
    def setColorbarDirection(self, direction):
        """
        Set the direction of the colorbar.

        Args:
            direction ('vretical' or 'horizontal'): The direction of the colorbar.
        """
        self._setColorbarDirection(direction)
        self.__setAppearance("colorbarDirection", direction)
        self.canvas().refreshCanvasSize()
        self.canvas().refreshMargin()

    def getColorbarDirection(self):
        """
        Get the direction of the colorbar.

        Returns:
            str: The direction of the colorbar.
        """
        return self.__getAppearance("colorbarDirection", "vertical")

    @saveCanvas
    def setColorbarPosition(self, pos):
        """
        Set the position of the colorbar.

        Args:
            pos(length 2 float): The position of the colorbar in the form of (x,y).
        """
        self._setColorbarPosition(pos)
        self.__setAppearance("colorbarPosition", pos)

    def getColorbarPosition(self):
        """
        Get the position of the colorbar.

        Returns:
            length 2 float: The position of the colorbar.
        """
        return self.__getAppearance('colorbarPosition', (0.02, 0))

    @saveCanvas
    def setColorbarSize(self, size):
        """
        Set the size of the colorbar.

        Args:
            size(length 2 float): The size of the colorbar in the form of (width, height).
        """
        self._setColorbarSize(size)
        self.__setAppearance("colorbarSize", size)

    def getColorbarSize(self):
        """
        Get the size of the colorbar.

        Returns:
            length 2 float: The size of the colorbar.
        """
        return self.__getAppearance('colorbarSize', (0.04, 1))

    def _loadAppearance(self, appearance):
        self.setColormap(appearance.get('Colormap', 'gray'))
        self.setGamma(appearance.get('ColorGamma', 1.0))
        self.setOpacity(appearance.get('Opacity', 1.0))
        self.setColorRange(*appearance.get('Range', self.getAutoColorRange()))
        self.setLog(appearance.get('Log', False))
        self.setColorbarVisible(appearance.get('colorbarVisible', False))
        self.setColorbarPosition(appearance.get('colorbarPosition', (0.02, 0)))
        self.setColorbarSize(appearance.get('colorbarSize', (0.04, 1)))

    def _setColormap(self, cmap):
        warnings.warn(str(type(self)) + " does not implement _setColormap(cmap) method.", NotImplementedWarning)

    def _setGamma(self, gamma):
        warnings.warn(str(type(self)) + " does not implement _setGamma(gamma) method.", NotImplementedWarning)

    def _setOpacity(self, opacity):
        warnings.warn(str(type(self)) + " does not implement _setOpacity(opacity) method.", NotImplementedWarning)

    def _setColorRange(self, min, max):
        warnings.warn(str(type(self)) + " does not implement _setColorRange(min, max) method.", NotImplementedWarning)

    def _setLog(self, log):
        warnings.warn(str(type(self)) + " does not implement _setLog(log) method.", NotImplementedWarning)

    def _setColorbarVisible(self, visible):
        warnings.warn(str(type(self)) + " does not implement _setColorbarVisible(visible) method.", NotImplementedWarning)

    def _setColorbarDirection(self, direction):
        warnings.warn(str(type(self)) + " does not implement _setColorbarDirection(direction) method.", NotImplementedWarning)

    def _setColorbarPosition(self, pos):
        warnings.warn(str(type(self)) + " does not implement _setColorbarPosition(pos) method.", NotImplementedWarning)

    def setColorbarSize(self, size):
        warnings.warn(str(type(self)) + " does not implement _setColorbarSize(size) method.", NotImplementedWarning)
