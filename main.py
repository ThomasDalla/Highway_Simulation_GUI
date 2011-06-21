#!/usr/bin/python
__author__ = 'thomas'

from PySide.QtGui import QApplication
from highwaySimulatorGui import *
import sys

#def trace(frame, event, arg):
#    with open('/home/thomas/ZumoDrive/Highway_Simulation_GUI/trace.log','a') as log:
#        log.write("%s, %s:%d\n" % (event, frame.f_code.co_filename, frame.f_lineno))
#    return trace
#sys.settrace(trace)

app = QApplication(sys.argv)
app.setApplicationName("Highway Simulation GUI")

mw = HighwaySimulatorGui()
mw.show()

sys.exit(app.exec_())