import numpy as np
import math

def multiplyMatrix(Matrix1, Matrix2):
    result = np.matmul(np.array(Matrix1), np.array(Matrix2))
    return result

def makeMatrix(rows, cols):
    return [([0]*cols) for row in range(rows)]

#scaling
def multiplyVector(vector, number):
    return ((vector[0]*number, vector[1]*number, vector[2]*number))  

def normalVector(A, B, C):
    ABx = B[0] - A[0]
    ABy = B[1] - A[1]
    ABz = B[2] - A[2]

    ACx = C[0] - A[0]
    ACy = C[1] - A[1]
    ACz = C[2] - A[2]

    AB = (ABx, ABy, ABz)
    AC = (ACx, ACy, ACz)

    result = np.cross(np.array(AB), np.array(AC))

    return ((result[0], result[1], result[2]))


def normalizeMatrix(vector):
    #getting L2 norm
    norm = np.linalg.norm(vector)
    if norm!=0:
        normal = vector/norm
        return normal
    return vector    

#from https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
def planeLineIntersection(planePoint, normal, linePointA, linePointB):
    normal = normalizeMatrix(normal)
    ABx = linePointB[0] - linePointA[0]
    ABy = linePointB[1] - linePointA[1]
    ABz = linePointB[2] - linePointA[2]
    #extravariable
    ABw = linePointB[3] - linePointA[3]
    AB = np.array([ABx, ABy, ABz, ABw]) #direction vector
    if np.dot(AB, normal) == 0: #line and plane are parallel
        return None
    else:
        #plane point - line point
        pPoint = np.array(planePoint)
        lPointA = np.array(linePointA)
        d = (np.subtract(pPoint, lPointA).dot(normal))/np.dot(AB, normal)
        intersection = lPointA + AB * d

        return intersection

#from https://mathinsight.org/distance_point_plane#:~:text=The%20shortest%20distance%20from%20a,as%20a%20gray%20line%20segment.
def distPointToPlane(planePoint, normal, point):
    normal = normalizeMatrix(normal)
    pPoint = np.array(planePoint)
    point = np.array(point)
    #note:cannot be abs val because shud be able to be negative :p
    return np.subtract(point, pPoint).dot(normal)

def distance(p1, p2):
    x1 = p1[0]
    y1 = p1[1]
    z1 = p1[2]

    x2 = p2[0]
    y2 = p2[1]
    z2 = p2[2]

    return math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

def magnitude(a):
    return math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
