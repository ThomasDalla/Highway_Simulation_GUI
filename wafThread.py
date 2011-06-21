__author__ = 'thomas'

from PySide.QtCore import QObject, Signal, QRunnable
import subprocess, threading
import os, json, random
from datetime import datetime
import Gnuplot

def dateToFilename(d=-1,rn=-1,prate=-1):
    prateStr = ''
    if prate>=0:
        prateStr = '_pr%.3d' % prate
    if rn==-1:
        rn=random.randint(1,10000)
    if d==-1:
        d= datetime.now()
    return '-'.join([str(d.year),'%2.2d'%d.month,'%2.2d'%d.day])+'_'+'-'.join(['%2.2d'%d.hour,'%2.2d'%d.minute,'%2.2d'%d.second])+'_'+'%.7d'%rn+prateStr
    #return '-'.join([str(d.year),'%2.2d'%d.month,'%2.2d'%d.day])+'_'+'-'.join(['%2.2d'%d.hour,'%2.2d'%d.minute,'%2.2d'%d.second])+'_'+'%d'%d.microsecond

#class Ns2Command(object):
#    def __init__(self, options, stdout, scenario='vanet-highway-test-thomas', command='./waf',cwd='/home/thomas/soft/ns-3.9'):
#        super(Ns2Command,self).__init__()
#        self.options    = options
#        self.scenario   = scenario
#        self.command    = command
#        self.cwd        = cwd
#        self.stdout     = stdout
#        self.process    = None
#    def run(self, timeout=1500):
#        def target():
#            #print 'Thread started'
#            #self.process = subprocess.Popen(self.cmd, shell=True)
#            self.process = subprocess.Popen([self.command, '--run', self.scenario+self.options], stdout=self.stdout, cwd='/home/thomas/soft/ns-3.9')
#            self.process.communicate()
#            #print 'Thread finished'
#
#        thread = threading.Thread(target=target)
#        thread.start()
#
#        thread.join(timeout)
#        if thread.is_alive():
#            #print 'Terminating process'
#            self.process.terminate()
#            thread.join()
#        return self.process.returncode

class WafThread(QRunnable, QObject):
    simuDone = Signal(str)
    def __init__(self, options, outputFolder, scenario='vanet-highway-test-thomas'):
        QRunnable.__init__(self)
        QObject.__init__(self)
        self.options = ''
        self.optionsDict = options
        self.prate = options['prate']
        #print self.optionsDict
        for option in options:
            if option=='vel1' or option=='spl':
                speedInMs = options[option].getValue()*1000/3600
                self.options += ' --%s=%s' % (option, speedInMs)
            else:
                self.options += ' --%s=%s' % (option, options[option])
        self.runNumber = random.randint(1,10000)
        #self.runNumber = 1
        self.options += ' --rn=%d' % self.runNumber   # randomize the results
        self.command = './waf'
        self.scenario = scenario
        self.outputFolder = outputFolder
        settings = {}
        for option in options:
            #self.output['settings'][option+'| '+self.options[option].getName()] = self.options[option].getValue()
            if option=='prate':
                settings[option] = options[option]
            else:
                settings[option] = options[option].getValue()
        self.output = {'settings':settings,'command':'%s %s%s' % (self.command, ' --run \'', self.scenario+self.options+'\'')}
    def run(self, *args, **kwargs):
        outputBase = os.path.join(self.outputFolder,dateToFilename(datetime.now(), self.runNumber, prate=self.prate))
        self.outputFile = outputBase+'.txt'
        self.outputAmbu = outputBase+'_ambu.txt'
        basename, ext = os.path.splitext(self.outputFile)
        self.options += ' --ambu=1 --af=%s' % self.outputAmbu
        out = open(self.outputFile, 'w')

#        command = Ns2Command(self.options, out, scenario=self.scenario)
#        returnCode = command.run()
        self.startTime = datetime.now()
        #print 'launching process...'
        process = subprocess.Popen(['./waf', '--run', self.scenario+self.options], stdout=out, cwd='/home/thomas/soft/ns-3.9')
        #print 'launched!'
        process.communicate()
        #print 'process done'
        returnCode = process.returncode
        #print 'return code: %d' % returnCode

        out.close()
        out = open(self.outputFile, 'r')
        result = out.read()
        out.close()
        self.output['returnCode'] = returnCode
        self.output['simulationTime'] = (datetime.now()-self.startTime).seconds
        if returnCode==0 or returnCode==-15:
            #print result
            jsonResult = '{\n'+result+'"end":"True"\n}'
            try:
                jsonR = json.loads(jsonResult)
                self.output['results'] = jsonR
                self.output['succeed'] = 1
            except ValueError:
                self.output['results'] = result
                self.output['succeed'] = "Error decoding Json Result"
            else:
                hasRead = False
                tries=0
                while (not hasRead) and (tries<10):
                    tries += 1
                    try: # Try to read the ambu file
                        ambuResult = open(self.outputAmbu)
                    except IOError: # If there is an error, sleep
                        from time import sleep
                        sleep(5)
                    else: # else go to the next step!
                        hasRead =  True
                if hasRead:
                    currentData = {'time':[],'pos':[],'vel':[],'velms':[]}
                    currentAccData = {'time':[],'acc':[]}
                    k   = 0
                    mod = 10
                    previousPos     = -1
                    previousTime    = -1
                    previousVel     = -1
                    #previousVelMS   = -1
                    previousVelSum  = -1
                    previousTimeSum = -1
                    currentVelSum   = 0
                    for line in ambuResult:
                        r =line.replace('\n','').split(' ')
                        currentTime = float(r[0])-1000.0
                        currentPos  = float(r[1])
                        if previousPos>-1:
                            # calculate velocity
                            currentVelMS = (currentPos-previousPos)/(currentTime-previousTime)
                            currentVel = currentVelMS*3600.0/1000.0
                            currentVelSum += currentVelMS
                            if previousVel>-1:
                                #acc = (currentVelMS-previousVelMS)/(currentTime-previousTime)
                                currentData['time'].append(currentTime)
                                currentData['pos'].append(currentPos)
                                currentData['vel'].append(currentVel)
                                currentData['velms'].append(currentVelMS)
                                k = (k+1) % mod
                                if k==0:
                                    if previousVelSum>-1:
                                        acc = (currentVelSum-previousVelSum)/(mod*(currentTime-previousTimeSum))
                                        currentAccData['acc'].append(acc)
                                        currentAccData['time'].append(currentTime)
                                    previousVelSum = currentVelSum
                                    previousTimeSum = currentTime
                                    currentVelSum = 0
                            previousVel = currentVel
                            #previousVelMS = currentVelMS
                        previousTime = currentTime
                        previousPos  = currentPos
                    ambuResult.close()
                    # Gnuplot
                    g = Gnuplot.Gnuplot()
                    x = currentData['time']
                    v = currentData['vel']
                    a = currentAccData['acc']
                    d1 = Gnuplot.Data(x,v,title='velocity (km/h)',smooth='csplines with lines')
                    d2 = Gnuplot.Data(currentAccData['time'],a,title='acceleration (m/s2)',smooth='freq with boxes')
                    # 'smooth csplines  with lines'
                    g.xlabel('Time (sec.)')
                    #g.ylabel('Velocity (km/h)')
                    # update basename
                    minGapStr = maxGapStr = gapStr = ''
                    if 'minGapLane0' in jsonR:
                        minGapStr = '_gMin%.3d' % jsonR['minGapLane0']
                    if 'maxGapLane0' in jsonR:
                        maxGapStr = '_gMax%.4d' % jsonR['maxGapLane0']
                    if 'averageGapOnLane0' in jsonR:
                        gapStr = '_g%.4d' % jsonR['averageGapOnLane0_New']
                    basename += minGapStr+gapStr+maxGapStr
                    try:
                        t = '[prate:%d][dis:%d][gap:%2.2f][flow:%2.2f][maxFlow:%2.2f]'\
                        % (self.prate,
                           self.optionsDict['dis'].getValue(),
                           self.optionsDict['gap'].getValue(),
                           self.optionsDict['flow1'].getValue(),
                           self.optionsDict['maxflow'].getValue())
                    except:
                        t = basename
                    g.title(t)
                    g.plot(d1)
                    g.hardcopy(filename=basename+'_vel.svg',terminal='svg',enhanced=1,size='1024 768')
                    #g.ylabel('Acceleration (m/s2)')
                    g.plot(d2)
                    g.hardcopy(basename+'_acc.svg',terminal='svg',enhanced=1,size='1024 768')
                else:
                    self.output['results']['ambuDebug'] = 'Impossible to read %s' % self.outputAmbu
        else:
            self.output['results'] = result
            self.output['succeed'] = 0
        with open(self.outputFile,'w') as outFile:
            outFile.write(json.dumps(self.output, sort_keys=True, indent=4))
            outFile.close()
        self.simuDone.emit(self.outputFile)
