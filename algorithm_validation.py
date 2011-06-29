__author__ = 'thomas'

from PySide.QtGui import *
from PySide.QtCore import *

from helpers import *
from math import sqrt

# distance between two points:
def dist(p1,p2):
    x1 = p1.x()
    y1 = p1.y()
    x2 = p2.x()
    y2 = p2.y()
    return sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

def lineDist(l):
    return dist(l.p1(),l.p2())

def atIntersection(seg):
    if seg=='Q' or seg=='R' or seg=='S' or seg=='T':
        return True
    else:
        return False

def sameWay(seg1, seg2):
    if seg1==seg2\
    or (seg1=='A' and seg2=='B')\
    or (seg1=='B' and seg2=='A')\
    or (seg1=='C' and seg2=='D')\
    or (seg1=='D' and seg2=='C')\
    or (seg1=='E' and seg2=='F')\
    or (seg1=='F' and seg2=='E')\
    or (seg1=='G' and seg2=='H')\
    or (seg1=='H' and seg2=='G')\
    or (seg1=='I' and seg2=='J')\
    or (seg1=='J' and seg2=='I')\
    or (seg1=='K' and seg2=='L')\
    or (seg1=='L' and seg2=='K')\
    or (seg1=='M' and seg2=='N')\
    or (seg1=='N' and seg2=='M')\
    or (seg1=='O' and seg2=='P')\
    or (seg1=='P' and seg2=='O'):
        return True
    else:
        return False

def routesIntersect(path1, path2):
    for seg1 in path1:
        for seg2 in path2:
            if seg1 == seg2:
                return True
    return False

def redirect(carSeg,dst):
    # if the cars are in the GH segment
    if carSeg=='G' or carSeg=='H':
        if dst == 'W':
            return 'N'
        elif dst != 'E':
            return 'E'
        else:
            return 'N'
    elif carSeg=='A' or carSeg=='B':
        if dst=='E':
            return 'S'
        elif dst != 'W':
            return 'W'
        else:
            return 'S'
    elif carSeg=='K' or carSeg=='L':
        if dst == 'N':
            return 'E'
        elif dst != 'S':
            return 'S'
        else:
            return 'E'
    elif carSeg=='M' or carSeg=='N':
        if dst == 'S':
            return 'W'
        elif dst == 'W':
            return 'N'
        else:
            return 'W'


import sys

app = QApplication(sys.argv)
app.setApplicationName("Algorithm Validation")

dashPen = QPen(Qt.white)
dashPen.setStyle(Qt.DashLine)
dashPenRed = QPen(Qt.red)
dashPenRed.setStyle(Qt.DashLine)

class AlgorithmValidationWidget(QWidget):
    message = Signal(str)
    def __init__(self):
        QWidget.__init__(self)
        self.resize(300,300)
        self.setAttribute(Qt.WA_PaintOutsidePaintEvent)
    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 8))

        # white background
#        background = QRectF(0,0,300,300)
#        painter.drawRect(background)
#        painter.fillRect(background, Qt.white)

        # Roads
        horizontalRoad = QRectF(0,120,300,60)
        painter.fillRect(horizontalRoad, Qt.gray)
        verticalRoad = QRectF(120,0,60,300)
        painter.fillRect(verticalRoad, Qt.gray)
        painter.setPen(Qt.white)
        painter.drawLine(QLineF(0, 150, 120, 150))
        painter.drawLine(QLineF(180, 150, 300, 150))
        painter.drawLine(QLineF(150, 0, 150, 120))
        painter.drawLine(QLineF(150, 180, 150, 300))
        painter.setPen(dashPen)
        painter.drawLine(0, 135, 120, 135)
        painter.drawLine(0, 165, 120, 165)
        painter.drawLine(180, 135, 300, 135)
        painter.drawLine(180, 165, 300, 165)
        painter.drawLine(135, 0, 135, 120)
        painter.drawLine(165, 0, 165, 120)
        painter.drawLine(135, 180, 135, 300)
        painter.drawLine(165, 180, 165, 300)

        self.xSeg = {'A':125,'B':140,'C':155,'D':170,
                     'E':125,'F':140,'G':155,'H':170,
                     'I':5,'J':5,'K':5,'L':5,
                     'M':290,'N':290,'O':290,'P':290,
                     'Q':132,'R':162,'S':132,'T':162}
        self.ySeg = {'A':10,'B':10,'C':10,'D':10,
                     'E':295,'F':295,'G':295,'H':295,
                     'I':130,'J':145,'K':160,'L':175,
                     'M':130,'N':145,'O':160,'P':175,
                     'Q':140,'R':140,'S':168,'T':168}

        # Segment names
        painter.setPen(Qt.darkGray)
        painter.drawText(125,10,'A')
        painter.drawText(140,10,'B')
        painter.drawText(155,10,'C')
        painter.drawText(170,10,'D')
        painter.drawText(125,295,'E')
        painter.drawText(140,295,'F')
        painter.drawText(155,295,'G')
        painter.drawText(170,295,'H')
        painter.drawText(5,130,'I')
        painter.drawText(5,145,'J')
        painter.drawText(5,160,'K')
        painter.drawText(5,175,'L')
        painter.drawText(290,130,'M')
        painter.drawText(290,145,'N')
        painter.drawText(290,160,'O')
        painter.drawText(290,175,'P')
        painter.drawText(132, 140, 'Q')
        painter.drawText(162, 140, 'R')
        painter.drawText(132, 168, 'S')
        painter.drawText(162, 168, 'T')

    def placeCars(self, carSegment, carSegmentDiff, carDest, ambuSegment, ambuSegmentDiff, ambuDest, multipleLanes=True):
        #self.paintEvent('car')
        self.paintEvent('')
        # DEFAULT MESSAGE
        self.naviMessage = 'DISPLAY INFORMATION ONLY (1)'

        if carSegment==ambuSegment and (carSegmentDiff==ambuSegmentDiff or carSegment=='Q' or carSegment=='R' or carSegment=='S' or carSegment=='T'):
            QMessageBox.critical(self, 'Error', 'The car and the ambulance are at the same position.\nUse DIFF to put them on the same segment, different position.')
            return
        painter = QPainter(self)
        painter.setPen(Qt.black)
        self.carX = 0
        self.carY = 0

        # POSITION OF THE POINTS
        self.xPos = {'A':125,'B':140,'C':155,'D':170,
                     'E':125,'F':140,'G':155,'H':170,
                     'I':60,'J':60,'K':60,'L':60,
                     'M':240,'N':240,'O':240,'P':240,
                     'Q':132,'R':162,'S':132,'T':162}
        self.yPos = {'A':60,'B':60,'C':60,'D':60,
                     'E':240,'F':240,'G':240,'H':240,
                     'I':125,'J':140,'K':155,'L':165,
                     'M':125,'N':140,'O':155,'P':165,
                     'Q':130,'R':130,'S':160,'T':160}

        # CALCULATE THE CAR POSITION
        self.carX = self.xPos[carSegment]
        self.carY = self.yPos[carSegment]
        if carSegment=='A' or carSegment=='B' or carSegment=='C' or carSegment=='D'\
            or carSegment=='E' or carSegment=='F' or carSegment=='G' or carSegment=='H':
            self.carY += float(carSegmentDiff)*20
        elif carSegment!='Q' and carSegment!='R' and carSegment!='S' and carSegment!='T':
            self.carX += float(carSegmentDiff)*20

        # CALCULATE THE AMBULANCE POSITION
        self.ambuX = self.xPos[ambuSegment]
        self.ambuY = self.yPos[ambuSegment]
        if ambuSegment=='A' or ambuSegment=='B' or ambuSegment=='C' or ambuSegment=='D'\
            or ambuSegment=='E' or ambuSegment=='F' or ambuSegment=='G' or ambuSegment=='H':
            self.ambuY += float(ambuSegmentDiff)*20
        elif ambuSegment!='Q' and ambuSegment!='R' and ambuSegment!='S' and ambuSegment!='T':
            self.ambuX += float(ambuSegmentDiff)*20

        # POSSIBLE DIRECTIONS
        self.direction = dict()
        self.direction['W'] = [ ['A', 'Q', 'I'], ['B','Q','J'],
                                ['M', 'R', 'Q', 'I'], ['N','R','Q','J'],
                                ['G', 'T', 'R', 'Q', 'J'], ['H', 'T', 'R', 'Q', 'I'],
                                ['I'], ['J'],
                                ['Q', 'I'], ['R', 'Q', 'I'], ['T', 'R', 'Q', 'I']]
        self.direction['E'] = [ ['B', 'Q', 'S', 'T', 'O'], ['A', 'Q', 'S', 'T', 'P'],
                                ['K', 'S', 'T', 'O'], ['L', 'S', 'T', 'P'],
                                ['G', 'T', 'O'], ['H', 'T', 'P'],
                                ['T', 'P'], ['S', 'T', 'P'],['Q', 'S', 'T', 'P'],
                                ['E'], ['F']]
        self.direction['N'] = [ ['G', 'T','R', 'C'], ['H', 'T', 'R', 'D'],
                                ['M', 'R', 'D'], ['N', 'R', 'C'],
                                ['K', 'S', 'T', 'R', 'C'], ['L', 'S', 'T', 'R', 'D'],
                                ['S', 'T', 'R', 'D'], ['T', 'R', 'D'], ['R', 'D'],
                                ['C'], ['D']]
        self.direction['S'] = [ ['A', 'Q', 'S', 'E'], ['B', 'Q', 'S', 'F'],
                                ['K', 'S', 'F'], ['L', 'S', 'E'],
                                ['M', 'R', 'Q', 'S', 'E'], ['N', 'R', 'Q', 'S', 'F'],
                                ['R', 'Q', 'S', 'E'],['Q', 'S', 'E'],['S', 'E'],
                                ['E'], ['F']]

        # COPY OF THE POSSIBLE DIRECTIONS (otherwise car/ambu share the same pointer :s)
        self.direction2 = dict()
        self.direction2['W'] = [ ['A', 'Q', 'I'], ['B','Q','J'],
                                ['M', 'R', 'Q', 'I'], ['N','R','Q','J'],
                                ['G', 'T', 'R', 'Q', 'J'], ['H', 'T', 'R', 'Q', 'I'],
                                ['I'], ['J'],
                                ['Q', 'I'], ['R', 'Q', 'I'], ['T', 'R', 'Q', 'I']]
        self.direction2['E'] = [ ['B', 'Q', 'S', 'T', 'O'], ['A', 'Q', 'S', 'T', 'P'],
                                ['K', 'S', 'T', 'O'], ['L', 'S', 'T', 'P'],
                                ['G', 'T', 'O'], ['H', 'T', 'P'],
                                ['T', 'P'], ['S', 'T', 'P'],['Q', 'S', 'T', 'P'],
                                ['E'], ['F']]
        self.direction2['N'] = [ ['G', 'T','R', 'C'], ['H', 'T', 'R', 'D'],
                                ['M', 'R', 'D'], ['N', 'R', 'C'],
                                ['K', 'S', 'T', 'R', 'C'], ['L', 'S', 'T', 'R', 'D'],
                                ['S', 'T', 'R', 'D'], ['T', 'R', 'D'], ['R', 'D'],
                                ['C'], ['D']]
        self.direction2['S'] = [ ['A', 'Q', 'S', 'E'], ['B', 'Q', 'S', 'F'],
                                ['K', 'S', 'F'], ['L', 'S', 'E'],
                                ['M', 'R', 'Q', 'S', 'E'], ['N', 'R', 'Q', 'S', 'F'],
                                ['R', 'Q', 'S', 'E'],['Q', 'S', 'E'],['S', 'E'],
                                ['E'], ['F']]


        # Calculate the path to destination for the ambulance
        self.ambuPathSeg = None
        painter.setPen(Qt.white)
        for path in self.direction2[ambuDest]:
            if path[0]==ambuSegment:
                self.ambuPathSeg = path
        if self.ambuPathSeg is None:
            QMessageBox.critical(self, 'Error', 'The ambu cannot go there!')
            return
        else:
            #print self.ambuPathSeg
            if len(self.ambuPathSeg)>1:
                del self.ambuPathSeg[0]
            self.ambuPath = []
            previous_point = QPoint(self.ambuX, self.ambuY)
            for seg in self.ambuPathSeg:
                new_point = QPoint(self.xSeg[seg],self.ySeg[seg])
                self.ambuPath.append([previous_point, new_point])
                previous_point = new_point
            #print self.ambuPath
            for line in self.ambuPath:
                #print line
                painter.drawLine(*line)

        # Calculate the path to destination for the car
        self.carPathSeg = None
        painter.setPen(dashPenRed)
        for path in self.direction[carDest]:
            if path[0]==carSegment:
                self.carPathSeg = path
        if self.carPathSeg is None:
            QMessageBox.critical(self, 'Error', 'The car cannot go there!')
            return
        else:
            #print self.carPathSeg
            if len(self.carPathSeg)>1:
                del self.carPathSeg[0]
            self.carPath = []
            previous_point = QPoint(self.carX, self.carY)
            for seg in self.carPathSeg:
                new_point = QPoint(self.xSeg[seg],self.ySeg[seg])
                self.carPath.append([previous_point, new_point])
                previous_point = new_point
            #print self.carPath
            for line in self.carPath:
                #print line
                painter.drawLine(*line)

        # =========================
        # = PERFORM THE ALGORITHM =
        # =========================

        # distance of the first line of the car and the ambu
        carFirstLineDist = dist(*self.carPath[0])
        ambuFirstLineDist = dist(*self.ambuPath[0])

        # If the car is in its last segment
        # or at the intersection
        if len(self.carPathSeg)==1 or atIntersection(carSegment):
            # and the ambulance also
            if sameWay(carSegment, ambuSegment):
                # and even at the same segment
                if carSegment==ambuSegment:
                    # if the car is ahead
                    if carFirstLineDist < ambuFirstLineDist:
                        # and can change lane, we ask to change lane
                        if multipleLanes:
                            self.naviMessage = 'Please change lane, the ambulance is behind you'
                        # else if we have the same destination, change the car destination
                        elif carDest==ambuDest:
                            self.naviMessage = 'Please change your way to %s' % redirect(carSegment,carDest)
                        else: # else there is nothing we can do except continuing
                            self.naviMessage = 'Ambulance is behind you. Stick to your plan.'
                # else, we are in the same way, but not the same segment
                elif carFirstLineDist < ambuFirstLineDist:
                    # if we are ahead, give priority to the ambulance
                    self.naviMessage = 'Stay in this lane and slow down to let the ambulance go first.'
                # else, we should see it, no need to worry the driver more
            # else, we are not in the same way
            elif ambuDest==carDest and len(self.carPathSeg) < len(self.ambuPathSeg):
                # if the car is coming this way, let the driver know it
                self.naviMessage = 'Ambulance will come this way.'
            # else, there is nothing special to do (we are at the end segment and the ambu is not coming)

        # Else, if we are in the same way (but not the last one)
        elif sameWay(carSegment, ambuSegment):
            # and the same segment
            if ambuSegment==carSegment:
                # if the car is ahead
                if carFirstLineDist < ambuFirstLineDist:
                    # and can change lane, advise the driver to do so
                    if multipleLanes:
                        self.naviMessage = 'Please change lane, slow down, and let the ambulance go first.'
                    # else, if we have the same destination, change our way to the destination
                    elif carDest==ambuDest:
                        self.naviMessage = 'Please change your way to %s' % redirect(carSegment,carDest)
                    else: # else there is nothing we can do except continuing
                        self.naviMessage = 'Ambulance is behind you. Stick to your plan.'
            # else, we are in the same way but not the same segment
            elif carFirstLineDist < ambuFirstLineDist:
                # if we are ahead, let the driver know to stay in this lane but to slow down
                self.naviMessage = 'Stay in this lane and slow down to let the ambulance go first.'
            # else there is nothing special to do (same way, different segment, behind the ambu)

        # Else, if the ambu is at its last segment or at the intersection before its last segment
        # there is nothing special
        elif len(self.ambuPathSeg)==1 or atIntersection(ambuSegment):
            self.naviMessage = 'DISPLAY INFORMATION ONLY (2)'

        # else, we are in different ways and both going to cross the intersection
        # check if our routes intersect
        elif routesIntersect(self.ambuPathSeg, self.carPathSeg):
            self.naviMessage = 'STOP at the next intersection and let the ambulance go first.'
        # else, we are in different ways and are not going to cross our routes, just display info
        else:
            self.naviMessage = 'DISPLAY INFORMATION ONLY (3)'

        # Check if I'm on the same segment
        #if carSegment==ambuSegment:
            # Am I ahead or behind?

        self.message.emit(self.naviMessage)
        painter.fillRect(QRectF(self.carX, self.carY, 10,10), Qt.red)
        painter.fillRect(QRectF(self.ambuX, self.ambuY, 10,10), Qt.white)

class AlgorithmValidationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        centralLayout = QHBoxLayout()
        #centralLayout.setSpacing(0)
        centralLayout.setAlignment(Qt.AlignTop)
        self.resize(500,400)
        mainWidget.setLayout(centralLayout)

        # left part
        leftWidget = QGroupBox(mainWidget, "Visualisation")
        leftWidget.setLayout(QVBoxLayout())
        self.image = AlgorithmValidationWidget()
        self.image.setMinimumHeight(300)
        self.image.setMinimumWidth(300)
        self.image.message.connect(self.updateNavi)
        leftWidget.layout().addWidget(self.image)
        self.carNaviLabel = QLabel("CAR NAVI")
        self.carNaviLabel.setAlignment(Qt.AlignCenter)
        self.carNaviLabel.setFont(QFont("Century Gothic", 10))
        leftWidget.layout().addWidget(self.carNaviLabel)
        centralLayout.addWidget(leftWidget)

        # right part
        rightWidget = QWidget(mainWidget)
        rightWidget.setLayout(QVBoxLayout())
        # CAR
        carBox = QGroupBox("Car settings")
        carBox.setLayout(QVBoxLayout())
        self.carSegmentOption = SimpleComboboxOption('carseg','Segment',0, False, 'A','B','C','D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T')
        self.carDiffOption = SimpleComboboxOption('cardif','Difference',1, False, '+1','0','-1')
        self.carDestOption = SimpleComboboxOption('cardest','Destination',2, False, 'N', 'S', 'W', 'E')
        carBox.layout().addWidget(self.carSegmentOption)
        carBox.layout().addWidget(self.carDiffOption)
        carBox.layout().addWidget(self.carDestOption)
        rightWidget.layout().addWidget(carBox)
        # AMBU
        ambuBox = QGroupBox("Ambu settings")
        ambuBox.setLayout(QVBoxLayout())
        self.ambuSegmentOption = SimpleComboboxOption('ambuseg','Segment',6, False, 'A','B','C','D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T')
        self.ambuDiffOption = SimpleComboboxOption('ambudif','Difference',1, False, '+1','0','-1')
        self.ambuDestOption = SimpleComboboxOption('ambudest','Destination',2, False, 'N', 'S', 'W', 'E')
        ambuBox.layout().addWidget(self.ambuSegmentOption)
        ambuBox.layout().addWidget(self.ambuDiffOption)
        ambuBox.layout().addWidget(self.ambuDestOption)
        rightWidget.layout().addWidget(ambuBox)
        # Button
        self.applyButton = QPushButton('APPLY')
        self.applyButton.clicked.connect(self.applySettings)
        rightWidget.layout().addWidget(self.applyButton)
        centralLayout.addWidget(rightWidget)
    def updateNavi(self, msg):
        #self.carNaviLabel.setText('<div style="background-color:black"><font color="red">%s</font></div>'%msg.replace('\n','<br />'))
        self.carNaviLabel.setText('<font color="red">%s</font>'%msg.replace('\n','<br />'))
    def applySettings(self):
        self.image.placeCars(self.carSegmentOption.getName(), self.carDiffOption.getName(), self.carDestOption.getName(),
                             self.ambuSegmentOption.getName(), self.ambuDiffOption.getName(), self.ambuDestOption.getName())

mw = AlgorithmValidationWindow()
mw.show()

sys.exit(app.exec_())