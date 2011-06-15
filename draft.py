##!/usr/bin/env python
#from numpy.lib import *
#import Gnuplot
#from math import sin, pi
#
#x = linspace(0,10,31)
#y = x**2
#y2 = 10*sin(pi*x)
#g = Gnuplot.Gnuplot() #!! Won't be able to use 'with' in python 2.6?
#d = Gnuplot.Data(x,y,title='squared')
#d2=Gnuplot.Data(x,y2,title='sine')
#g('set grid')
#g.xlabel('x axis')
#g.ylabel('y axis')
#g.plot(d,d2)
#ans = raw_input('Enter f to create .png file, or Enter to quit ')
#if ans == 'f':
#    g.hardcopy('filename.png',terminal = 'png')
#    #g.hardcopy('filename.ps',terminal='postscript',enhanced=1,color=1)
#g.reset()


#import Gnuplot
#g = Gnuplot.Gnuplot()
#x = [1000,1001,1002,1003]
#y = [1,2,3,4]
#d = Gnuplot.Data(x,y,title='prout')
#g.plot(d)
#g.hardcopy('filename.png',terminal = 'svg')


import os
import Gnuplot

outputFolder = '/home/thomas/Dropbox/Keio/research/results'
if os.path.exists(outputFolder):
    for path, subdirs, files in os.walk(outputFolder):
        for name in filter(lambda x: x.endswith('_ambu.txt'), files):
            filePath = os.path.join(path,name)
            basename, ext = os.path.splitext(name)
            with open(filePath) as ambuResult:
                currentData = {'time':[],'pos':[],'vel':[],'velms':[]}
                currentAccData = {'time':[],'acc':[]}
                k   = 0
                mod = 10
                previousPos     = -1
                previousTime    = -1
                previousVel     = -1
                previousVelMS   = -1
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
                        previousVelMS = currentVelMS
                    previousTime = currentTime
                    previousPos  = currentPos
            print currentData
            print currentAccData
            g = Gnuplot.Gnuplot()
            x = currentData['time']
            v = currentData['vel']
            a = currentAccData['acc']
            d1 = Gnuplot.Data(x,v,title='velocity (km/h)',smooth='csplines with lines')
            #d1 = Gnuplot.Data(x,v,title='velocity (km/h)')
            #d2 = Gnuplot.Data(currentAccData['time'],a,title='acceleration (m/s2)',smooth='csplines with lines')
            d2 = Gnuplot.Data(currentAccData['time'],a,title='acceleration (m/s2)',smooth='freq with boxes')
            # 'smooth csplines  with lines'
            g.xlabel('Time (s)')
            #g.ylabel('Velocity (km/h)')
            g.title(name)
            g.plot(d1)
            g.hardcopy(basename+'_vel.svg',terminal='svg',enhanced=1,size='1024 768')
            #g.ylabel('Acceleration (m/s2)')
            #g('set style histogram')
            g.plot(d2)
            g.hardcopy(basename+'_acc.svg',terminal='svg',enhanced=1,size='1024 768')
            exit(0)