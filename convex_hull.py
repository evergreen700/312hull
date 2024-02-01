from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
#elif PYQT_VER == 'PYQT4':
#    from PyQt4.QtCore import QLineF, QPointF, QObject
#elif PYQT_VER == 'PYQT6':
#    from PyQt6.QtCore import QLineF, QPointF, QObject
#else:
#    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
    def __init__( self):
        super().__init__()
        self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line,color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self,line,color):
        self.showTangent(line,color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon,color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self,polygon):
        self.view.clearLines(polygon)

    def showText(self,text):
        self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull
    def compute_hull( self, points, pause, view):
        self.pause = pause
        self.view = view
        assert( type(points) == list and type(points[0]) == QPointF )

        t1 = time.time()
        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        points.sort(key=lambda p: p.x())
        t2 = time.time()
        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        polygon = topBottomSplit(points)

        #[QLineF(points[i],points[(i+1)%3]) for i in range(3)]
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon,RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))


def QPointXSort(points):
    if len(points) == 1:
        return points
    else:
        pointsFinal = []
        points1 = QPointXSort(points[:len(points)//2])
        points2 = QPointXSort(points[len(points)//2:])
        while (len(points1) > 0) & (len(points2) > 0):
            if points1[0].x() > points2[0].x():
                pointsFinal.append(points2[0])
                points2 = points2[1:]
            else:
                pointsFinal.append(points1[0])
                points1 = points1[1:]
        
        pointsFinal = pointsFinal+points1+points2
        return pointsFinal

def topBottomSplit(points):
    slope = (points[-1].y() - points[0].y()) / (points[-1].x() - points[0].x())
    topPoints = [points[0]]
    bottomPoints = [points[0]]
    for p in points[1:-1]:
        if (p.x() - points[0].x()) * slope + points[0].y() < p.y():
            topPoints.append(p)
        else:
            bottomPoints.append(p)
    topPoints.append(points[-1])
    bottomPoints.append(points[-1])

    topHull = QPointTop2(topPoints)
    bottomHull = QPointBottom2(bottomPoints[::-1])
    orderedPoints = topHull[:-1]+bottomHull[:-1]
    return [QLineF(orderedPoints[i], orderedPoints[(i + 1) % len(orderedPoints)]) for i in range(len(orderedPoints))]

def QPointTopHull(points):
    if len(points) <= 3:
        return points
    else:
        leftHull = QPointTopHull(points[:len(points)//2])
        rightHull = QPointTopHull(points[len(points)//2:])
        #find upper connection first:
        leftEndIndex = len(leftHull) - 1
        rightEndIndex = 0
        modified = True
        while modified:
            modified = False
            while not isBelow(leftHull[leftEndIndex], rightHull[rightEndIndex], leftHull): #(getAngle(leftHull[leftEndIndex-1], leftHull[leftEndIndex], rightHull[rightEndIndex]) < 180) & (leftEndIndex > 0):
                leftEndIndex = (leftEndIndex - 1)
                modified = True
            while not isBelow(leftHull[leftEndIndex], rightHull[rightEndIndex], rightHull): #(getAngle(leftHull[leftEndIndex], rightHull[rightEndIndex], rightHull[rightEndIndex+1-len(rightHull)]) < 180) & (rightEndIndex < len(rightHull)):
                rightEndIndex = (rightEndIndex + 1)
                modified = True

        finalPoints = leftHull[:leftEndIndex+1]+rightHull[rightEndIndex:]
        return finalPoints

def QPointBottomHull(points):
    if len(points) <= 3:
        return points
    else:
        leftHull = QPointBottomHull(points[:len(points)//2])
        rightHull = QPointBottomHull(points[len(points)//2:])
        #find upper connection first:
        leftEndIndex = len(leftHull) - 1
        rightEndIndex = 0
        modified = True
        while modified:
            modified = False
            while not isAbove(leftHull[leftEndIndex], rightHull[rightEndIndex], leftHull):
                leftEndIndex = (leftEndIndex - 1) % len(leftHull)
                modified = True
            while not isAbove(leftHull[leftEndIndex], rightHull[rightEndIndex], rightHull):
                rightEndIndex = (rightEndIndex + 1) % len(rightHull)
                modified = True

        finalPoints = leftHull[:leftEndIndex+1]+rightHull[rightEndIndex:]
        return finalPoints


def getAngle(a, b, c):
    return QLineF(b, a).angleTo(QLineF(b,c))
def isConvex(left, center, right):
    slope = (right.y()-left.y())/(right.x()-left.x())
    return (center.x()-left.x())*slope+left.y() < center.y()

def isBelow(leftEnd, rightEnd, testpoints):
    slope = (rightEnd.y() - leftEnd.y()) / (rightEnd.x() - leftEnd.x())
    for p in testpoints:
        if p not in (leftEnd, rightEnd):
            if ((p.x() - leftEnd.x()) * slope + leftEnd.y()) < p.y():
                return False
    return True

def isAbove(leftEnd, rightEnd, testpoints):
    slope = (rightEnd.y() - leftEnd.y()) / (rightEnd.x() - leftEnd.x())
    for p in testpoints:
        if p not in (leftEnd, rightEnd):
            if ((p.x() - leftEnd.x()) * slope + leftEnd.y()) > p.y():
                return False
    return True

def pointsToLines(points):
    slope = (points[-1].y() - points[0].y()) / (points[-1].x() - points[0].x())
    topPoints = [points[0]]
    bottomPoints = []
    for p in points[1:-1]:
        if (p.x() - points[0].x()) * slope + points[0].y() > p.y():
            topPoints.append(p)
        else:
            bottomPoints.append(p)
    orderedPoints = topPoints + [points[-1]] + bottomPoints[::-1]
    return [QLineF(orderedPoints[i],orderedPoints[(i+1)%len(points)]) for i in range(len(points))]

def QPointTop2(points):
    finalPoints = points[:2]
    for i in range(2, len(points)):
        finalPoints.append(points[i])
        while len(finalPoints)>2:
            if isAbove2(finalPoints[-3], finalPoints[-2], finalPoints[-1]):
                break
            finalPoints.pop(-2)
    return finalPoints

def QPointBottom2(points):
    finalPoints = points[:2]
    for i in range(2, len(points)):
        finalPoints.append(points[i])
        while len(finalPoints)>2:
            if not isAbove2(finalPoints[-3], finalPoints[-2], finalPoints[-1]):
                break
            finalPoints.pop(-2)
    return finalPoints
def isAbove2(leftEnd, p, rightEnd):
    slope = (rightEnd.y() - leftEnd.y()) / (rightEnd.x() - leftEnd.x())
    return ((p.x() - leftEnd.x()) * slope + leftEnd.y()) < p.y()


