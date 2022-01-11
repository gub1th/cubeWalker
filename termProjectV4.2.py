from cmu_112_graphics import *
import math
import numpy as np
import copy
import vectorFunctions as vf
import relevantMatrices as rm
import time
import random
import pygame

'''
PERSONAL NOTES:
-tbd

REFERENCES:
-references are commented above blocks of code
-some of these references were just used to gain better understanding
-adapted means I made alterations (some heavier than others) based on my understandings/knwoeldge

Explicit Use:
'Code-It-Yourself! 3D Graphics Engine' Series(Part 1-3) - https://www.youtube.com/watch?v=ih20l3pJoeU&t=868s <- (primary)
https://www.youtube.com/watch?v=3ZmqJb7J5wE&list=PLW3Zl3wyJwWOpdhYedlD-yCB7WQoHf-My&index=39
https://www.youtube.com/watch?v=UuNPHOJ_V5o&t=283s
https://en.wikipedia.org/wiki/Rotation_matrix
https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#playingSounds
https://www.cs.cmu.edu/~112/notes/notes-graphics.html

Implicit(for understanding):
Some videos from 'Math for Game Developers' Series - https://www.youtube.com/watch?v=dul0mui292Q&t=22s
Some videos from '3D Programming Fundamentals' Series - https://www.youtube.com/watch?v=8bQ5u14Z9OQ&t=1462s
'How 3d rendering works' - https://www.youtube.com/watch?v=VywuRtNKl0c
'The Camera Transform' - https://www.youtube.com/watch?v=mpTl003EXCY
https://math.stackexchange.com/questions/2305792/3d-projection-on-a-2d-plane-weak-maths-ressources/2306853

Music:
Chiptronical - https://patrickdearteaga.com/royalty-free-music/chiptronical/

'''

class model3D(object):
    def __init__(self, triList, color, double):
        self.triList = triList
        self.typesList = []
        self.triListTrans = []
        self.color = color
        self.rot = [0, 0, 0]
        self.pos = [0, 0, 0]
        self.stipple = ""
        self.cosTheta = 0
        self.double = double

class camera(object):
    def __init__(self, pos, rot):
        self.pos = pos
        self.rot = rot

#from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#playingSounds
class Sound(object):
    def __init__(self, path):
        self.path = path
        self.loops = 1
        pygame.mixer.music.load(path)

    def isPlaying(self):
        return bool(pygame.mixer.music.get_busy())

    def startMusic(self, loops = 1):
        self.loops = loops
        pygame.mixer.music.play(loops=loops)

    def stopMusic(self):
        pygame.mixer.music.stop()

    def setVolume(self, vol):
        pygame.mixer.music.set_volume(vol)    
    

#adapted from Code-It-Yourself!
def strictly3D(app, model):
    #function to take care of all transformations in 3d-space
    newTriangles = []
    for triangle in model.triList:
        if len(triangle[0]) == 3:
            translation = model.pos
        else:
            translation = [model.pos[0], model.pos[1], model.pos[2], 0]     

        #translation!    
        vertice0 = np.add(np.array(triangle[0]), translation)
        vertice1 = np.add(np.array(triangle[1]), translation)
        vertice2 = np.add(np.array(triangle[2]), translation)

        #add 1 more variable since will multiply with 4x4 matrix
        newVertice0 = (vertice0[0], vertice0[1], vertice0[2], 1)
        newVertice1 = (vertice1[0], vertice1[1], vertice1[2], 1)
        newVertice2 = (vertice2[0], vertice2[1], vertice2[2], 1)


        trans1 = rm.translationMatrix(-model.pos[0], -model.pos[1], -model.pos[2])
        trans2 = rm.translationMatrix(model.pos[0], model.pos[1], model.pos[2])
        simpleRotX = rm.rotationXMatrix(model.rot[0])
        simpleRotY = rm.rotationYMatrix(model.rot[1])
        simpleRotZ = rm.rotationZMatrix(model.rot[2])

    
        #rotation!
        rotX = np.matmul(np.matmul(trans1, simpleRotX), trans2)
        rotY = np.matmul(np.matmul(trans1, simpleRotY), trans2)
        rotZ = np.matmul(np.matmul(trans1, simpleRotZ), trans2)

        newVertice0 = vf.multiplyMatrix(newVertice0, rotX)
        newVertice0 = vf.multiplyMatrix(newVertice0, rotY)
        newVertice0 = vf.multiplyMatrix(newVertice0, rotZ)
        newVertice1 = vf.multiplyMatrix(newVertice1, rotX)
        newVertice1 = vf.multiplyMatrix(newVertice1, rotY)
        newVertice1 = vf.multiplyMatrix(newVertice1, rotZ)

        newVertice2 = vf.multiplyMatrix(newVertice2, rotX)
        newVertice2 = vf.multiplyMatrix(newVertice2, rotY)
        newVertice2 = vf.multiplyMatrix(newVertice2, rotZ)

        #to remove 4th variable
        newTriangles.append((newVertice0, newVertice1, newVertice2))

    return newTriangles    

#adapted from Code-It-Yourself!
def translate3Dto2D(app, canvas, model):
    i = 0

    for triangle in model.triListTrans:
        i+=1
        vertice0 = triangle[0]
        vertice1 = triangle[1]
        vertice2 = triangle[2]

        #add 1 more variable since will multiply with 4x4 matrix
        newVertice0 = (vertice0[0], vertice0[1], vertice0[2], 1)
        newVertice1 = (vertice1[0], vertice1[1], vertice1[2], 1)
        newVertice2 = (vertice2[0], vertice2[1], vertice2[2], 1)

        #getting normal utilizing the three vertices
        normal = vf.normalVector(newVertice0, newVertice1, newVertice2)
        normal = vf.normalizeMatrix(normal)

        #from 3d graphics mini-lecture
        #finding angle between normal and light ray (for flat shading)
        lenNormal = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
        lenLight = math.sqrt(app.lightPos[0]**2 + app.lightPos[1]**2 + app.lightPos[2]**2)
        cosTheta = abs(normal.dot(app.lightPos))/(lenNormal*lenLight)
        #just multiply rgb values by costheta!

        #camera either follows player from behind or is on the side of player
        if app.camFollow:
            pos, lookat = idealCamParams(app)
        else:
            trans1 = rm.translationMatrix(-app.cam.pos[0], -app.cam.pos[1], -app.cam.pos[2])
            trans2 = rm.translationMatrix(app.cam.pos[0], app.cam.pos[1], app.cam.pos[2])
            simpleRotY = rm.rotationYMatrix(app.cam.rot)
            rotY = np.matmul(np.matmul(trans1, simpleRotY), trans2)

            pos = app.cam.pos

            #turning vecDir(the lookDir)
            lookDir = vf.multiplyMatrix(app.vecDir, rotY)
            xL, yL, zL = lookDir[0], lookDir[1], lookDir[2]
            newRotate = (xL, yL, zL)
            lookat = np.add(app.cam.pos, newRotate)

        camToTriangle = newVertice0[0]-pos[0], newVertice0[1]-pos[1], newVertice0[2]-pos[2]
        #can only 'see' faces if the dot product of these vectors are less than zero     
        if np.dot(normal, camToTriangle) < 0 or model.double == 'double':
        
            #convert from worldspace into viewspace
            viewM = rm.viewMatrix(app, pos, lookat, [0, 1, 0])
            newVertice0 = vf.multiplyMatrix(newVertice0, viewM)
            newVertice1 = vf.multiplyMatrix(newVertice1, viewM)
            newVertice2 = vf.multiplyMatrix(newVertice2, viewM)
            
            #clipping the triangles
            newTriangle = (newVertice0, newVertice1, newVertice2)
            #put a 4th variable (1)
            planePoint = (0, 0, 0.1, 1)
            #upwards
            planeNormal = (0, 0, 1, 1)

            clippedTriangles = trianglesClipped(planePoint, planeNormal, newTriangle)
 
            if clippedTriangles != None:
                for triangle in clippedTriangles:
                    newVertice0 = triangle[0]
                    newVertice1 = triangle[1]
                    newVertice2 = triangle[2]

                    #projecting from 3d to 2d
                    newVertice0 = vf.multiplyMatrix(newVertice0, app.projMatrix)
                    newVertice1 = vf.multiplyMatrix(newVertice1, app.projMatrix)
                    newVertice2 = vf.multiplyMatrix(newVertice2, app.projMatrix)

                    #to 'normalize', so that the 'w' is equal to 1
                    if newVertice0[3]!= 0:
                        newVertice0[0]/= newVertice0[3]
                        newVertice0[1]/= newVertice0[3]
                        newVertice0[2]/= newVertice0[3]

                    if newVertice1[3]!= 0:
                        newVertice1[0]/= newVertice1[3]
                        newVertice1[1]/= newVertice1[3]
                        newVertice1[2]/= newVertice1[3]
                            
                    if newVertice2[3]!= 0:
                        newVertice2[0]/= newVertice2[3]
                        newVertice2[1]/= newVertice2[3]
                        newVertice2[2]/= newVertice2[3]

                    #so that origin is on screen center
                    newVertice0 = screenTransform(app, newVertice0)
                    x = newVertice0[0]
                    y = newVertice0[1]
                    z = newVertice0[2]
                    newVertice0 = (x, y, z)

                    newVertice1 = screenTransform(app, newVertice1)
                    x = newVertice1[0]
                    y = newVertice1[1]
                    z = newVertice1[2]
                    newVertice1 = (x, y, z)

                    newVertice2 = screenTransform(app, newVertice2)
                    x = newVertice2[0]
                    y = newVertice2[1]
                    z = newVertice2[2]

                    color = rgbStringLighting(model.color, cosTheta)

                    canvas.create_polygon(newVertice0[0], newVertice0[1], newVertice1[0], newVertice1[1], newVertice2[0], newVertice2[1], fill = color, stipple = model.stipple)
                    
                    #adding lines for objects
                    #canvas.create_line(newVertice0[0], newVertice0[1], newVertice1[0], newVertice1[1], width = 3, fill = 'white')
                    #canvas.create_line(newVertice1[0], newVertice1[1], newVertice2[0], newVertice2[1], width = 3, fill = 'white')
                    #canvas.create_line(newVertice2[0], newVertice2[1], newVertice0[0], newVertice0[1], width = 3, fill = 'white')

def createModels(app):
    app.modelList.append(makeFloor(app))
    app.modelList.append(makeBuilds())
    app.modelList.append(makeCube("player", 0.5, [0, 0, 0], [0, 0, 255]))
    app.modelList.append(makeCube("bullet", 0.2, [0, 9, 0], [18, 56, 200]))
    app.modelList.append(makeCube("target", 0.5, [0, 9, 0], [10, 210, 80]))
    app.modelList.append(makeCube("enemy", 0.5, [0, 9, 0], [255, 192, 203]))
    app.modelList.append(makeCube("bullet2", 0.2, [0, 9, 0], [0, 255, 255]))

def insertPanelsIntoBuilds(app, type):
    #inserting panel vertices into build list
    row, col = app.currCell
    x0, z0, x1, z1 = getCellBounds(app, row, col)
    #right corner is start(x0, z0)
    #no change if N, need rotation otherwise
    dirs = 0
    if app.currDir == 'E':
        dirs = 1      
    elif app.currDir == 'S':
        dirs = 2
    elif app.currDir == 'W':
        dirs = 3

    #adding a ramp panel    
    if type == 'r':
        panel = makeRampPanel(x0, z0, app.cellWidth, dirs)
        
    for triangle in panel.triList:
        app.builds.triList.append(triangle)


def makeRampPanel(startX, startZ, width, dirz):
    #0, 1, 2, 3 = N, E, S, W
    #rotation depending on direction it faces
    rotY = rm.rotationYMatrix(math.radians(90) * dirz)

    triList = [
    [(startX, 0, startZ), (startX + width, width, startZ - width), (startX + width, 0, startZ)],
    [(startX, 0, startZ), (startX, width, startZ - width), (startX + width, width, startZ - width)]]

    triListNew = []

    for triangle in triList:
        vertice0 = triangle[0]
        vertice1 = triangle[1]
        vertice2 = triangle[2]

        newVertice0 = (vertice0[0], vertice0[1], vertice0[2], 1)
        newVertice1 = (vertice1[0], vertice1[1], vertice1[2], 1)
        newVertice2 = (vertice2[0], vertice2[1], vertice2[2], 1)

        newVertice0 = vf.multiplyMatrix(newVertice0, rotY)
        newVertice1 = vf.multiplyMatrix(newVertice1, rotY)
        newVertice2 = vf.multiplyMatrix(newVertice2, rotY)

        triListNew.append((newVertice0, newVertice1, newVertice2))

    rampPanel = model3D(triListNew, [33, 42, 1], "double")

    return rampPanel

def makeFloor(app):
    floorList = []

    #starting position
    startX = startZ = app.floorStartPos
    typesList = []
    for row in range(app.rows): #z
        typesList.append(('flatTile', 'flatTile'))
        for col in range(app.cols): #x

            v1 = startX + (col + 1) * app.cellWidth, 0.0, startZ - row * app.cellWidth
            v2 = startX + col * app.cellWidth, 0.0, startZ - (row + 1) * app.cellWidth
            v3 = startX + col * app.cellWidth, 0.0, startZ - row * app.cellWidth
            triangle1 = (v1, v2, v3)

            v4 = startX + (col + 1) * app.cellWidth, 0.0, startZ - row * app.cellWidth
            v5 = startX + (col + 1) * app.cellWidth, 0.0, startZ - (row + 1) * app.cellWidth
            v6 = startX + col * app.cellWidth, 0.0, startZ - (row + 1) * app.cellWidth
            triangle2 = (v4, v5, v6)

            floorList.append(triangle1)
            floorList.append(triangle2)
    floor = model3D(floorList, [255, 0, 0], "single")
    floor.typesList = typesList
    return floor

def removeNBuild(app):
    model = app.floor
    #removing back-most tiles
    del model.triList[0:4]
    del model.typesList[0]

    zCell = app.currCell[0] + (- 1)

    startX = app.floorStartPos
    app.startZ = app.cellWidth * zCell

    tempList = []

    #making new tiles in front
    for row in range(1): #z
        for col in range(2): #x

            flatTile = [((startX + (col + 1) * app.cellWidth, 0.0, app.startZ - row * app.cellWidth), 
                (startX + col * app.cellWidth, 0.0, app.startZ - (row + 1) * app.cellWidth),
                (startX + col * app.cellWidth, 0.0, app.startZ - row * app.cellWidth)),
                ((startX + (col + 1) * app.cellWidth, 0.0, app.startZ - row * app.cellWidth),
                (startX + (col + 1) * app.cellWidth, 0.0, app.startZ - (row + 1) * app.cellWidth),
                (startX + col * app.cellWidth, 0.0, app.startZ - (row + 1) * app.cellWidth))]

            noTile = [((startX + (col + 1) * 0.01, 0.0, app.startZ - row * 0.01), 
                (startX + col * 0.01, 0.0, app.startZ - (row + 1) * 0.01),
                (startX + col * 0.01, 0.0, app.startZ - row * 0.01)),
                ((startX + (col + 1) * 0.01, 0.0, app.startZ - row * 0.01),
                (startX + (col + 1) * 0.01, 0.0, app.startZ - (row + 1) * 0.01),
                (startX + col * 0.01, 0.0, app.startZ - (row + 1) * 0.01))]    
            
            #cannot of 2 noTiles in a row
            if model.typesList[1][col] == 'noTile':
                types = flatTile
            else:
                types = random.choice([flatTile, noTile])

            if types == flatTile:
                tempList.append('flatTile')
            elif types == noTile:
                tempList.append('noTile')

            v1 = types[0][0]
            v2 = types[0][1]
            v3 = types[0][2]

            triangle1 = (v1, v2, v3)

            v4 = types[1][0]
            v5 = types[1][1]
            v6 = types[1][2]

            triangle2 = (v4, v5, v6)

            model.triList.append(triangle1)
            model.triList.append(triangle2)

    model.typesList.append((tempList[0], tempList[1]))        

    index = app.currCell[1]
    index = int(index)

    #initiating target mode
    if random.random() <= app.targetProb:
        if (app.floor.typesList[0][index] == "noTile") and (len(app.builds.triListTrans)) == 0:
            app.gameOver = True
        app.targetMode = True    
        x = random.uniform(0, 2 * app.cellWidth)
        y = 1
        z = app.startZ
        app.target.pos = [x, y, z]
        app.moving = False
        app.timeToShoot = time.time()
    
    #initiating duel mode
    if random.random() <= app.duelProb:
        if (app.floor.typesList[0][index] == "noTile") and (len(app.builds.triListTrans)) == 0:
            app.gameOver = True
        if not app.targetMode:    
            x = random.uniform(0, 2 * app.cellWidth)
            y = 0
            z = app.startZ
            app.enemy.pos = [x, y, z]
            app.moving = False
            app.duelMode = True

def aiMovement(app):
    #random angle
    angle = random.uniform(0, math.radians(360))
    x = 0.5 * math.sin(angle) * random.randint(-1, 1)
    z = 0.5 * math.cos(angle) * random.randint(-1, 1)

    #random movement time (in 1 particular direction)
    time = random.randint(3, 6)

    order = random.randint(0, 1)
    if order == 0:
        app.d1 = x
        app.d2 = z
        
    else:
        app.d1 = z
        app.d2 = x
  
    app.moveTime = time


def makeCube(name, size, pos, color):
    #base for most models
    triangles = [
                #south
                [(-size, 0, -size), (-size, 2*size, -size), (size, 2*size, -size)],
                [(-size, 0, -size), (size, 2*size, -size), (size, 0, -size)],
                #east
                [(size, 0, -size), (size, 2*size, -size), (size, 2*size, size)],
                [(size, 0, -size), (size, 2*size, size), (size, 0, size)],
                #north
                [(size, 0, size), (size, 2*size, size), (-size, 2*size, size)],
                [(size, 0, size), (-size, 2*size, size), (-size, 0, size)],
                #west
                [(-size, 0, size), (-size, 2*size, size), (-size, 2*size, -size)],
                [(-size, 0, size), (-size, 2*size, -size), (-size, 0, -size)],
                #top
                [(-size, 2*size, -size), (-size, 2*size, size), (size, 2*size, size)],
                [(-size, 2*size, -size), (size, 2*size, size), (size, 2*size, -size)],
                #bottom
                [(size, 0, -size), (-size, 0, size), (-size, 0, -size)],
                [(size, 0, -size), (size, 0, size), (-size, 0, size)]
                ]

    #note: single if '3d', double if '2d' as the appearance of the face depends on the normal
    name = model3D(triangles, color, "single")
    name.pos = pos            
    return name          

def makeBuilds():
    builds = model3D([], [0, 255, 0], "double")
    builds.stipple = 'gray50'
    return builds

def detectCollision(pos1, pos2, side1, side2):
    #the pos are center pos
    #side are lengths of sides
    #added side because due to the nature of how my models were initially made
    #thus, this function is specific
    newPos1 = (pos1[0], pos1[1] + side1/2, pos1[2])
    newPos2 = (pos2[0], pos2[1] + side2/2, pos2[2])
    faceDiag1 = math.sqrt(2 * side1**2)
    internalDiag1 = math.sqrt(side1**2  + faceDiag1**2)

    faceDiag2 = math.sqrt(2 * side2**2)
    internalDiag2 = math.sqrt(side2**2 + faceDiag2**2)

    distCenters = vf.distance(newPos1, newPos2)

    if distCenters < (internalDiag1/2 + internalDiag2/2):
        return True
    return False

def projectile(app, model, angle, startingPos, bulletModel, timePassed):
    #based on suvat equations
    anglez = model.rot[1] + math.radians(270)
    u = (app.speed * math.cos(angle) * math.cos(anglez), app.speed * math.sin(angle), app.speed * math.cos(angle) * math.sin(anglez))
    v = np.add(u, vf.multiplyVector(app.accel, timePassed))
    move = np.add(vf.multiplyVector(u, timePassed), vf.multiplyVector(app.accel, 0.5 * timePassed**2))
    newPos = np.add(startingPos, move)
    bulletModel.pos = newPos 

def rotateAndCalcLaunchAngle(app):
    #calculating optimal rotation and projection angle for AI
    playerPos = app.player.pos
    enemyPos = app.enemy.pos

    #rotation based on position of player and enemy
    z = playerPos[2] - enemyPos[2]
    x = playerPos[0] - enemyPos[0]

    angleToRotate = math.atan2(z, x) - math.radians(90)
    rotation = angleToRotate + math.radians(180)
    app.enemy.rot[1] += rotation

    #based on suvat
    dist = vf.distance(enemyPos, playerPos)
    temp = (dist * app.accel[1])/app.speed**2

    if temp < -1:
        temp = -1

    launchAngle = -temp/2

    return (launchAngle, rotation)

def notInBounds(app):
    index = int(app.currCell[1])
    return(app.player.pos[0] < 0 or app.player.pos[0] > (app.cols * app.cellWidth) or ((app.floor.typesList[0][index] == "noTile") and (len(app.builds.triListTrans)) == 0))   

def initializePos(model):
    model.pos = [0, 9, 0]

def timerFired(app):
    #music settings
    app.soundIntro.setVolume(app.volumeLevel)
    if app.gameOver:
        if app.soundIntro.isPlaying():
            app.soundIntro.stopMusic()
        return
    if app.startGame == False:
        return  

    #points always increasing
    app.points += 1

    #cam always follows player
    app.cam.pos[2] = app.player.pos[2]

    #end if step on illegal bounds
    if notInBounds(app):
        app.gameOver = True
    
    #to rotate player to face forward after player shoots
    if app.rotateRight:
        app.player.rot[1] += math.radians(4)
        if app.player.rot[1] >= 0:
            app.rotateRight = False
            app.player.rot[1] = 0

    if app.rotateLeft:
        app.player.rot[1] -= math.radians(4)
        if app.player.rot[1] <= 0:
            app.rotateLeft = False
            app.player.rot[1] = 0
       
    #the continuous forward movement   
    if app.moving:
        x = app.move * math.sin(app.player.rot[1])
        y = app.move * math.cos(app.player.rot[1])
        app.player.pos[0] -= x
        app.player.pos[2] -= y
        app.player.triListTrans = strictly3D(app, app.player)
    
    if not app.moving:
        app.target.rot[1] += app.move

    #check whether player is lower than plane and adjust if necessary
    if len(app.modelList[2].triListTrans) != 0:
        checkAndAdjust(app)
    
    #falling movement from ramp
    if app.fall:
        app.player.pos[1] -= 0.3
        if app.player.pos[1]<= 0:
            app.player.pos[1] = 0
            app.fall = False

    currTime = time.time()

    #targetmode
    if app.targetMode:
        app.counter = currTime - app.timeToShoot
        if app.counter >= 6:
            app.gameOver = True
        if app.bulletFired:
            app.bullet.triListTrans = strictly3D(app, app.bullet)
            app.timing += 0.05
            projectile(app, app.player, app.userAngle, app.bulletStartPos, app.bullet, app.timing)

            result = detectCollision(app.bullet.pos, app.target.pos, 0.4, 1)

            if app.bullet.pos[1]<= 0 or result == True:
                if result == True:
                    app.counter = 0
                    app.points += 50
                    app.targetMode = False
                    app.moving = True
                    initializePos(app.bullet)
                    initializePos(app.target)
                app.bulletFired = False
                app.timing = 0
                if app.player.rot[1]>0:
                    app.rotateLeft = True
                else:
                    app.rotateRight = True    
        
    #duelmode
    if app.duelMode:
        #player-related
        if app.bulletFired:
            app.bullet.triListTrans = strictly3D(app, app.bullet)
            app.timing += 0.05
            projectile(app, app.player, app.userAngle, app.bulletStartPos, app.bullet, app.timing)

            result = detectCollision(app.bullet.pos, app.enemy.pos, 0.4, 1)

            if app.bullet.pos[1]<= 0 or result == True:
                if result == True:
                    initializePos(app.bullet)
                    initializePos(app.enemy)
                    initializePos(app.bullet2)
                    app.points += 50
                    app.duelMode = False
                    app.moving = True
                app.bulletFired = False
                app.timing = 0
                if app.player.rot[1]>0:
                    app.rotateLeft = True
                else:
                    app.rotateRight = True    

        #AI-related
        #movement part
        if app.needUpdate:
            aiMovement(app)
            app.needUpdate = False
        else:
            if app.bullet2Fired == False:
                app.launchAngle, app.rotationAngle = rotateAndCalcLaunchAngle(app)
                app.bullet2StartPos = app.enemy.pos.copy()
                app.bullet2Fired = True
                app.bullet2Start = time.time()

            app.enemy.pos[0] += app.d1
            app.enemy.pos[2] += app.d2

            if app.enemy.pos[0]<0 or app.enemy.pos[0]>2* app.cellWidth:
                app.enemy.pos[0] -= 1.5* app.d1
            elif app.enemy.pos[2] > app.startZ + 2*app.cellWidth or app.enemy.pos[2] < app.startZ - 0.5 * app.cellWidth:    
                app.enemy.pos[2] -= 1.5 * app.d2

            app.tempTime += 0.5
            if app.tempTime >= app.moveTime:
                app.needUpdate = True   
            #shooting part
            if app.bullet2Fired:
                app.bullet2.triListTrans = strictly3D(app, app.bullet2)
                app.timing1 += 0.05
                projectile(app, app.enemy, app.launchAngle, app.bullet2StartPos, app.bullet2, app.timing1)

                result = detectCollision(app.bullet2.pos, app.player.pos, 0.4, 1)

                if app.bullet2.pos[1]<= 0 or result == True:
                    if result == True:
                        app.gameOver = True
                    app.bullet2Fired = False
                    app.enemy.rot[1] -= app.rotationAngle
                    app.timing1 = 0 


    app.currCell = getCell(app, app.player.pos[0], app.player.pos[2]) 
    if app.tempCell[0] != app.currCell[0]:
        if app.tempCell == (0.0, 0.0):
            app.tempCell = app.currCell
        else:
            removeNBuild(app)
            app.tempCell = app.currCell

    for model in app.modelList:
        model.triListTrans = strictly3D(app, model)


def appStarted(app):
    pygame.mixer.init()
    app.soundIntro = Sound("audio\\Chiptronical.ogg")
    app.soundIntro.startMusic(-1)
    app.volumeLevel = 0.5
    app.soundIntro.setVolume(app.volumeLevel)

    app.startGame = False
    app.instructionScreen = False
    app.mainMenu = True
    app.leaderBoardScreen = False
    app.enterNameScreen = False

    restartApp(app)

def restartApp(app):
    app.timerDelay = 1

    app.name = ""
    app.textFile = 'leaderboard.txt'
    app.topPlayers = []    

    app.points = 0
    app.counter = 0

    app.targetProb = 0.25
    app.duelProb = 0.25
    app.timeToShoot = 0
    
    app.gameOver = False
    app.needUpdate = False
    app.targetMode = False
    app.duelMode = False

    #AI-movement
    app.tempTime = 0
    app.moveTime = 0
    app.d1 = 0
    app.d2 = 0

    app.cellWidth = 4
    app.rows = 3
    app.cols = 2
    app.floorStartPos = 0
    
    app.modelList = []
    createModels(app)
    app.floor = app.modelList[0]
    app.builds = app.modelList[1]
    app.player = app.modelList[2]
    app.player.pos[0] = app.cellWidth/2
    app.bullet = app.modelList[3]
    app.target = app.modelList[4]
    app.enemy = app.modelList[5]
    app.bullet2 = app.modelList[6]
    app.bulletStartPos = []
    app.bullet2StartPos = []

    #projectile-related
    app.bulletFired = False
    app.bulletStart = 0
    app.bullet2Fired = False
    app.bullet2Start = 0

    app.timing = 0
    app.timing1 = 0
    app.accel = (0, -9.8, 0)
    app.launchAngle = 0
    app.rotationAngle = 0
    app.speed = 10.5

    app.userAngle = math.radians(45)
    app.userMove = 0.3
    app.move = 0.1
    app.rotateLeft = False
    app.rotateRight = False

    app.fall = False
    app.moving = True

    #cam/view related
    app.cam = camera([-5, 1, app.player.pos[0]], 0)
    app.camFollow = True
    app.vecDir = [app.cellWidth, 1, app.player.pos[2] - 2, 1]
    app.lightPos = [-3, 8, app.player.pos[2] + 1]

    app.projMatrix = rm.projectionMatrix(app)
    
    app.currDir = getDir(app)
    app.currCell = getCell(app, app.player.pos[0], app.player.pos[2])
    app.tempCell = app.currCell

def insertName(app):
    #insert name for leaderboard input
    with open(app.textFile, 'a') as wf:
        wf.write(f'{app.name}#{app.points}\n')
    
def findTopPlayers(app):
    #find top 5 scores and players
    with open(app.textFile, 'r') as rf:
        lines = rf.readlines()

    nameList = []
    scoreList = []
    if len(lines)>0:    
        for line in lines:
            name = line.split('#', 1)[0]
            score = line.split('#', 1)[1]
            nameList.append(name)
            scoreList.append(score)       
    zipped = reversed(sorted(zip(scoreList, nameList)))
    app.topPlayers = list(zipped)[:5]


def getDir(app):
    #get direction that cube faces
    dirs = ["N", "E", "S", "W"]
    return dirs[int((app.player.rot[1] + (math.pi/4))%(2*math.pi) //(math.pi/2))]    

def getCell(app, x, z):
    col = (x - app.floorStartPos)//app.cellWidth
    row = (z - app.floorStartPos)//app.cellWidth

    return (row, col)

def getCellBounds(app, row, col):
    x0 = app.floorStartPos + col * app.cellWidth
    x1 = x0 + app.cellWidth

    z0 = app.floorStartPos + row * app.cellWidth
    z1 = z0 + app.cellWidth

    return(x0, z0, x1, z1)

#adapted from https://www.youtube.com/watch?v=UuNPHOJ_V5o&t=283s
def idealCamParams(app):
    model = app.player
    rotY = rm.rotationYMatrix(model.rot[1])

    idealOffset = [0, 2, 3, 1]
    idealOffset = vf.multiplyMatrix(idealOffset, rotY)
    idealOffset = idealOffset[:-1]
    idealOffset = np.add(idealOffset, model.pos)

    idealLookat = [0, 0, -1, 1]
    idealLookat = vf.multiplyMatrix(idealLookat, rotY)
    idealLookat = idealLookat[:-1]
    idealLookat = np.add(idealLookat, model.pos)

    return idealOffset, idealLookat



#from DoItYourself!
def trianglesClipped(planePoint, normal, triangle):
    #no of triangles clipped against the plane
    normal = vf.normalizeMatrix(normal) 

    insidePoints = []
    outsidePoints = []

    d0 = vf.distPointToPlane(planePoint, normal, triangle[0])
    d1 = vf.distPointToPlane(planePoint, normal, triangle[1])
    d2 = vf.distPointToPlane(planePoint, normal, triangle[2])

    pairs = [(d0, triangle[0]), (d1, triangle[1]), (d2, triangle[2])]

    for d, t in pairs:
        #should append the triangle if distance >= 0
        if d >= 0:
            insidePoints.append(t)
        else:
            outsidePoints.append(t)
    insideCount = len(insidePoints)

    newP = [None, None, None]
    newPA = [None, None, None]
    newPB = [None, None, None]

    #all points outside of plane
    if insideCount == 0: 
        noOfTris = 0

    elif insideCount == 1:
        newP[0] = insidePoints[0]
        newP[1] = vf.planeLineIntersection(planePoint, normal, insidePoints[0], outsidePoints[0])
        newP[2] = vf.planeLineIntersection(planePoint, normal, insidePoints[0], outsidePoints[1])
        noOfTris = 1

    elif insideCount == 2:
        #triangle 1
        newPA[0] = insidePoints[0]
        newPA[1] = insidePoints[1]
        newPA[2] = vf.planeLineIntersection(planePoint, normal, insidePoints[0], outsidePoints[0])
        
        #triangle 2
        newPB[0] = insidePoints[1]
        newPB[1] = newPA[2]
        newPB[2] = vf.planeLineIntersection(planePoint, normal, insidePoints[1], outsidePoints[0])
        noOfTris = 2

    #insideCount == 3     
    else: 
        #output triangle = input triangle
        newP[0] = insidePoints[0]
        newP[1] = insidePoints[1]
        newP[2] = insidePoints[2]
        noOfTris = 1        
    
    if noOfTris == 0:
        return None
    elif noOfTris == 1:
        return ([[newP[0], newP[1], newP[2]]])
    else:
        return ([(newPA[0], newPA[1], newPA[2]), (newPB[0], newPB[1], newPB[2])])


def screenTransform(app, vector):
    #from ndc space to screen space
    if vector[2] == 0:
        z = 1
    else:
        z = vector[2]    

    vector[0] = (vector[0]/z + 1) * app.width/2
    vector[1] = (-vector[1]/z + 1) * app.height/2

    return vector

#adapted from https://www.cs.cmu.edu/~112/notes/notes-graphics.html
def rgbStringLighting(color, cosTheta):
    r = color[0]
    g = color[1]
    b = color[2]
    return f'#{int(r*cosTheta):02x}{int(g*cosTheta):02x}{int(b*cosTheta):02x}'

def mousePressed(app, event):
    x, y = event.x, event.y
    #main menu
    if app.mainMenu:
        #start
        if app.width*0.4<x and x<app.width*0.62 and app.height*0.47<y and y<app.height*0.54:
            app.startGame = True
            app.mainMenu = False

        #instructions
        if app.width*0.33<x and x<app.width*0.68 and app.height*0.74<y and y<app.height*0.79:
            app.instructionScreen = True

        #leaderboard
        if app.width*0.33<x and x<app.width*0.69 and app.height*0.625<y and y<app.height*0.67:
            findTopPlayers(app)
            app.leaderBoardScreen = True

    #back
    if app.leaderBoardScreen:    
        if app.width*0.797<x and x<app.width*0.936 and app.height*0.877<y and y<app.height*0.929:
            app.leaderBoardScreen = False
            app.mainMenu = True

    #back
    if app.instructionScreen:
        if app.width*0.81<x and x<app.width*0.95 and app.height*0.89<y and y<app.height*0.93: 
            app.instructionScreen = False
            app.mainMenu = True     


def keyPressed(app, event):
    #if on enter name screen, don't do any other functions
    if app.enterNameScreen:
        if event.key == 'Backspace':
            if app.name != 0:
                app.name = app.name[:-1]
        if event.key.isalpha() and len(event.key) == 1:
            app.name += event.key.upper()
        if event.key == 'Enter':
            insertName(app)
            appStarted(app)    
        return

    #adjusting volume
    if event.key == 'a':
        app.volumeLevel -= 0.05
        if app.volumeLevel < 0:
            app.volumeLevel = 0

    elif event.key == 's':
        app.volumeLevel += 0.05  
        if app.volumeLevel > 1:
            app.volumeLevel = 1    

    #restart
    if event.key == 'e':
        restartApp(app)
        app.startGame = True

    #main menu
    if event.key == 'w':
        appStarted(app)

    #enter name for leaderboard
    if event.key == 'q':
        if app.gameOver:
            if not app.enterNameScreen:
                app.enterNameScreen = True           

    if app.gameOver:
        return
    if app.startGame == False:
        return

    app.currDir = getDir(app)

    #for debugging
    if event.key == 'v':
        print(app.player.pos)
        print(app.floor.typesList)
    elif event.key == 'b':
        print(app.currCell)
    #targetMode    
    elif event.key == '1':
        if app.targetProb == 0.99:
            app.targetProb = 0.25
        else:    
            app.targetProb = 0.99
    #duelMode        
    elif event.key == '2':
        if app.duelProb == 0.99:
            app.duelProb = 0.25
        else:    
            app.duelProb = 0.99    

    #change camera perspective
    if event.key == 't':
        if app.camFollow:
            app.camFollow = False
        else:
            app.camFollow = True  

    x = app.userMove * math.sin(app.player.rot[1])
    z = app.userMove * math.cos(app.player.rot[1])

    #player movement
    if event.key == 'j': 
        app.player.pos[0] += z
        app.player.pos[2] -= x

    elif event.key == 'l':
        app.player.pos[0] -= z
        app.player.pos[2] += x

    #making ramps
    elif event.key == 'r':
        insertPanelsIntoBuilds(app, "r")

    #additional player movement
    if app.targetMode or app.duelMode:
        if event.key == 'k':
            app.player.pos[0] += x
            app.player.pos[2] += z

        elif event.key == 'i':
            app.player.pos[0] -= x
            app.player.pos[2] -= z

        #player rotation
        elif event.key == 'y':
            if not app.bulletFired:
                app.player.rot[1] += app.userMove

        elif event.key == 'u':
            if not app.bulletFired:
                app.player.rot[1] -= app.userMove

        #projectile angle
        elif event.key == 'g':
            app.userAngle -= math.radians(5)
            if app.userAngle < 0:
                app.userAngle = 0

        elif event.key == 'h':
            app.userAngle += math.radians(5)    
            if app.userAngle > math.radians(90):
                app.userAngle = math.radians(90)

        #fire
        elif event.key == 'f':
            if not app.bulletFired:
                app.bulletStartPos = app.player.pos.copy()
                app.bulletFired = True
                app.bulletStart = time.time()
    
    for model in app.modelList:
        model.triListTrans = strictly3D(app, model)
   
    app.currCell = getCell(app, app.player.pos[0], app.player.pos[2])   


def pointRelativeToPlane(app, normal, p, v):
    #check position of point relative to plane
    #p is normal point, v is random point
    x = np.subtract(v, p)
    d = np.subtract(np.dot(normal, v), np.dot(normal, x))

    if np.dot(normal, v) > d:
        return "below"
    elif np.dot(normal, v) < d:
        return "above"
    else:
        return "on"

def checkAndAdjust(app):
    for triangle in app.builds.triListTrans:

        newVertice0 = triangle[0][:3]
        newVertice1 = triangle[1][:3]
        newVertice2 = triangle[2][:3]
        #getting normal
        normal = vf.normalVector(newVertice0, newVertice1, newVertice2)
        normal = vf.normalizeMatrix(normal)

        #currnt status of point relative to plane
        status = pointRelativeToPlane(app, normal, newVertice0, app.player.pos)
        if status == 'below':
            #increase y position of player until it is above the plane
            while True:
                app.player.rot[0] = math.radians(45)
                app.player.pos[1] += 0.1
                newStatus = pointRelativeToPlane(app, normal, newVertice0, app.player.pos)
                #if higher than max height(the ramp height)
                if app.player.pos[1]>= app.cellWidth:
                    if len(app.builds.triList) != 0:
                        app.builds.triList.pop()
                    app.fall = True
                    app.player.rot[0] = 0
                    break      
                if newStatus != 'below':
                    break  
                
def drawGameOver(app, canvas):
    pilImage = Image.open("images\\gameover3.png")
    pilImage = pilImage.resize((app.width, app.height), Image.ANTIALIAS)
    canvas.image = ImageTk.PhotoImage(pilImage)
    canvas.create_image(app.width/2, app.height/2, image = canvas.image)
    canvas.create_text(app.width*0.514, app.height*0.6, text = f'SCORE: {app.points}', font = "Courier 35 bold italic", fill = 'red')

def drawMainMenu(app, canvas):
    pilImage = Image.open("images\\startscreen2.png")
    pilImage = pilImage.resize((app.width, app.height), Image.ANTIALIAS)
    canvas.image = ImageTk.PhotoImage(pilImage)
    canvas.create_image(app.width/2, app.height/2, image = canvas.image)

def drawInstructions(app, canvas):    
    pilImage = Image.open("images\\instructs3.png")
    pilImage = pilImage.resize((app.width, app.height), Image.ANTIALIAS)
    canvas.image = ImageTk.PhotoImage(pilImage)
    canvas.create_image(app.width/2, app.height/2, image = canvas.image)

def drawEnterName(app, canvas):
    pilImage = Image.open("images\\entername2.png")
    pilImage = pilImage.resize((app.width, app.height), Image.ANTIALIAS)
    canvas.image = ImageTk.PhotoImage(pilImage)
    canvas.create_image(app.width/2, app.height/2, image = canvas.image)
    canvas.create_text(app.width * 0.51, app.height * 0.39, text = app.name, font = "Courier 35 bold italic")

def drawLeaderBoard(app, canvas):
    pilImage = Image.open("images\\leaderboardpage.png")
    pilImage = pilImage.resize((app.width, app.height), Image.ANTIALIAS)
    canvas.image = ImageTk.PhotoImage(pilImage)
    canvas.create_image(app.width/2, app.height/2, image = canvas.image)
    for i in range(len(app.topPlayers)):
        score, name = app.topPlayers[i]
        canvas.create_text(app.width/2, app.height/4 + i*app.height/8, text = f'{i+1}. {score}   {name}', font = "Courier 35 bold", fill = 'black')

def drawScore(app, canvas):
    canvas.create_text(app.width/2, app.height/12, text = f'SCORE: {app.points}', font = "Courier 35 bold italic")

def drawTimer(app, canvas):
    if app.counter>0:
        if app.counter>=4:
            color = 'red'
        else:    
            color = 'green'    
        canvas.create_text(5 * app.width/6, app.height/12, text = f'TIMER: {round(6 - app.counter, 2)}', font = "Courier 20 bold italic", fill = color)

def drawProjAngle(app, canvas):
    if app.targetMode or app.duelMode:
        angle = math.degrees(app.userAngle)
        if angle < 30:
            color = 'turquoise'
        elif angle <60:
            color = 'medium turquoise'
        else:
            color = 'dark turquoise'   
        canvas.create_text(5 * app.width/6, app.height/4, text = f'ANGLE: {round(angle)}', font = "Courier 20 bold italic", fill = color)



def redrawAll(app, canvas):
    if app.mainMenu:
        drawMainMenu(app, canvas)    
    if app.instructionScreen:
        drawInstructions(app, canvas)
    if app.leaderBoardScreen:
        drawLeaderBoard(app, canvas)    
    if app.startGame:
        drawScore(app, canvas)    
        for model in app.modelList:
            translate3Dto2D(app, canvas, model)
        drawTimer(app, canvas)
        drawProjAngle(app, canvas)
    if app.gameOver:
        drawGameOver(app, canvas)
    if app.enterNameScreen:
        drawEnterName(app, canvas)
    

def main():
    runApp(width=1000, height=1000)

if __name__ == '__main__':
    main()