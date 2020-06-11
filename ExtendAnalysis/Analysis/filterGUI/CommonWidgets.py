from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SpinBoxOverOne(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimum(1)
        self.setValue(1)


class OddSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimum(1)
        self.setSingleStep(2)
        self.setValue(3)
        self.valueChanged.connect(self.valChanged)

    def valChanged(self, val):
        if val % 2 == 0:
            self.setValue(val - 1)


class kernelSizeLayout(QGridLayout):
    def __init__(self, dimension=2, odd=True):
        super().__init__()
        self.addWidget(QLabel('Kernel Size'), 1, 0)
        if odd:
            spin = OddSpinBox
        else:
            spin = SpinBoxOverOne
        self._kernels = [spin() for d in range(dimension)]
        for i, k in enumerate(self._kernels):
            self.addWidget(QLabel('Axis' + str(i + 1)), 0, i + 1)
            self.addWidget(k, 1, i + 1)

    def getKernelSize(self):
        return [k.value() for k in self._kernels]

    def setKernelSize(self, val):
        for k, v in zip(self._kernels, val):
            k.setValue(v)


class kernelSigmaLayout(QGridLayout):
    def __init__(self, dimension=2):
        super().__init__()
        self.addWidget(QLabel('Sigma'), 1, 0)
        self._kernels = [QDoubleSpinBox() for d in range(dimension)]
        for i, k in enumerate(self._kernels):
            k.setMinimum(0)
            self.addWidget(QLabel('Axis' + str(i + 1)), 0, i + 1)
            self.addWidget(k, 1, i + 1)

    def getKernelSigma(self):
        return [k.value() for k in self._kernels]

    def setKernelSigma(self, val):
        for k, v in zip(self._kernels, val):
            k.setValue(v)


class AxisCheckLayout(QHBoxLayout):
    def __init__(self, dim):
        super().__init__()
        self._axes = [QCheckBox("Axis" + str(i)) for i in range(dim)]
        for a in self._axes:
            self.addWidget(a)

    def GetChecked(self):
        axes = []
        for i, a in enumerate(self._axes):
            if a.isChecked():
                axes.append(i)
        return axes

    def SetChecked(self, axes):
        for i, a in enumerate(self._axes):
            if i in axes:
                a.setChecked(True)
            else:
                a.setChecked(False)


class AxisSelectionLayout(QHBoxLayout):
    def __init__(self, label, dim=2, init=0):
        super().__init__()
        self.dimension = 0
        self.group = QButtonGroup()
        self.childs = []
        self.addWidget(QLabel(label))
        self.setDimension(dim)
        self.childs[init].setChecked(True)

    def __update(self):
        for c in self.childs:
            self.removeWidget(c)
            self.group.removeButton(c)
            c.deleteLater()
        self.childs = [QRadioButton(str(i)) for i in range(self.dimension)]
        for c in self.childs:
            self.addWidget(c)
            self.group.addButton(c)

    def setDimension(self, n):
        if n == self.dimension:
            return
        self.dimension = n
        self.__update()

    def getAxis(self):
        for i, b in enumerate(self.childs):
            if b.isChecked():
                return i

    def setAxis(self, axis):
        self.childs[axis].setChecked(True)


class AxesSelectionDialog(QDialog):
    def __init__(self, dim=2):
        super().__init__()
        self.dim = dim
        self.__initlayout()
        self.show()

    def __initlayout(self):
        self.axis1 = AxisSelectionLayout("Axis 1", self.dim, 0)
        self.axis2 = AxisSelectionLayout("Axis 2", self.dim, 1)
        ok = QPushButton("O K", clicked=self.accept)
        cancel = QPushButton("CALCEL", clicked=self.close)
        h1 = QHBoxLayout()
        h1.addWidget(ok)
        h1.addWidget(cancel)
        layout = QVBoxLayout()
        layout.addLayout(self.axis1)
        layout.addLayout(self.axis2)
        layout.addLayout(h1)
        self.setLayout(layout)

    def setDimension(self, n):
        self.axis1.setDimension(n)
        self.axis2.setDimension(n)

    def getAxes(self):
        return (self.axis1.getAxis(), self.axis2.getAxis())
