import math
import vectorFunctions as vf
import numpy as np

#X, Y and Z Rotation matrices taken (and adapted) from https://en.wikipedia.org/wiki/Rotation_matrix
def rotationXMatrix(theta):
    rows = cols = 4
    matrix = vf.makeMatrix(rows, cols)

    matrix[0][0] = 1
    matrix[1][1] = math.cos(theta)
    matrix[1][2] = math.sin(theta)
    matrix[2][1] = -math.sin(theta)
    matrix[2][2] = math.cos(theta)
    matrix[3][3] = 1

    return matrix


def rotationYMatrix(theta):
    rows = cols = 4
    matrix = vf.makeMatrix(rows, cols)

    matrix[0][0] = math.cos(theta)
    matrix[0][2] = math.sin(theta)
    matrix[1][1] = 1
    matrix[2][0] = -math.sin(theta)
    matrix[2][2] = math.cos(theta)
    matrix[3][3] = 1

    return matrix



def rotationZMatrix(theta):
    rows = cols = 4
    matrix = vf.makeMatrix(rows, cols)

    matrix[0][0] = math.cos(theta)
    matrix[0][1] = math.sin(theta)
    matrix[1][0] = -math.sin(theta)
    matrix[1][1] = math.cos(theta)
    matrix[2][2] = 1
    matrix[3][3] = 1

    return matrix


def translationMatrix(x, y, z):
    rows = cols = 4
    matrix = vf.makeMatrix(rows, cols)
    
    matrix[0][0] = 1
    matrix[1][1] = 1
    matrix[2][2] = 1
    matrix[3][3] = 1
    matrix[3][0] = x
    matrix[3][1] = y
    matrix[3][2] = z

    return matrix

#pos is where object should be. vecDir is forward vector

#Calculations based from: https://www.youtube.com/watch?v=3ZmqJb7J5wE&list=PLW3Zl3wyJwWOpdhYedlD-yCB7WQoHf-My&index=39 (8:57)
def viewMatrix(app, vecPos, vecDir, vecUp):
    rows = cols = 4
    matrixR = vf.makeMatrix(rows, cols)
    matrixT = vf.makeMatrix(rows, cols)

    vPos = np.array(vecPos)
    vDir = np.array(vecDir)
    vUp = np.array(vecUp)

    #forward
    #normalize this
    vecForward = np.subtract(vDir, vPos)
    vecForward = np.array(vf.normalizeMatrix(vecForward))

    #up
    a = vecForward * vUp.dot(vecForward)
    #normalize this
    vecUp = np.subtract(vUp, a)
    vecUp = vf.normalizeMatrix(vecUp)

    vecRight = np.cross(vecUp, vecForward)

    matrixR[0][0] = vecRight[0]
    matrixR[1][0] = vecRight[1]
    matrixR[2][0] = vecRight[2]
    matrixR[0][1] = vecUp[0]
    matrixR[1][1] = vecUp[1]
    matrixR[2][1] = vecUp[2]
    matrixR[0][2] = vecForward[0]
    matrixR[1][2] = vecForward[1]
    matrixR[2][2] = vecForward[2]
    matrixR[3][3] = 1

    matrixT[0][0] = 1
    matrixT[1][1] = 1
    matrixT[2][2] = 1
    matrixT[0][3] = vPos[0]
    matrixT[1][3] = vPos[1]
    matrixT[2][3] = vPos[2]
    matrixT[3][3] = 1

    invMatrixR = np.linalg.inv(matrixR)
    invMatrixT = np.linalg.inv(matrixT)
    #multiplying inverses
    invMatrixRT = np.matmul(invMatrixR, invMatrixT)
    #since the g matrix is 1x4, not 4x1 we must transform this accoridngly
    invMatrixRT = np.rot90(invMatrixRT)
    invMatrixRT = np.flipud(invMatrixRT)
    return invMatrixRT


#From Code-It-Yourself!
def projectionMatrix(app):
    nearPlane = 0.1
    farPlane = 1000
    fov = 90
    aspectRatio = app.height/app.width
    fovRad = 1/math.tan(math.radians(0.5*fov))
    
    rows = cols = 4
    matrix = vf.makeMatrix(rows, cols)
  
    matrix[0][0] = aspectRatio * fovRad
    matrix[1][1] = fovRad
    matrix[2][2] = farPlane / (farPlane - nearPlane)
    matrix[2][3] = 1
    matrix[3][2] = (-farPlane * nearPlane) / (farPlane - nearPlane)
    
    return matrix