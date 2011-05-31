#!/usr/bin/python
__author__ = 'thomas'

from PySide.QtGui import QApplication
from highwaySimulatorGui import *
import sys

app = QApplication(sys.argv)
app.setApplicationName("Highway Simulation GUI")

mw = HighwaySimulatorGui()
mw.show()

sys.exit(app.exec_())