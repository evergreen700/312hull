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
        points = QPointXSort(points)
        t2 = time.time()
        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        polygon = pointsToLines(QPointHull(points))

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

def QPointHull(points):
    if len(points) <= 3:
        return points
    else:
        leftHull = QPointHull(points[:len(points)//2])
        rightHull = QPointHull(points[len(points)//2:])
        #find upper connection first:
        upperLeftEndIndex = len(leftHull) - 1
        upperRightEndIndex = 0
        modified = True
        while modified:
            modified = False
            while not isAbove(leftHull[upperLeftEndIndex], rightHull[upperRightEndIndex], leftHull):
                upperLeftEndIndex = (upperLeftEndIndex - 1) % len(leftHull)
                modified = True
            while not isAbove(leftHull[upperLeftEndIndex], rightHull[upperRightEndIndex], rightHull):
                upperRightEndIndex = (upperRightEndIndex + 1) % len(rightHull)
                modified = True

        #Basically the same for the lower connection:
        lowerLeftEndIndex = len(leftHull) - 1
        lowerRightEndIndex = 0
        modified = True
        while modified:
            modified = False
            while not isBelow(leftHull[lowerLeftEndIndex], rightHull[lowerRightEndIndex], leftHull):
                lowerLeftEndIndex = (lowerLeftEndIndex - 1) % len(leftHull)
                modified = True
            while not isBelow(leftHull[lowerLeftEndIndex], rightHull[lowerRightEndIndex], rightHull):
                lowerRightEndIndex = (lowerRightEndIndex + 1) % len(rightHull)
                modified = True

        finalPoints = []
        for i in range(0, len(leftHull)):
            if (leftHull[i].y() >= leftHull[-1].y()) & (i <= upperLeftEndIndex):
                finalPoints.append(leftHull[i])
            elif (leftHull[i].y() <= leftHull[-1].y()) & (i <= lowerLeftEndIndex):
                finalPoints.append(leftHull[i])

        for i in range(0, len(rightHull)):
            if (rightHull[i].y() >= rightHull[0].y()) & (i >= upperRightEndIndex):
                finalPoints.append(rightHull[i])
            elif (rightHull[i].y() <= rightHull[0].y()) & (i >= lowerRightEndIndex):
                finalPoints.append(rightHull[i])

        return finalPoints

def isAbove(leftEnd, rightEnd, testpoints):
    slope = (rightEnd.y()-leftEnd.y())/(rightEnd.x()-leftEnd.x())
    for p in testpoints:
        if p not in (leftEnd, rightEnd):
            if (p.x()-leftEnd.x())*slope+leftEnd.y() < p.y():
                return False
    return True

def isBelow(leftEnd, rightEnd, testpoints):
    slope = (rightEnd.y() - leftEnd.y()) / (rightEnd.x() - leftEnd.x())
    for p in testpoints:
        if p not in (leftEnd, rightEnd):
            if (p.x() - leftEnd.x()) * slope + leftEnd.y() > p.y():
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

