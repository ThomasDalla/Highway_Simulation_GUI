__author__ = 'thomas'

from PySide.QtGui import QMainWindow, QTabWidget, QVBoxLayout, QGroupBox, QPushButton, QProgressBar, QMessageBox, QGridLayout, QTextBrowser, QFont, QPixmap, QImage
from PySide.QtCore import Slot, QThreadPool, QThread, QSize
from helpers import *
from wafThread import *
import tempfile
import tarfile
from datetime import datetime
import json

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
        centralLayout.setAlignment(Qt.AlignTop)
        gridWidget = QWidget()
        gridLayout = QGridLayout()
        gridWidget.setLayout(gridLayout)
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
        gridLayout.addWidget(generalGroup,0,0)
        # TRAFFIC
        trafficGroup = QGroupBox('Traffic Settings')
        trafficGroup.setLayout(QVBoxLayout())
        # m/s = (km/h)*1000/3600
        self.options['vel1'] = SimpleSpinOption('vel1','Average Speed (km/h)',105,True)
        self.options['vel1'].setRange(5,150)
        self.options['dis'] = SimpleComboboxOption('dis','Speed Distribution Model',3, False, 'Uniform','Exponential','Normal','Log Normal')
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
        gridLayout.addWidget(trafficGroup,0,1)
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
        gridLayout.addWidget(vanetGroup,1,0)
        # BATCH SETTINGS
        batchGroup = QGroupBox("Batch Settings")
        batchGroup.setLayout(QVBoxLayout())
        self.gapPrateOption = SimpleSpinOption('gapPrate', 'VANET percentage rate gap', 10, integer=True)
        self.sameSimuTimesOption = SimpleSpinOption('sameSimuTimes', 'How many times the same simulation', 100, integer=True)
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
        self.actionWhenDone.addItems(['When finished... Do nothing', 'When finished... Shutdown', 'When finished... Restart the simulations'])
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
                waf = WafThread(self.options, self.pathOption.getValue())
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
                result = "%3.3d\t%f" % (int(r['settings']['prate']),float(r['results']['timeToReachDest']))
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
        QSettings().setValue('actionWhenDone',self.actionWhenDone.currentIndex())
        QSettings().setValue('sameSimuTimes',self.sameSimuTimesOption.getValue())
        QSettings().setValue('gapPrate',self.gapPrateOption.getValue())
    def closeEvent(self, *args, **kwargs):
        self.saveSettings()
        try:
            for waf in self.simulations:
                del waf
            del self.simulations[:]
        except:
            pass
        super(HighwaySimulatorGui,self).closeEvent(*args, **kwargs)

class HighwayAnalyzeWidget(QWidget):
    def __init__(self):
        super(HighwayAnalyzeWidget,self).__init__()
        self.averageSimulationTime = 290.0
        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
        self.setLayout(mainLayout)
        gridWidget = QWidget()
        self.gridLayout = QGridLayout()
        gridWidget.setLayout(self.gridLayout)
        self.setupTopGroup()
        self.setupFilterGroup()
        self.layout().addWidget(gridWidget)
        # Analyze the results BUTTON
        self.analyzeResultsButton = QPushButton('Analyze the results')
        self.analyzeResultsButton.clicked.connect(self.analyzeResults)
        self.analyzeResultsButton.setEnabled(False)
        self.gridLayout.addWidget(self.analyzeResultsButton,0,1)
        # LOG
        self.logText = QTextBrowser()
        self.logText.setFont(QFont('Century Gothic', 7))
        self.gridLayout.addWidget(self.logText,1,1)
        self.results = []
        self.logFile = os.path.join(self.resultsPath(), 'analyze_'+os.uname()[1]+'.log')
        # Image
        self.picLabel = QLabel()
        self.picLabel.setAlignment(Qt.AlignHCenter)
        #self.picLabel.resize(800,600)
        self.picLabel.setMinimumSize(800,600)
        self.layout().addWidget(self.picLabel)
    def setupTopGroup(self):
        topGroup = QGroupBox("Simulation Results")
        self.resultsPathLineEdit = SimpleOption('resultsPath','Results Path','/home/thomas/Dropbox/Keio/research/results/')
        topGroupLayout = QVBoxLayout()
        topGroupLayout.setAlignment(Qt.AlignTop)
        topGroupLayout.addWidget(self.resultsPathLineEdit)
        self.loadResultsLabel = QLabel()
        self.loadResultsLabel.setAlignment(Qt.AlignHCenter)
        topGroupLayout.addWidget(self.loadResultsLabel)
        self.loadResultsButton = QPushButton("Load the results")
        self.loadResultsButton.clicked.connect(self.loadResults)
        topGroupLayout.addWidget(self.loadResultsButton)
        topGroup.setLayout(topGroupLayout)
        self.gridLayout.addWidget(topGroup,0,0)
    def resultsPath(self):
        return self.resultsPathLineEdit.getValue()
    def setupFilterGroup(self):
        filterGroup = QGroupBox('Filter the results')
        filterGroupLayout = QVBoxLayout()
        filterGroupLayout.setAlignment(Qt.AlignTop)
        # Distribution Model
        self.filterDistribution = SimpleComboboxOption('dis','Speed Distribution Model',3, True, 'Uniform','Exponential','Normal','Log Normal')
        filterGroupLayout.addWidget(self.filterDistribution)
        # Number of results per point
        self.filterNb = SimpleSpinOption('simuNbMin', 'Minimum results for a given setting', 10, integer=True, checkable=True)
        self.filterNb.checkBox.setChecked(True)
        filterGroupLayout.addWidget(self.filterNb)
        filterGroup.setLayout(filterGroupLayout)
        self.gridLayout.addWidget(filterGroup,1,0)
    def loadResults(self):
        self.loadResultsButton.setText('Loading the results...')
        self.loadResultsButton.setEnabled(False)
        self.results = []
        self.resultsThread = LoadResults(resultsPath=self.resultsPath())
        self.resultsThread.done.connect(self.loadResultsDone)
        self.resultsThread.error.connect(self.loadResultsError)
        self.resultsThread.start()
    @Slot(str)
    def loadResultsError(self, errorMsg):
        QMessageBox.critical(self, 'Error!', errorMsg)
        self.analyzeResultsButton.setEnabled(False)
    @Slot(dict)
    def loadResultsDone(self, results):
        self.results = results
        msg= 'Found %d Simulation Results' % len(self.results)
        self.loadResultsLabel.setText(msg)
        self.calculateAverageSimulationTime()
        self.loadResultsButton.setText('Reload the results')
        self.loadResultsButton.setEnabled(True)
        self.analyzeResultsButton.setEnabled(True)
    def calculateAverageSimulationTime(self):
        totalTime = 0
        nb = 0
        for r in self.results:
            if 'simulationTime' in r:
                #print 'simu time: %s' % r['simulationTime']
                totalTime += int(r['simulationTime'])
                nb += 1
            #print 'from %s: [%3.3f,%3.3f]' % (r['filename'], r['settings']['prate'],r['results']['timeToReachDest'])
        if nb<=0:
            errorMsg= 'No simulation found with simulationTime'
            QMessageBox.critical(self, 'Error!', errorMsg)
            self.averageSimulationTime = 290.0
        else:
            self.averageSimulationTime= totalTime/nb
            self.loadResultsLabel.setText(self.loadResultsLabel.text()+'\nAverage simulation time: %3.0f'%self.averageSimulationTime)
    def analyzeResults(self):
        if len(self.results)<=0:
            QMessageBox.critical(self, 'Error!', 'No results loaded :s')
            return
        self.log("=== ANALYZING RESULTS ===")
        self.logText.clear()
        p=0
        meanValues = {}
        with open(os.path.join(self.resultsPath(),'test.dat'),'w') as data:
            while p<=100:
                nb = 0
                totalTimeToReachDest = 0
                totalSimulationTime  = 0
                if self.filterDistribution.checkBox.isChecked():
                    fil = lambda x: x['settings']['prate']==p and x['settings']['dis']==self.filterDistribution.getValue()
                else:
                    fil = lambda x: x['settings']['prate']==p
                for result in filter(fil, self.results):
                    totalSimulationTime  += float(result['simulationTime'])
                    totalTimeToReachDest += float(result['results']['timeToReachDest'])
                    nb += 1
                if self.filterNb.checkBox.isChecked():
                    minNb = self.filterNb.getValue()
                else:
                    minNb = 0
                if nb>minNb:
                    meanSimulationTime  = float(1.0*totalSimulationTime/nb)
                    meanTimeToReachDest = float(1.0*totalTimeToReachDest/nb)
                    meanValues[p] = {'prate':p,
                                     'simuLationTime':meanSimulationTime,
                                     'simulationsNb':nb,
                                     'timeToReachDest':meanTimeToReachDest}
                    self.log(meanValues[p])
                    toPlot = '%s %s' % (p, meanValues[p]['timeToReachDest'])
                    #print toPlot
                    data.write(toPlot+'\n')
                p += 1
            data.close()
        outputPic = 'graphs/' + dateToFilename()
        s = subprocess.Popen(['./toPlot.sh', outputPic, self.resultsPath()], cwd=self.resultsPath())
        s.wait()
        outputPicPath = os.path.join(self.resultsPath(),outputPic+'.svg')
        pic = QImage(outputPicPath)
        #pic = pic.scaled(QSize(640,480))
        self.picLabel.setPixmap(QPixmap(pic))
        #os.system(os.path.join(self.resultsPath(),'toPlot.sh'))
    def log(self, txt):
        toLog = '%s | %s' % (datetime.now(), txt)
        with open(self.logFile, 'a') as logFile:
            logFile.write(toLog+'\n')
        self.logText.append(toLog)

class LoadResults(QThread):
    done = Signal(list)
    error = Signal(str)
    def __init__(self, resultsPath):
        super(LoadResults,self).__init__()
        self.resultsPath = resultsPath
    def run(self):
        results = []
        if os.path.exists(self.resultsPath):
            tempdir = tempfile.mkdtemp(prefix='results_tmpdir',dir=self.resultsPath)
            # temporary extract the tar.gz files in this folder
            for filename in filter(lambda x: x.endswith('.tar.gz') and x.startswith('results'), os.listdir(self.resultsPath)):
                tar = tarfile.open(os.path.join(self.resultsPath,filename), "r:gz")
                tar.extractall(tempdir)
                tar.close()
            for path, subdirs, files in os.walk(self.resultsPath):
                for name in filter(lambda x: x.endswith('.txt'), files):
                #for name in files:
                    filePath = os.path.join(path,name)
                    with open(filePath) as result:
                        try:
                            r = json.loads(result.read())
                        except:
                            #print 'errra with file %s' % name
                            pass
                        else:
                            r['filename'] = name
                            r['date'] = os.path.getctime(filePath)
                            if 'results' in r and 'timeToReachDest' in r['results']:
                                results.append(r)
                        result.close()
            # remove the temporary folder
            for filename in os.listdir(tempdir):
                os.remove(os.path.join(tempdir,filename))
            os.rmdir(tempdir)
            self.done.emit(results)
        else:
            errorMsg = 'The directory containing the results (%s) does not exist' % self.resultsPath
            self.error.emit(errorMsg)