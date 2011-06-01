__author__ = 'thomas'

from helpers import *
from wafThread import *
import os
import tarfile
import tempfile
from PySide.QtGui import QWidget, QLabel, QVBoxLayout, QGroupBox, QPushButton, QMessageBox, QTextBrowser, QFont, QPixmap, QImage, QTextOption
from PySide.QtCore import Slot, QThread, Qt

class HighwayAnalyzeWidget(QWidget):
    def __init__(self):
        super(HighwayAnalyzeWidget,self).__init__()
        self.averageSimulationTime = 290.0
        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        topWidget = QWidget()
        self.topLayout = QHBoxLayout()
        self.topLayout.setSpacing(0)
        topWidget.setLayout(self.topLayout)
        topLeftWidget = QWidget()
        self.topLeftLayout = QVBoxLayout()
        topLeftWidget.setLayout(self.topLeftLayout)
        self.setupTopGroup()
        self.setupFilterGroup()
        self.topLayout.addWidget(topLeftWidget)
        self.layout().addWidget(topWidget)
        # Button and log
        buttonAndLogWidget = QWidget()
        buttonAndLogWidget.setLayout(QVBoxLayout())
        # Analyze the results BUTTON
        self.analyzeResultsButton = QPushButton('Analyze the results')
        self.analyzeResultsButton.clicked.connect(self.analyzeResults)
        self.analyzeResultsButton.setEnabled(False)
        buttonAndLogWidget.layout().addWidget(self.analyzeResultsButton)
        # LOG
        self.logText = QTextBrowser()
        self.logText.setFont(QFont('Century Gothic', 7))
        self.logText.setWordWrapMode(QTextOption.NoWrap)
        buttonAndLogWidget.layout().addWidget(self.logText)
        self.topLayout.addWidget(buttonAndLogWidget)
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
        topGroupLayout.setSpacing(0)
        topGroupLayout.setAlignment(Qt.AlignTop)
        topGroupLayout.addWidget(self.resultsPathLineEdit)
        self.loadResultsLabel = QLabel()
        self.loadResultsLabel.setAlignment(Qt.AlignHCenter)
        topGroupLayout.addWidget(self.loadResultsLabel)
        self.loadResultsButton = QPushButton("Load the results")
        self.loadResultsButton.clicked.connect(self.loadResults)
        topGroupLayout.addWidget(self.loadResultsButton)
        topGroup.setLayout(topGroupLayout)
        self.topLeftLayout.addWidget(topGroup)
    def resultsPath(self):
        return self.resultsPathLineEdit.getValue()
    def setupFilterGroup(self):
        filterGroup = QGroupBox('Filter the results')
        filterGroupLayout = QVBoxLayout()
        filterGroupLayout.setSpacing(0)
        filterGroupLayout.setAlignment(Qt.AlignTop)
        # Distribution Model
        self.filterDistribution = SimpleComboboxOption('dis','Speed Distribution Model',3, True, 'Uniform','Exponential','Normal','Log Normal')
        filterGroupLayout.addWidget(self.filterDistribution)
        # Number of results per point
        self.filterNb = SimpleSpinOption('simuNbMin', 'Minimum results for a given setting', 10, integer=True, checkable=True)
        self.filterNb.checkBox.setChecked(True)
        filterGroupLayout.addWidget(self.filterNb)
        # Filter the date
        dateWidget = QWidget()
        dateWidget.setLayout(QHBoxLayout())
        self.filterDate = QCheckBox('After')
        self.filterDate.setChecked(QSettings().value('filterDate','0')=='1')
        dateWidget.layout().addWidget(self.filterDate)
        self.filterDateYear = QComboBox()
        for m in xrange(2010,2012):
            self.filterDateYear.addItem(str(m))
        self.filterDateYear.setCurrentIndex(int(QSettings().value('dateYear', 1)))
        dateWidget.layout().addWidget(self.filterDateYear)
        dateWidget.layout().addWidget(QLabel('Year'))
        self.filterDateMonth = QComboBox()
        for m in xrange(1,13):
            self.filterDateMonth.addItem(str(m))
        self.filterDateMonth.setCurrentIndex(int(QSettings().value('dateMonth', 4)))
        dateWidget.layout().addWidget(self.filterDateMonth)
        dateWidget.layout().addWidget(QLabel('Month'))
        self.filterDateDay = QComboBox()
        for d in xrange(1,32):
            self.filterDateDay.addItem(str(d))
        self.filterDateDay.setCurrentIndex(int(QSettings().value('dateDay', 0)))
        dateWidget.layout().addWidget(self.filterDateDay)
        dateWidget.layout().addWidget(QLabel('Day'))
        filterGroupLayout.addWidget(dateWidget)
        filterGroup.setLayout(filterGroupLayout)
        self.topLeftLayout.addWidget(filterGroup)
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
        self.analyzeResults()
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
    def fil(self, r):
        return self.checkDis(r) and self.checkDate(r)
    def checkDis(self,r):
        return (not self.filterDistribution.checkBox.isChecked()) or r['settings']['dis']==self.filterDistribution.getValue()
    def checkDate(self, r):
        return (not self.filterDate.isChecked()) or (r['date'] >= datetime(int(self.filterDateYear.currentText()), int(self.filterDateMonth.currentText()), int(self.filterDateDay.currentText())))
    def analyzeResults(self):
        self.saveSettings()
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
                for result in filter(lambda x: x['settings']['prate']==p and self.fil(x), self.results):
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
        if len(meanValues)>0:
            outputPic = 'graphs/' + dateToFilename()
            s = subprocess.Popen(['./toPlot.sh', outputPic, self.resultsPath()], cwd=self.resultsPath())
            s.wait()
            outputPicPath = os.path.join(self.resultsPath(),outputPic+'.svg')
            pic = QImage(outputPicPath)
            #pic = pic.scaled(QSize(640,480))
            self.picLabel.setPixmap(QPixmap(pic))
            #os.system(os.path.join(self.resultsPath(),'toPlot.sh'))
        else:
            QMessageBox.critical(self, 'Error!', 'No simulation satisfies the criteria...')
    def log(self, txt):
        toLog = str(txt)
        with open(self.logFile, 'a') as logFile:
            logFile.write(toLog+'\n')
        self.logText.append(toLog)
    def saveSettings(self):
        QSettings().setValue('simuNbMin', self.filterNb.getValue())
        QSettings().setValue('dis', self.filterDistribution.getValue())
        QSettings().setValue('dateDay', self.filterDateDay.currentIndex())
        QSettings().setValue('dateMonth', self.filterDateMonth.currentIndex())
        QSettings().setValue('dateYear', self.filterDateYear.currentIndex())
        if self.filterDate.isChecked():
            QSettings().setValue('filterDate', '1')
        else:
            QSettings().setValue('filterDate', '0')

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
                            r['date'] = datetime.fromtimestamp(os.path.getmtime(filePath))
                            #print r['date']
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