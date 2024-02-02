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
        points.sort(key=lambda p: p.x())
        t2 = time.time()
        t3 = time.time()
        #Calling the hull function on the sorted points
        polygon = topBottomSplit(points)
        t4 = time.time()

        self.showHull(polygon,RED)
        self.showText('Time Elapsed (Convex Hull): {:3.5f} sec'.format(t4-t3))


#This function splits the sorted points into an upper and lower part, then calls the convex hull functions on each part
def topBottomSplit(points):
    slope = (points[-1].y() - points[0].y()) / (points[-1].x() - points[0].x())
    topPoints = [points[0]]
    bottomPoints = [points[0]]
    for p in points[1:-1]:
        if (p.x() - points[0].x()) * slope + points[0].y() < p.y():
            topPoints.append(p)
        else:
            bottomPoints.append(p)
    #After this last append, the top and bottom point arrays each start with the farthest left point overall, and end with the farthest right point overall.
    #These points are guaranteed to be in the hull so it is good to use them for joining later on.
    topPoints.append(points[-1])
    bottomPoints.append(points[-1])

    #Calling the actual hull functions on each half.
    topHull = QPointTopHull(topPoints)
    bottomHull = QPointBottomHull(bottomPoints)
    #Combining the halfs (bottom half gets reversed so the whole thing is in clockwise order, and duplicate ends are taken off.
    orderedPoints = topHull[:-1]+bottomHull[-1:0:-1]
    #This final line turns the array of points into an array of lines
    return [QLineF(orderedPoints[i], orderedPoints[(i + 1) % len(orderedPoints)]) for i in range(len(orderedPoints))]

def QPointTopHull(points):
    #Normally, we would have a set of points size 3 as our base case. Since I split the top and bottom parts,
    #I'm not sure if the point in the middle of a set of 3 should be in the hull. If the first and last point are in the final hull, the middle point will not be checked.
    #So, we set the base case as 1 or 2 points, not 3.
    if len(points) <= 2:
        return points
    else:
        #Splitting into left and right halves to call recursively
        leftHull = QPointTopHull(points[:len(points)//2])
        rightHull = QPointTopHull(points[len(points)//2:])
        #These indexes represent the farthest right point on the left part and the farthest left point on the right part
        leftEndIndex = len(leftHull) - 1
        rightEndIndex = 0
        modified = True
        #loop until we do a full iteration without changing left or right end index
        while modified:
            modified = False
            while isBelow(leftHull[leftEndIndex], rightHull[rightEndIndex], leftHull[leftEndIndex-1:leftEndIndex]):
                #if the upper tangent line is above the next point (if it exists)
                leftEndIndex = (leftEndIndex - 1)
                modified = True
            while isBelow(leftHull[leftEndIndex], rightHull[rightEndIndex], rightHull[rightEndIndex+1:rightEndIndex+2]):
                #if the upper tangent line is below the next point (if it exists)
                rightEndIndex = (rightEndIndex + 1)
                modified = True

        finalPoints = leftHull[:leftEndIndex+1]+rightHull[rightEndIndex:]
        return finalPoints

#This function is basically the same as the top function, just checking for lower tangent when combining instead of upper tangent
def QPointBottomHull(points):
    if len(points) <= 2:
        return points
    else:
        leftHull = QPointBottomHull(points[:len(points)//2])
        rightHull = QPointBottomHull(points[len(points)//2:])
        leftEndIndex = len(leftHull) - 1
        rightEndIndex = 0
        modified = True
        while modified:
            modified = False
            while isAbove(leftHull[leftEndIndex], rightHull[rightEndIndex], leftHull[leftEndIndex-1:leftEndIndex]):
                leftEndIndex = (leftEndIndex - 1)
                modified = True
            while isAbove(leftHull[leftEndIndex], rightHull[rightEndIndex], rightHull[rightEndIndex+1:rightEndIndex+2]):
                rightEndIndex = (rightEndIndex + 1)
                modified = True

        finalPoints = leftHull[:leftEndIndex+1]+rightHull[rightEndIndex:]
        return finalPoints


#Functions for examining if any of the points are above or below a specific line.
def isBelow(leftEnd, rightEnd, testpoints):
    slope = (rightEnd.y() - leftEnd.y()) / (rightEnd.x() - leftEnd.x())
    for p in testpoints:
        if ((p.x() - leftEnd.x()) * slope + leftEnd.y()) < p.y():
            return True
    return False

def isAbove(leftEnd, rightEnd, testpoints):
    slope = (rightEnd.y() - leftEnd.y()) / (rightEnd.x() - leftEnd.x())
    for p in testpoints:
        if ((p.x() - leftEnd.x()) * slope + leftEnd.y()) > p.y():
            return True
    return False