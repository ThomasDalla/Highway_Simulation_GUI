__author__ = 'thomas'

import os
import json
import tempfile
import tarfile
from datetime import datetime
from sys import exit

results = []
resultsPath = '/home/thomas/Dropbox/Keio/research/results/'
if os.path.exists(resultsPath):
    tempdir = tempfile.mkdtemp(prefix='results_tmpdir',dir=resultsPath)
    # temporary extract the tar.gz files in this folder
    for filename in filter(lambda x: x.endswith('.tar.gz'), os.listdir(resultsPath)):
        tar = tarfile.open(os.path.join(resultsPath,filename), "r:gz")
        tar.extractall(tempdir)
        tar.close()
    for path, subdirs, files in os.walk(resultsPath):
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
else:
    print 'The directory containing the results (%s) does not exist' % resultsPath
    exit()
print 'number of simulations found: %d' % len(results)

totalTime = 0
nb = 0
for r in results:
    if 'simulationTime' in r:
        #print 'simu time: %s' % r['simulationTime']
        totalTime += int(r['simulationTime'])
        nb += 1
    #print 'from %s: [%3.3f,%3.3f]' % (r['filename'], r['settings']['prate'],r['results']['timeToReachDest'])
if nb<=0:
    print 'No simulation found with simulationTime'
else:
    print 'Average Simulation Time: %d (among %d simulations)' % (int(int(totalTime)/int(nb)),nb)

p=0
meanValues = {}
with open(os.path.join(resultsPath,'test.dat'),'w') as data:
    while p<=100:
        nb = 0
        totalTimeToReachDest = 0
        totalSimulationTime  = 0
        for result in filter(lambda x: x['settings']['prate']==p, results):
            totalSimulationTime  += float(result['simulationTime'])
            totalTimeToReachDest += float(result['results']['timeToReachDest'])
            nb += 1
        if nb>10:
            meanSimulationTime  = float(1.0*totalSimulationTime/nb)
            meanTimeToReachDest = float(1.0*totalTimeToReachDest/nb)
            meanValues[p] = {'prate':p,
                             'simuLationTime':meanSimulationTime,
                             'simulationsNb':nb,
                             'timeToReachDest':meanTimeToReachDest}
            print meanValues[p]
            toPlot = '%s %s' % (p, meanValues[p]['timeToReachDest'])
            #print toPlot
            data.write(toPlot+'\n')
        p += 1
    data.close()

os.system(os.path.join(resultsPath,'toPlot.sh'))