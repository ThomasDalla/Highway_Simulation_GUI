__author__ = 'thomas'

from PySide.QtGui import QMainWindow, QTabWidget, QVBoxLayout, QGroupBox, QPushButton, QProgressBar, QMessageBox, QGridLayout, QTextBrowser, QFont, QPixmap, QImage
from PySide.QtCore import Slot, QThreadPool, QThread, QSize
from helpers import *
from wafThread import *
from datetime import datetime
import json
from highwayAnalyze import *

class HighwaySimulatorGui(QMainWindow):
    def __init__(self):
        super(HighwaySimulatorGui, self).__init__()
        centralTab = QTabWidget()
        mainWidget = QWidget()
        self.resultsWidget = HighwayAnalyzeWidget()
        centralTab.addTab(mainWidget, 'Run')
        centralTab.addTab(self.resultsWidget, 'Analyze')
        self.setCentralWidget(centralTab)
        centralLayout = QVBoxLayout()
        #centralLayout.setSpacing(0)
        centralLayout.setAlignment(Qt.AlignTop)
        gridWidget = QWidget()
        gridLayout = QGridLayout()
        gridLayout.setSpacing(0)
        gridWidget.setLayout(gridLayout)
        mainWidget.setLayout(centralLayout)
        self.options = dict()
        # GENERAL
        generalGroup = QGroupBox('General Settings')
        generalGroup.setLayout(QVBoxLayout())
        generalGroup.layout().setSpacing(0)
        self.pathOption = SimpleOption('path','Output Path','/home/thomas/Dropbox/Keio/research/results/')
        generalGroup.layout().addWidget(self.pathOption)
        self.scenarioOption = SimpleComboboxOption('scenario','Scenario',1, False, 'vanet-highway-test-thomas','vanet-highway-scenario2')
        generalGroup.layout().addWidget(self.scenarioOption)
        self.options['time'] = SimpleSpinOption('time','Simulation Time (sec.)',1500,True)
        self.options['time'].setRange(0,3000)
        self.options['mix'] = SimpleSpinOption('mix','Percentage of cars compare to trucks (%)',80,True)
        self.options['mix'].setRange(0,100)
        self.options['gap'] = SimpleSpinOption('gap','Average Gap (m.)',5)
        self.options['gap'].setRange(1,2000)
        self.options['lane'] = SimpleSpinOption('lane','Number of Lanes',2,True)
        self.options['lane'].setRange(2,4)
        self.options['spl'] = SimpleSpinOption('spl','Speed Limit (km/h)',130,True)
        self.options['spl'].setRange(1,200)
        for widget in ('time','mix','gap','lane','spl'):
            generalGroup.layout().addWidget(self.options[widget])
        gridLayout.addWidget(generalGroup,0,0)
        # TRAFFIC
        trafficGroup = QGroupBox('Traffic Settings')
        trafficGroup.setLayout(QVBoxLayout())
        trafficGroup.layout().setSpacing(0)
        # m/s = (km/h)*1000/3600
        self.options['vel1'] = SimpleSpinOption('vel1','Average Speed (km/h)',105,True)
        self.options['vel1'].setRange(5,150)
        self.options['dis'] = SimpleComboboxOption('dis','Speed Distribution Model',3, False, 'Uniform','Exponential','Normal','Log Normal')
        self.options['spstd'] = SimpleSpinOption('spstd','Speed Distribution Variance',1.0)
        self.options['spstd'].setRange(0,50)
        self.options['flow1'] = SimpleSpinOption('flow1','Traffic Flow Mean (veh/s)',1.0)
        self.options['flow1'].setRange(0.1,50.0)
        self.options['std1'] = SimpleSpinOption('std1','Traffic Flow Variance',0.8)
        self.options['std1'].setRange(0.1,50.0)
        self.options['maxflow'] = SimpleSpinOption('maxflow','Traffic Maximum Flow (veh/s)',5)
        self.options['maxflow'].setRange(0.1,50.0)
        for widget in ('vel1','dis','spstd','flow1','std1','maxflow'):
            trafficGroup.layout().addWidget(self.options[widget])
        gridLayout.addWidget(trafficGroup,0,1)
        # VANET
        vanetGroup = QGroupBox('VANET Settings')
        vanetGroup.setLayout(QVBoxLayout())
        vanetGroup.layout().setSpacing(0)
#        self.options['prate'] = SimpleSpinOption('prate','Penetration Rate of VANET (%)',100,True)
#        self.options['prate'].setRange(0,100)
        self.options['prate'] = 0 # start with 0
        self.options['pw'] = SimpleSpinOption('pw','Transmission Power (dBm)',21.5)
        self.options['pw'].setRange(10,50)
        #for widget in ('prate','pw'):
        for widget in ('pw',):
            vanetGroup.layout().addWidget(self.options[widget])
        gridLayout.addWidget(vanetGroup,1,0)
        # BATCH SETTINGS
        batchGroup = QGroupBox("Batch Settings")
        batchGroup.setLayout(QVBoxLayout())
        self.gapPrateOption = SimpleSpinOption('gapPrate', 'VANET percentage rate gap', 10, integer=True)
        self.sameSimuTimesOption = SimpleSpinOption('sameSimuTimes', 'How many times the same simulation', 100, integer=True)
        batchGroup.layout().setSpacing(0)
        batchGroup.layout().addWidget(self.gapPrateOption)
        batchGroup.layout().addWidget(self.sameSimuTimesOption)
        gridLayout.addWidget(batchGroup,1,1)
        # START SIMU
        centralLayout.addWidget(gridWidget)
        self.startButton = QPushButton('START')
        self.startButton.clicked.connect(self.startSimu)
        centralLayout.addWidget(self.startButton)
        self.progressBar    = QProgressBar()
        centralLayout.addWidget(self.progressBar)
        self.shutdownWhenDone = QCheckBox('Shutdown when done')
        self.actionWhenDone = QComboBox()
        self.actionWhenDone.addItems(['When finished... do nothing', 'When finished... shutdown the computer', 'When finished... Re-run the simulations!'])
        self.actionWhenDone.setCurrentIndex(int(QSettings().value('actionWhenDone', 0)))
        centralLayout.addWidget(self.actionWhenDone)
        self.infoLabel = QLabel()
        centralLayout.addWidget(self.infoLabel)
        # LOG
        self.logText = QTextBrowser()
        self.logText.setFont(QFont('Century Gothic', 7))
        centralLayout.addWidget(self.logText)
        self.setWindowTitle('Nishimura Lab | Highway Simulation')
        #self.resize(520,len(self.options)*60+100)
        #self.resultFile = open('/home/thomas/Dropbox/Keio/research/results/summary.txt', 'a')
        #self.resultFile = os.path.join(self.pathOption.getValue(), 'summary.txt')
        self.logFile = os.path.join(self.pathOption.getValue(), 'results_'+os.uname()[1]+'.log')
    def log(self, txt):
        toLog = '%s | %s' % (datetime.now(), txt)
        with open(self.logFile, 'a') as logFile:
            logFile.write(toLog+'\n')
        self.logText.append(toLog)
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
        self.log("=== SIMULATIONS START ===")
        self.logText.clear()
        self.startTime = datetime.now()
        self.simulations = []
        #self.nextPrate = 0
        self.gapPrate  = self.gapPrateOption.getValue()
        self.sameSimuTimes = self.sameSimuTimesOption.getValue()
        #self.nextSimu   = 0
        self.blockUi()
        self.simulationsDone = 0
        #output = self.pathOption.getValue() + dateToFilename(d) + '_results.txt'
        pRate = 0
        self.simulationsTotal = 0
#        print 'sameSimuTimes: %d'%self.sameSimuTimes
#        print 'gapPrate: %d'%self.gapPrate
        while pRate <= 100:
            simu = 0
            self.options['prate'] = pRate
            while simu<self.sameSimuTimes:
                waf = WafThread(self.options, self.pathOption.getValue(), scenario=self.scenarioOption.getName())
                waf.simuDone.connect(self.wafDone)
                self.simulations.append(waf)
                QThreadPool.globalInstance().start(waf)
                self.simulationsTotal += 1
                simu += 1
            pRate += self.gapPrate
        runningSimulations = 'Running %d Simulations...' % self.simulationsTotal
        self.startButton.setText(runningSimulations)
        self.log(runningSimulations)
        self.progressBar.setRange(0,self.simulationsTotal)
        self.progressBar.setValue(0)
        # 300 seconds per task average
        roughTime = self.simulationsTotal*self.resultsWidget.averageSimulationTime/QThreadPool.globalInstance().maxThreadCount()
        self.infoLabel.setText('Rough time estimation: %s' % formatTimeLeft(roughTime))
    @Slot(str)
    def wafDone(self, outputPath):
        #print 'thread done!\nReceived:'
        self.simulationsDone += 1
        simulationsLeft = self.simulationsTotal-self.simulationsDone
        with open(outputPath,'r') as out:
            r = json.loads(out.read())
            out.close()
            if 'timeToReachDest' in r['results']:
                try:
                    result = "%3.3d\t%f" % (int(r['settings']['prate']),float(r['results']['timeToReachDest']))
                except TypeError, e:
                    result = 'PYTHON ERROR: %s | File: %s' % (e, outputPath)
                    print result
                    print r
            else:
                result = 'ERROR: No timeToReachDest (%s)' % outputPath
            self.startButton.setText('%d simulations left...' % simulationsLeft)
            self.log(result)
#            with open(self.resultFile, 'a') as summary:
#                summary.write('%s | %s\n' % (datetime.now(), result))
#                summary.close()
        self.progressBar.setValue(self.simulationsDone)
        if self.simulationsDone==self.simulationsTotal:
            self.releaseUi()
            if self.actionWhenDone.currentIndex()==1:
                self.saveSettings()
                os.system('sudo halt')
            elif self.actionWhenDone.currentIndex()==2:
                self.startSimu()
        else:
            # calculate estimated time left
#            percentage_done = 1.0*self.simulationsDone/self.simulationsTotal
#            done_in = (datetime.now()-self.startTime).seconds
#            timeLeft = done_in*((1.0/percentage_done)-1.0)
            # v2: average time per simulation * nb of simulations left
            averageTimePerSimulation = (datetime.now()-self.startTime).seconds/self.simulationsDone
            timeLeft = averageTimePerSimulation * simulationsLeft
            #print "%f perc done in %d seconds => %d seconds left" % (percentage_done, done_in, timeLeft)
            formatedTimeLeft = formatTimeLeft(timeLeft)
            self.infoLabel.setText("Estimated time left: %s" % formatedTimeLeft)
    def saveSettings(self):
        for setting in self.options:
            if setting != 'prate':
                self.options[setting].save()
        self.pathOption.save()
        self.scenarioOption.save()
        QSettings().setValue('actionWhenDone',self.actionWhenDone.currentIndex())
        QSettings().setValue('sameSimuTimes',self.sameSimuTimesOption.getValue())
        QSettings().setValue('gapPrate',self.gapPrateOption.getValue())
        self.resultsWidget.saveSettings()
    def closeEvent(self, *args, **kwargs):
        self.saveSettings()
        try:
            for waf in self.simulations:
                del waf
            del self.simulations[:]
        except:
            pass
        super(HighwaySimulatorGui,self).closeEvent(*args, **kwargs)
