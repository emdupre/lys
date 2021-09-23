import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .ExtendType import *


class AnalysisWindow(ExtendMdiSubWindow):
    def __init__(self, title, proj=None):
        set = globalSetting()
        if "Floating" in set:
            b = set["Floating"]
        else:
            b = False
        super().__init__(title, floating=b)
        if proj is not None:
            name = proj.replace(home() + "/", "")
            self.__proj = home() + "/" + name
            self.__setting = home() + "/.lys/" + name + "/settings.dic"
        self.show()

    def restore(self, file=None):
        if file is None or not isinstance(file, str):
            _restore(self, self.__setting)
        else:
            _restore(self, file)

    def save(self, file=None):
        if file is None or not isinstance(file, str):
            return _save(self, self.__setting)
        else:
            return _save(self, file)

    def ProjectFolder(self):
        os.makedirs(self.__proj, exist_ok=True)
        return self.__proj

    def SettingFolder(self):
        print("AnalysisWindow.SettingFolder is deprecated.")
        os.makedirs(self.ProjectFolder() + '/_settings', exist_ok=True)
        return self.ProjectFolder() + '/_settings'


def _restore(self, file):
    settings = Dict(file).data

    for obj in self.findChildren(QSpinBox) + self.findChildren(QDoubleSpinBox):
        name = obj.objectName()
        if _checkName(name):
            if name in settings:
                obj.setValue(settings[name])

    for obj in self.findChildren(QCheckBox) + self.findChildren(QRadioButton):
        name = obj.objectName()
        if _checkName(name):
            if name in settings:
                obj.setChecked(settings[name])

    for obj in self.findChildren(QComboBox):
        name = obj.objectName()
        if _checkName(name):
            if name in settings:
                i = obj.findText(settings[name])
                if i != -1:
                    obj.setCurrentIndex(i)

    for obj in self.findChildren(QLineEdit):
        name = obj.objectName()
        if _checkName(name):
            if name in settings:
                obj.setText(settings[name])


def _save(self, file):
    settings = {}

    for obj in self.findChildren(QSpinBox) + self.findChildren(QDoubleSpinBox):
        name = obj.objectName()
        if _checkName(name):
            settings[name] = obj.value()

    for obj in self.findChildren(QCheckBox) + self.findChildren(QRadioButton):
        name = obj.objectName()
        if _checkName(name):
            settings[name] = obj.isChecked()

    for obj in self.findChildren(QComboBox):
        name = obj.objectName()
        if _checkName(name):
            settings[name] = obj.currentText()

    for obj in self.findChildren(QLineEdit):
        name = obj.objectName()
        if _checkName(name):
            settings[name] = obj.text()
    d = Dict(file)
    d.data = settings
    return settings


def _checkName(name):
    if name == "":
        return False
    elif name.startswith("qt_"):
        return False
    else:
        return True
