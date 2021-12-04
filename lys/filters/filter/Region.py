import numpy as np
import dask.array as da
from scipy.optimize import minimize
from scipy.ndimage import map_coordinates

from lys import Wave, DaskWave
from lys.filters import FilterSettingBase, filterGUI, addFilter

from .FilterInterface import FilterInterface
from .CommonWidgets import RegionSelectWidget, QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, AxisSelectionLayout, QFileDialog, QSpinBox


class NormalizeFilter(FilterInterface):
    """
    Normalize data specified by *range* along *axis*.

    When *axis* = 1 and data.ndim=2, range should be [(x1, x2), None].
    The result is as follow.
    data[0] = data[:,0]/data[x1:x2, 0].mean(), data[1]=data[:,1]/data[x1:x2, 1].mean(), ...

    Args: 
        range(sqeuence of length-2 float or None): see description above.
        axis(int): axis along which normalization is applied.
    """

    def __init__(self, range, axis):
        self._range = range
        self._axis = axis

    def _makeSlice(self, wave):
        sl = []
        for i, r in enumerate(self._range):
            if r is None:
                sl.append(slice(None))
            elif (r[0] == 0 and r[1] == 0) or self._axis == i:
                sl.append(slice(None))
            else:
                ind = wave.posToPoint(r, i)
                sl.append(slice(*ind))
        return tuple(sl)

    def _execute(self, wave, **kwargs):
        axes = list(range(wave.data.ndim))
        if self._axis == -1:
            data = wave.data / wave.data[self._makeSlice(wave)].mean()
        else:
            letters = ["a", "b", "c", "d", "e", "f",
                       "g", "h", "i", "j", "k", "l", "m", "n"]
            axes.remove(self._axis)
            nor = 1 / wave.data[self._makeSlice(wave)].mean(axis=axes)
            subscripts = ""
            for i in range(wave.data.ndim):
                subscripts += letters[i]
            subscripts = subscripts + "," + letters[self._axis] + "->" + subscripts
            data = da.einsum(subscripts, wave.data, nor)
        return DaskWave(data, *wave.axes, **wave.note)

    def getParameters(self):
        return {"range": self._range, "axis": self._axis}


class ReferenceNormalizeFilter(FilterInterface):
    """
    Normalize data by reference specified by refIndex.

    When data.ndim=2 and *axis* = 1, type='Divide', refIndex=5, data is normalized as
    data[:,0] = data[:,0]/data[:,5], data[:,1]=data[:,1]/dsata[:,5], ...

    Args:
        axis(int): axis along which data is normalized.
        type('Diff' or 'Divide'): operator between data and reference.
        refIndex(int): index of reference data.
    """

    def __init__(self, axis, type, refIndex):
        self._type = type
        self._axis = axis
        self._ref = refIndex

    def _execute(self, wave, *axes, **kwargs):
        ref = self.__makeReference(wave)
        if self._type == "Diff":
            data = wave.data.astype(float) - ref
        if self._type == "Divide":
            data = wave.data.astype(float) / ref
        return DaskWave(data, *wave.axes, **wave.note)

    def __makeReference(self, wave):
        sl = [slice(None)] * wave.data.ndim
        sl[self._axis] = self._ref
        order = list(range(1, wave.data.ndim))
        order.insert(self._axis, 0)
        res = da.stack([wave.data[tuple(sl)]] * wave.data.shape[self._axis]).transpose(*order)
        return res

    def getParameters(self):
        return {"axis": self._axis, "type": self._type, "refIndex": self._ref}


class SelectRegionFilter(FilterInterface):
    """
    Cut data by range specified by *region*

    *range* should be [(x1,x2),(y1,y2),...], where x1 and y2 specifies selected region in *axes* units.

    The calculated result is data[x1:x2, y1:y2, ...]

    Args:
        range(sequence of length-2 tuple or None): see above description.

    Example:

        Select region of 5\*5 data::

            w = Wave(np.ones([5, 5]), [1, 2, 3, 4, 5], [11, 12, 13, 14, 15])
            f = filters.SelectRegionFilter(range=[(2, 4), (11, 14)]) # range is given in axes unit
            result = f.execute(w)
            print(result.data.shape)
            # (2, 3)
            print(result.x)
            # [2, 3]
            print(result.y)
            # [11, 12, 13]
    """

    def __init__(self, range):
        self._range = range

    def _execute(self, wave, *axes, **kwargs):
        key = self._makeSlice(wave)
        data = wave.data[key]
        axes = []
        for i, s in enumerate(key):
            if wave.axisIsValid(i):
                axes.append(wave.getAxis(i)[s])
            else:
                axes.append(None)
        return DaskWave(data, *axes, **wave.note)

    def _makeSlice(self, wave):
        sl = []
        for i, r in enumerate(self._range):
            if r is None:
                sl.append(slice(None))
            elif r[0] == 0 and r[1] == 0:
                sl.append(slice(None))
            else:
                ind = wave.posToPoint(r, i)
                sl.append(slice(*ind))
        return tuple(sl)

    def getParameters(self):
        return {"range": self._range}


class MaskFilter(FilterInterface):
    def __init__(self, filename):
        self._mask = filename

    def _execute(self, wave, *axes, **kwargs):
        mask = DaskWave(Wave(self._mask))
        return DaskWave(wave.data * mask.data, *wave.axes, **wave.note)

    def getParameters(self):
        return {"mask": self._mask}


class ReferenceShiftFilter(FilterInterface):
    def __init__(self, axis, region, order=3):
        self._region = region
        self._axis = axis
        self._order = order

    def _makeSlice(self, wave):
        sl = []
        for i, r in enumerate(self._region):
            if (r[0] == 0 and r[1] == 0) or self._axis == i:
                pass
            else:
                ind = wave.posToPoint(r, i)
                sl.append(slice(*ind))
        return tuple(sl)

    def _execute(self, wave, *args, **kwargs):
        region = self._makeSlice(wave)

        def _fit_image(tar, ref):
            return _fit_image_(tar, ref, region=region, order=self._order)
        gumap2 = da.gufunc(_fit_image, signature="(i,j),(i,j)->(i,j)", output_dtypes=wave.data.dtype, vectorize=True, axes=[(0, 1), (0, 1), (0, 1)], allow_rechunk=True)

        def array_fit(x):
            if len(x) == 0:
                return np.array([])
            return gumap2(x, x[:, :, 0])
        gumap1 = da.gufunc(array_fit, signature="(i,j,k)->(i,j,k)", output_dtypes=wave.data.dtype, vectorize=True, axes=[(0, 1, self._axis), (0, 1, self._axis)], allow_rechunk=True)
        return DaskWave(gumap1(wave.data), *wave.axes, **wave.note)

    def getParameters(self):
        return {"axis": self._axis, "region": self._region, "order": self._order}


def _image_shift(shift, im, ord):
    x = np.linspace(0, im.shape[0] - 1, im.shape[0])
    y = np.linspace(0, im.shape[1] - 1, im.shape[1])
    xx, yy = np.meshgrid(x, y)
    return map_coordinates(im, [yy + shift[1], xx + shift[0]], order=ord)


def _image_dif(tar, ref, shift, region, ord=3):
    im = _image_shift(shift, tar, ord)
    return np.sum((im[region] - ref[region])**2)


def _fit_image_(tar, ref, region=None, order=3):
    ord = order
    norm = np.sum(ref)
    tar_n = tar / norm
    ref_n = ref / norm
    s = minimize(lambda s: _image_dif(tar_n, ref_n, s, region, ord), [0, 0], method="Nelder-Mead", options={'xatol': 1e-4})
    return _image_shift(s.x, tar, ord)


@filterGUI(NormalizeFilter)
class _NormalizeSetting(FilterSettingBase):
    def __init__(self, dim):
        super().__init__(dim)
        self.range = RegionSelectWidget(self, dim)
        self.combo = QComboBox()
        self.combo.addItem("Whole")
        for d in range(dim):
            self.combo.addItem("Axis" + str(d + 1))

        vbox = QHBoxLayout()
        vbox.addWidget(QLabel("Normalization direction"))
        vbox.addWidget(self.combo)

        hbox = QVBoxLayout()
        hbox.addLayout(vbox)
        hbox.addLayout(self.range)
        self.setLayout(hbox)

    def getParameters(self):
        return {"range": self.range.getRegion(), "axis": self.combo.currentIndex() - 1}

    def setParameters(self, range, axis):
        self.combo.setCurrentIndex(axis + 1)
        for i, r in enumerate(range):
            self.range.setRegion(i, r)


@filterGUI(ReferenceNormalizeFilter)
class _ReferenceNormalizeSetting(FilterSettingBase):
    def __init__(self, dim):
        super().__init__(dim)
        self.__axis = AxisSelectionLayout("Axis", dim)
        self.__type = QComboBox()
        self.__type.addItems(["Diff", "Divide"])
        self.__ref = QComboBox()
        self.__ref.addItems(["First", "Last"])
        hbox = QHBoxLayout()
        hbox.addLayout(self.__axis)
        hbox.addWidget(self.__type)
        hbox.addWidget(self.__ref)
        self.setLayout(hbox)

    def getParameters(self):
        ref = self.__ref.currentText()
        if ref == "First":
            ref = 0
        else:
            ref = -1
        return {"axis": self.__axis.getAxis(), "type": self.__type.currentText(), "refIndex": ref}

    def setParameters(self, axis, type, refIndex):
        self.__axis.setAxis(axis)
        if type == "Diff":
            self.__type.setCurrentIndex(0)
        else:
            self.__type.setCurrentIndex(1)
        if refIndex == 0:
            self.__ref.setCurrentIndex(0)
        else:
            self.__ref.setCurrentIndex(1)


@filterGUI(SelectRegionFilter)
class _SelectRegionSetting(FilterSettingBase):
    def __init__(self, dim):
        super().__init__(dim)
        self.range = RegionSelectWidget(self, dim)
        self.setLayout(self.range)

    def getParameters(self):
        return {"range": self.range.getRegion()}

    def setParameters(self, range):
        for i, r in enumerate(range):
            self.range.setRegion(i, r)


@filterGUI(MaskFilter)
class _MaskSetting(FilterSettingBase):
    def __init__(self, dim):
        super().__init__(dim)
        self.__filename = QLineEdit()

        hbox = QHBoxLayout()
        hbox.addWidget(self.__filename)
        hbox.addWidget(QPushButton("Load", clicked=self._LoadMask))
        self.setLayout(hbox)

    def _LoadMask(self):
        file, _ = QFileDialog.getOpenFileName(None, 'Open file', filter="npz(*.npz)")
        if 0 != len(file):
            self.__filename.setText(file)

    def getParameters(self):
        return {"filename": self.__filename.text()}

    def setParameters(self, filename):
        self.__filename.setText(filename)


@filterGUI(ReferenceShiftFilter)
class _RefShiftSetting(FilterSettingBase):
    def __init__(self, dim):
        super().__init__(dim)
        self.range = RegionSelectWidget(self, dim)
        self.combo = QComboBox()
        for d in range(dim):
            self.combo.addItem("Axis" + str(d + 1))
        self._order = QSpinBox()
        self._order.setValue(3)
        self._order.setRange(1, 5)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Axis"))
        hbox.addWidget(self.combo)
        hbox.addWidget(QLabel("Order"))
        hbox.addWidget(self._order)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(self.range)
        self.setLayout(vbox)

    def getParameters(self):
        return {"axis": self.combo.currentIndex(), "region": self.range.getRegion(), "order": self._order.value()}

    def setParameters(self, axis, region, order=3):
        self.combo.setCurrentIndex(axis)
        self._order.setValue(order)
        for i, r in enumerate(region):
            self.range.setRegion(i, r)


addFilter(ReferenceNormalizeFilter, gui=_ReferenceNormalizeSetting, guiName="Normalize by ref.", guiGroup="Normalize")
addFilter(NormalizeFilter, gui=_NormalizeSetting, guiName="Normalize by area", guiGroup="Normalize")

addFilter(SelectRegionFilter, gui=_SelectRegionSetting, guiName="Select Region", guiGroup="Resize and interpolation")

addFilter(MaskFilter, gui=_MaskSetting, guiName="Masking", guiGroup="UDAnalysis")
addFilter(ReferenceShiftFilter, gui=_RefShiftSetting, guiName="Reference Shift", guiGroup="UDAnalysis")
