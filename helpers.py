__author__ = 'thomas'

from PySide.QtGui import QWidget, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox
from PySide.QtCore import QSettings, Qt
from datetime import datetime
import random

def formatTimeLeft(timeLeft):
    if timeLeft>60*60*24:
        timeLeft = timeLeft/60.0/60.0/24.0
        unit = 'day'
    elif timeLeft>60*60:
        timeLeft = timeLeft/60.0/60.0
        unit = 'hour'
    elif timeLeft>60:
        timeLeft /= 60.0
        unit = 'minute'
    else:
        unit = 'second'
    if timeLeft>1:
        unit += 's'
    return "%2.2f %s" % (timeLeft, unit)

class SimpleOption(QWidget):
    def __init__(self, settingsName, labelText, defaultValue, checkable=False):
        super(SimpleOption, self).__init__()
        self.setLayout(QHBoxLayout())
        #self.layout().setSpacing(0)
        self.checkable = checkable
        if checkable:
            self.checkBox = QCheckBox()
            self.layout().addWidget(self.checkBox)
        self.label = QLabel(labelText)
        self.label.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        #self.label.setMinimumWidth(240)
        self.layout().addWidget(self.label)
        self.settingsName = settingsName
        self.editor(defaultValue)
    def editor(self, defaultValue):
        self.lineEdit = QLineEdit()
        self.lineEdit.setText(str(QSettings().value(self.settingsName, defaultValue)))
        self.lineEdit.setToolTip('Default value: %s' % defaultValue)
        self.lineEdit.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.layout().addWidget(self.lineEdit)
    def setEnabled(self, e):
        self.lineEdit.setEnabled(e)
    def getName(self):
        return self.label.text()
    def setName(self, newName):
        self.label.setText(newName)
    def getValue(self):
        return self.lineEdit.text()
    def setValue(self, newValue):
        self.lineEdit.setText(str(newValue))
    def save(self):
        QSettings().setValue(self.settingsName, self.getValue())
    def __str__(self):
        return str(self.getValue())

class SimpleSpinOption(SimpleOption):
    def __init__(self, settingsName, labelText, defaultValue, integer=False, checkable=False):
        self.integer = integer
        super(SimpleSpinOption,self).__init__(settingsName, labelText, defaultValue, checkable)
    def editor(self, defaultValue):
        if self.integer:
            self.spinBox = QSpinBox()
        else:
            self.spinBox = QDoubleSpinBox()
        self.spinBox.setRange(0,10**5)
        self.spinBox.setValue(float(QSettings().value(self.settingsName, defaultValue)))
        self.spinBox.setToolTip('Default value: %s' % defaultValue)
        self.spinBox.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.layout().addWidget(self.spinBox)
    def setEnabled(self, e):
        self.spinBox.setEnabled(e)
    def getValue(self):
        return self.spinBox.value()
    def setValue(self, newValue):
        self.spinBox.setValue(newValue)
    def setRange(self, min, max):
        self.spinBox.setRange(min, max)

class SimpleComboboxOption(SimpleOption):
    def __init__(self, settingsName, labelText, defaultValue, checkable=False, *options):
        self.options = options
        super(SimpleComboboxOption,self).__init__(settingsName, labelText, defaultValue, checkable)
    def editor(self, defaultValue):
        #options = ('Uniform','Exponential','Normal','Log Normal')
        options = self.options
        self.combo = QComboBox()
        self.combo.addItems(options)
        self.combo.setCurrentIndex(int(QSettings().value(self.settingsName, defaultValue)))
        self.combo.setToolTip('Default value: %s' % defaultValue)
        #self.combo.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.layout().addWidget(self.combo)
    def setEnabled(self, e):
        self.combo.setEnabled(e)
    def getValue(self):
        return self.combo.currentIndex()
    def getName(self):
        return self.combo.currentText()
