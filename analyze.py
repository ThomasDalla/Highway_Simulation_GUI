__author__ = 'thomas'

import os
import json
from Gnuplot import *

results = []

resultsPath = '/home/thomas/Dropbox/Keio/research/results/'
if os.path.exists(resultsPath):
    for path, subdirs, files in os.walk(resultsPath):
        #for name in filter(lambda x: x.endswith(resultsPath), files):
        for name in files:
            if name!='summary.txt':
                # try json load
                with open(os.path.join(path,name)) as result:
                    try:
                        r = json.loads(result.read())
                        r['filename'] = name
                    except:
                        #print 'errra with file %s' % name
                        pass
                    else:
                        if 'results' in r and 'timeToReachDest' in r['results']:
                            if r['settings']['dis']==2:
                                results.append(r)
                    result.close()

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
    print 'No simulation found for the criteria'
    from sys import exit
    exit()

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
        if nb>0:
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