import numpy as np
import time
from scipy.signal import *
from scipy.ndimage import *

from ExtendAnalysis import Wave, DaskWave
from .FilterInterface import FilterInterface

import dask.array as da


class PeakFilter(FilterInterface):
    def __init__(self, axis, order, type="ArgRelMax", size=1):
        self._order = order
        self._type = type
        self._axis = axis
        self._size = size

    def _execute(self, wave, *args, **kwargs):
        if self._type == "ArgRelMax":
            f = relmax
        else:
            f = relmin
        axes = [ax for ax in wave.axes]
        axes[self._axis] = None
        if isinstance(wave, Wave):
            uf = np.vectorize(f, signature="(i),()->(j)")
            tran = list(range(wave.data.ndim))
            tran.remove(self._axis)
            tran.append(self._axis)
            wave.data = uf(wave.data.transpose(*tran), self._order)
        if isinstance(wave, DaskWave):
            uf = da.gufunc(f, signature="(i),(),()->(j)", output_dtypes=float, vectorize=True, axes=[(self._axis,), (), (), (self._axis)], allow_rechunk=True, output_sizes={"j": self._size})
            wave.data = uf(wave.data, self._order, self._size)
        wave.axes = axes
        return wave

    def getParams(self):
        return self._axis, self._order, self._type, self._size


def relmax(x, order, size):
    data = argrelextrema(x, np.greater_equal, order=order)[0]
    index = np.argsort([x[i] for i in data])
    res = [data[i] for i in index[::-1] if data[i] != 0 and data[i] != len(x) - 1]
    while len(res) < size:
        res.append(0)
    return np.array(res[:size])


def relmin(x, order, size):
    data = argrelextrema(x, np.less_equal, order=order)[0]
    index = np.argsort([x[i] for i in data])
    res = [data[i] for i in index]
    while len(res) < size:
        res.append(0)
    return np.array(res[:3])


class PeakPostFilter(FilterInterface):
    def __init__(self, axis, axes=(0, 1)):
        self._axes = axes
        self._axis = axis

    def _execute(self, wave, *args, **kwargs):
        if isinstance(wave, Wave):
            wave.data = _find4D(wave.data)
        if isinstance(wave, DaskWave):
            uf = da.gufunc(_find4D, signature="(i,j,k,l)->(i,j,k,l)", output_dtypes=float, vectorize=True, axes=[(0, 1, 2, 3), (0, 1, 2, 3)], allow_rechunk=True)
            wave.data = uf(wave.data)
        return wave

    def getParams(self):
        return self._axis, self._axes


def _find4D(data):
    edge = [_findNearest(data[0, :, :, 0], data[0, 0, n, 0]) for n in range(data.shape[2])]
    plane = [_findNearest(data.transpose(1, 0, 2, 3)[:, :, :, 0], e).transpose(1, 0) for e in edge]
    plane = [_correct2D(p, data[:, :, :, 0]) for p in plane]
    volume = [_findNearest(data.transpose(0, 1, 3, 2), p) for p in plane]
    return np.array(volume).transpose(1, 2, 0, 3)


def _correct2D(target, data, threshold1=0.3, threshold2=3, value=25):
    ref = _makeReference(target, -value, threshold2, True, 30)
    ref = _makeReference(ref, value, threshold1, False, 30)
    ref = np.tile(ref, (data.shape[2], 1, 1)).transpose(1, 2, 0)
    index = np.argmin(np.abs(data - ref), axis=2)
    xx, yy = np.meshgrid(range(data.shape[1]), range(data.shape[0]))
    return data[yy, xx, index]


def _makeReference(data, value, threshold, upper, loop):
    med = median_filter(data, 3)
    d = percentile_filter(data, value, 5)
    mask = np.abs(data - med) > threshold
    if upper:
        tmp = np.where(mask & (data < med), d, data)
    else:
        tmp = np.where(mask & (data > med), d, data)
    if loop == 0:
        return tmp
    else:
        return _makeReference(tmp, value, threshold, upper, loop - 1)


def _findNearest(data, reference):  # reference: n-dim array, data: (n+2)-dim array, return (n+1)-dim array
    ref = np.array(reference)
    mesh = np.meshgrid(*[range(x) for x in ref.shape], indexing="ij")
    res = []
    for i in range(data.shape[-2]):
        sl = [slice(None)] * (data.ndim)
        sl[-2] = i
        tile = tuple([data.shape[-1]] + [1] * (data.ndim - 2))
        order = list(range(1, ref.ndim + 1)) + [0]
        diff = np.abs(data[tuple(sl)] - np.tile(ref, tile).transpose(*order))
        index = np.argmin(diff, axis=-1)
        sl2 = mesh + [i] + [index]
        ref = data[tuple(sl2)]
        res.append(ref)
    return np.array(res).transpose(order)
