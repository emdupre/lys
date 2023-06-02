import logging
from matplotlib import animation

from lys import glb, frontCanvas
from lys.Qt import QtWidgets, QtCore
from lys.widgets import lysCanvas, AxisSelectionLayout


class AnimationTab(QtWidgets.QGroupBox):
    updated = QtCore.pyqtSignal(int)
    _type = [".mp4 (ffmpeg required)", ".gif"]

    def __init__(self, cui):
        super().__init__("Animation")
        self.__initlayout()
        self._cui = cui
        self.__axis.setDimension(cui.getFilteredWave().ndim)
        self._cui.dimensionChanged.connect(self.__dimensionChanged)

    def __dimensionChanged(self):
        self.__axis.setDimension(self._cui.getFilteredWave().ndim)

    def __initlayout(self):
        self.__axis = AxisSelectionLayout("Frame axis", 2)
        btn = QtWidgets.QPushButton("Create animation", clicked=self.__animation)
        self.__filename = QtWidgets.QLineEdit()
        self.__types = QtWidgets.QComboBox()
        self.__types.addItems(self._type)

        g = QtWidgets.QGridLayout()
        g.addWidget(QtWidgets.QLabel("Filename"), 0, 0)
        g.addWidget(self.__filename, 0, 1)
        g.addWidget(QtWidgets.QLabel("Type"), 1, 0)
        g.addWidget(self.__types, 1, 1)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.__axis)
        self.layout.addLayout(g)
        self.layout.addLayout(self.__makeTimeOptionLayout())
        self.layout.addLayout(self.__makeGeneralFuncLayout())
        self.layout.addWidget(btn)
        self.setLayout(self.layout)

    def __makeTimeOptionLayout(self):
        self.__useTime = QtWidgets.QCheckBox('Draw frame')
        self.__timeoffset = QtWidgets.QDoubleSpinBox()
        self.__timeoffset.setRange(float('-inf'), float('inf'))
        self.__timeunit = QtWidgets.QLineEdit()

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.__useTime)
        hbox1.addWidget(self.__timeoffset)
        hbox1.addWidget(self.__timeunit)
        return hbox1

    def __makeGeneralFuncLayout(self):
        self.__useFunc = QtWidgets.QCheckBox("Use general func f(canv, i, axis)")
        self.__funcName = QtWidgets.QLineEdit()

        h1 = QtWidgets.QHBoxLayout()
        h1.addWidget(self.__useFunc)
        h1.addWidget(self.__funcName)
        return h1

    def __loadCanvasSettings(self):
        c = frontCanvas()
        if c is None:
            return None, None
        d = {}
        c.SaveAsDictionary(d)
        dic = {t: d[t] for t in ['AxisSetting', 'TickSetting', 'AxisRange', 'LabelSetting', 'TickLabelSetting', 'Size', 'Margin']}
        wd = c.getWaveData()
        return dic, wd

    def __animation(self):
        logging.info('[Animation] Analysis started.')
        dic, data = self.__loadCanvasSettings()
        if dic is None:
            QtWidgets.QMessageBox.information(self, "Error", "You should specify the Graph that is used to create animation.", QtWidgets.QMessageBox.Yes)
            return

        name = self.__filename.text()
        if len(name) == 0:
            QtWidgets.QMessageBox.information(self, "Error", "Filename is required to make animation.", QtWidgets.QMessageBox.Yes)
            return

        if self.__types.currentText() == ".gif":
            name += ".gif"
        else:
            if "ffmpeg" not in animation.writers:
                QtWidgets.QMessageBox.information(self, "Error", "FFMPEG is required to make mp4 animation.", QtWidgets.QMessageBox.Yes)
                return
            name += ".mp4"

        wave = self._cui.getFilteredWave()
        axis = wave.getAxis(self.__axis.getAxis())
        params = self.__prepareOptionalParams()
        self._makeAnime(name, dic, data, axis, params)

    def __prepareOptionalParams(self):
        params = {}
        if self.__useTime.isChecked():
            params['time'] = {"unit": self.__timeunit.text(), "offset": self.__timeoffset.value()}
        if self.__useFunc.isChecked():
            params['gfunc'] = self.__funcName.text()
        return params

    def _makeAnime(self, file, dic, data, axis, params):
        c = lysCanvas(lib="matplotlib")
        c.Append(data)
        c.LoadFromDictionary(dic)
        setter = _valueSetter(self._cui, self.__axis.getAxis(), len(axis))
        ani = animation.FuncAnimation(c.getFigure(), _frame, fargs=(c, axis, params, setter.setValue), frames=len(axis), interval=30, repeat=False, init_func=_init)
        if self.__types.currentText() == ".gif":
            writer = "pillow"
        else:
            writer = "ffmpeg"
        ani.save(file, writer=writer)
        QtWidgets.QMessageBox.information(self, "Info", "Animation is saved to " + file, QtWidgets.QMessageBox.Yes)
        return file


class _valueSetter:
    def __init__(self, cui, axis, nmax):
        self._cui = cui
        self._axis = axis
        self._n = 0
        self._nmax = nmax

    def setValue(self, value):
        if self._n >= self._nmax:
            return
        self._cui.setAxisRange(self._axis, value)
        self._n += 1


def _init():
    pass


def _frame(i, c, axis, params, setValue):
    setValue(axis[i])
    if "time" in params:
        _drawTime(c, axis[i], **params["time"])
    if "gfunc" in params:
        f = glb.shell().eval(params["gfunc"])
        f(c, i, axis)


def _drawTime(c, data=None, unit="", offset=0):
    t = '{:.10g}'.format(round(data + float(offset), 1)) + " " + unit
    ta = c.getTextAnnotations()
    if len(ta) == 0:
        t = c.addText(t, pos=(0.1, 0.1))
        t.setBoxStyle("square")
    else:
        ta[0].setText(t)
