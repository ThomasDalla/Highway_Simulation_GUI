__author__ = 'thomas'

from PySide.QtGui import QMainWindow, QTabWidget, QVBoxLayout, QGroupBox, QPushButton, QProgressBar, QCheckBox
from PySide.QtCore import Slot, QThreadPool
from helpers import *
from datetime import datetime
import json
from wafThread import *

class HighwaySimulatorGui(QMainWindow):
    def __init__(self):
        super(HighwaySimulatorGui, self).__init__()
        centralTab = QTabWidget()
        mainWidget = QWidget()
        resultsWidget = QWidget()
        centralTab.addTab(mainWidget, 'Run')
        centralTab.addTab(resultsWidget, 'Analyze')
        self.setCentralWidget(centralTab)
        centralLayout = QVBoxLayout()
        mainWidget.setLayout(centralLayout)
        self.options = dict()
        # GENERAL
        generalGroup = QGroupBox('General Settings')
        generalGroup.setLayout(QVBoxLayout())
        self.pathOption = SimpleOption('path','Output Path','/home/thomas/Dropbox/Keio/research/results/')
        generalGroup.layout().addWidget(self.pathOption)
        self.options['time'] = SimpleSpinOption('time','Simulation Time (sec.)',1500,True)
        self.options['time'].setRange(0,3000)
        self.options['mix'] = SimpleSpinOption('mix','Percentage of cars compare to trucks (%)',80,True)
        self.options['mix'].setRange(0,100)
        self.options['gap'] = SimpleSpinOption('gap','Average Gap (m.)',5)
        self.options['gap'].setRange(2,2000)
        self.options['lane'] = SimpleSpinOption('lane','Number of Lanes',2,True)
        self.options['lane'].setRange(2,4)
        self.options['spl'] = SimpleSpinOption('spl','Speed Limit (km/h)',130,True)
        self.options['spl'].setRange(1,200)
        for widget in ('time','mix','gap','lane','spl'):
            generalGroup.layout().addWidget(self.options[widget])
        centralLayout.addWidget(generalGroup)
        # TRAFFIC
        trafficGroup = QGroupBox('Traffic Settings')
        trafficGroup.setLayout(QVBoxLayout())
        # m/s = (km/h)*1000/3600
        self.options['vel1'] = SimpleSpinOption('vel1','Average Speed (km/h)',105,True)
        self.options['vel1'].setRange(5,150)
        self.options['dis'] = SimpleComboboxOption('dis','Speed Distribution Model',3, 'Normal','Log Normal','Uniform')
        self.options['spstd'] = SimpleSpinOption('spstd','Speed Distribution Variance',1.0)
        self.options['spstd'].setRange(0,10)
        self.options['flow1'] = SimpleSpinOption('flow1','Traffic Flow Mean (veh/s)',1.0)
        self.options['flow1'].setRange(0.1,5.0)
        self.options['std1'] = SimpleSpinOption('std1','Traffic Flow Variance',0.9)
        self.options['std1'].setRange(0.1,5.0)
        self.options['maxflow'] = SimpleSpinOption('maxflow','Traffic Maximum Flow (veh/s)',5)
        self.options['maxflow'].setRange(0.1,5.0)
        for widget in ('vel1','dis','spstd','flow1','std1','maxflow'):
            trafficGroup.layout().addWidget(self.options[widget])
        centralLayout.addWidget(trafficGroup)
        # VANET
        vanetGroup = QGroupBox('VANET Settings')
        vanetGroup.setLayout(QVBoxLayout())
#        self.options['prate'] = SimpleSpinOption('prate','Penetration Rate of VANET (%)',100,True)
#        self.options['prate'].setRange(0,100)
        self.options['prate'] = 0 # start with 0
        self.options['pw'] = SimpleSpinOption('pw','Transmission Power (dBm)',21.5)
        self.options['pw'].setRange(10,50)
        #for widget in ('prate','pw'):
        for widget in ('pw',):
            vanetGroup.layout().addWidget(self.options[widget])
        centralLayout.addWidget(vanetGroup)
        # START SIMU
        self.startButton = QPushButton('START')
        self.startButton.clicked.connect(self.startSimu)
        centralLayout.addWidget(self.startButton)
        self.progressBar    = QProgressBar()
        centralLayout.addWidget(self.progressBar)
        self.shutdownWhenDone = QCheckBox('Shutdown when done')
        c = QSettings().value('shutdown', 0)
        if c=='0':
            c = False
        else:
            c = True
        self.shutdownWhenDone.setChecked(c)
        centralLayout.addWidget(self.shutdownWhenDone)
        self.infoLabel = QLabel()
        centralLayout.addWidget(self.infoLabel)
        self.setWindowTitle('Nishimura Lab | Highway Simulation')
        self.resize(520,len(self.options)*60+100)
        #self.resultFile = open('/home/thomas/Dropbox/Keio/research/results/summary.txt', 'a')
        self.resultFile = '/home/thomas/Dropbox/Keio/research/results/summary.txt'
    def blockUi(self):
        self.startButton.setEnabled(False)
        for option in self.options:
            if option!='prate':
                self.options[option].setEnabled(False)
    def releaseUi(self):
        self.startButton.setEnabled(True)
        self.startButton.setText('START')
        for option in self.options:
            if option!='prate':
                self.options[option].setEnabled(True)
    def startSimu(self):
        self.startTime = datetime.now()
        self.simulations = []
        #self.nextPrate = 0
        self.gapPrate  = 10
        self.sameSimuTimes = 30 # Do X times the same simulation (with the same settings)
        #self.nextSimu   = 0
        self.blockUi()
        self.simulationsDone = 0
        #output = self.pathOption.getValue() + dateToFilename(d) + '_results.txt'
        pRate = 0
        self.simulationsTotal = 0
        while pRate <= 100:
            simu = 0
            self.options['prate'] = pRate
            while simu<self.sameSimuTimes:
                waf = WafThread(self.options, self.pathOption.getValue())
                waf.simuDone.connect(self.wafDone)
                self.simulations.append(waf)
                QThreadPool.globalInstance().start(waf)
                self.simulationsTotal += 1
                simu += 1
            pRate += self.gapPrate
        self.startButton.setText('Running %d Simulations...' % self.simulationsTotal)
        self.progressBar.setRange(0,self.simulationsTotal)
        # 300 seconds per task average
        roughTime = self.simulationsTotal*300.0/QThreadPool.globalInstance().maxThreadCount()
        self.infoLabel.setText('Rough time estimation: %s' % self.formatTimeLeft(roughTime))
    def formatTimeLeft(self, timeLeft):
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
    @Slot(str)
    def wafDone(self, outputPath):
        #print 'thread done!\nReceived:'
        self.simulationsDone += 1
        simulationsLeft = self.simulationsTotal-self.simulationsDone
        with open(outputPath,'r') as out:
            r = json.loads(out.read())
            out.close()
            if 'timeToReachDest' in r['results']:
                result = "%3.3d\t%f" % (int(r['settings']['prate']),float(r['results']['timeToReachDest']))
            else:
                result = 'ERROR: No timeToReachDest (%s)' % outputPath
            self.startButton.setText('%d simulations left...' % simulationsLeft)
            print '%s | %s' % (datetime.now(), result)
            with open(self.resultFile, 'a') as summary:
                summary.write('%s | %s\n' % (datetime.now(), result))
                summary.close()
        self.progressBar.setValue(self.simulationsDone)
        if self.simulationsDone==self.simulationsTotal:
            self.releaseUi()
            if self.shutdownWhenDone.isChecked():
                self.saveSettings()
                os.system('sudo halt')
        else:
            # calculate estimated time left
#            percentage_done = 1.0*self.simulationsDone/self.simulationsTotal
#            done_in = (datetime.now()-self.startTime).seconds
#            timeLeft = done_in*((1.0/percentage_done)-1.0)
            # v2: average time per simulation * nb of simulations left
            averageTimePerSimulation = (datetime.now()-self.startTime).seconds/self.simulationsDone
            timeLeft = averageTimePerSimulation * simulationsLeft
            #print "%f perc done in %d seconds => %d seconds left" % (percentage_done, done_in, timeLeft)
            formatedTimeLeft = self.formatTimeLeft(timeLeft)
            self.infoLabel.setText("Estimated time left: %s" % formatedTimeLeft)
    def saveSettings(self):
        for setting in self.options:
            if setting != 'prate':
                self.options[setting].save()
        self.pathOption.save()
        if self.shutdownWhenDone.isChecked():
            c = 1
        else:
            c = 0
        QSettings().setValue('shutdown',c)
    def closeEvent(self, *args, **kwargs):
        self.saveSettings()
        try:
            for waf in self.simulations:
                del waf
            del self.simulations[:]
        except:
            pass
        super(HighwaySimulatorGui,self).closeEvent(*args, **kwargs)