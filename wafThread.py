__author__ = 'thomas'

from PySide.QtCore import QObject, Signal, QRunnable
import subprocess, threading
import os, json, random
from datetime import datetime

def dateToFilename(d=-1,rn=-1):
    if rn==-1:
        rn=random.randint(1,10000)
    if d==-1:
        d= datetime.now()
    return '-'.join([str(d.year),'%2.2d'%d.month,'%2.2d'%d.day])+'_'+'-'.join(['%2.2d'%d.hour,'%2.2d'%d.minute,'%2.2d'%d.second])+'_'+'%.7d'%rn
    #return '-'.join([str(d.year),'%2.2d'%d.month,'%2.2d'%d.day])+'_'+'-'.join(['%2.2d'%d.hour,'%2.2d'%d.minute,'%2.2d'%d.second])+'_'+'%d'%d.microsecond

class Ns2Command(object):
    def __init__(self, options, stdout, scenario='vanet-highway-test-thomas', command='./waf',cwd='/home/thomas/soft/ns-3.9'):
        super(Ns2Command,self).__init__()
        self.options    = options
        self.scenario   = scenario
        self.command    = command
        self.cwd        = cwd
        self.stdout     = stdout
        self.process    = None
    def run(self, timeout=1500):
        def target():
            #print 'Thread started'
            #self.process = subprocess.Popen(self.cmd, shell=True)
            self.process = subprocess.Popen([self.command, '--run', self.scenario+self.options], stdout=self.stdout, cwd='/home/thomas/soft/ns-3.9')
            self.process.communicate()
            #print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            #print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode

class WafThread(QRunnable, QObject):
    simuDone = Signal(str)
    def __init__(self, options, outputFolder, scenario='vanet-highway-test-thomas'):
        QRunnable.__init__(self)
        QObject.__init__(self)
        self.options = ''
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
        self.outputFile = os.path.join(self.outputFolder,dateToFilename(datetime.now(), self.runNumber)+'.txt')
        out = open(self.outputFile, 'w')
        command = Ns2Command(self.options, out)
        self.startTime = datetime.now()
        returnCode = command.run()
        out.close()
        out = open(self.outputFile, 'r')
        result = out.read()
        out.close()
        self.output['returnCode'] = returnCode
        self.output['simulationTime'] = (datetime.now()-self.startTime).seconds
        if returnCode==0:
            #print result
            jsonResult = '{\n'+result+'"end":"True"\n}'
            try:
                self.output['results'] = json.loads(jsonResult)
                self.output['succeed'] = 1
            except:
                self.output['results'] = result
                self.output['succeed'] = "Error decoding Json Result"
        else:
            self.output['results'] = result
            self.output['succeed'] = 0
        with open(self.outputFile,'w') as outFile:
            outFile.write(json.dumps(self.output, sort_keys=True, indent=4))
            outFile.close()
        self.simuDone.emit(self.outputFile)
