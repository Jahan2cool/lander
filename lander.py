import numpy as np
import pygame
import math
pygame.init()
clock = pygame.time.Clock()
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Lunar Lander')
run = True
FPS = 30
font = pygame.font.Font(None,50)
smallfont = pygame.font.Font(None,35)

black = (0,0,0)
Mooncolor = (148,148,148)
red = (255,0,0)
yellow = (255,120,0)
orange = (255,80,0)
bottomColor = (255,255,255)
topcolor = (74,74,74)
split, crash, wreset = False, False, False

emptyVectors = np.array([(0.0,0.0),(0.0,0.0),(0.0,0.0),(0.0,0.0),(0.0,0.0),(0.0,0.0),(0.0,0.0),(0.0,0.0)])
movementScale = 0.6
thrustvalue = 3/4
G = 1.62/4
num = int(1)


phase = 'p2'

class rocketclass():
    def __init__(self,vertices,vectors,color, mass,maxthrust,fuel, radius = 20, angle=-math.pi/2, angleVect = 0):
        self.vertices = vertices
        self.vectors = vectors
        self.mass = mass
        self.color = color
        self.maxthrust = maxthrust
        self.fuel = fuel
        self.radius = radius
        self.angle = angle
        self.angleVect = angleVect
        self.mass=mass
        
    def fuelcheck(self, keys):
        booleans = {"thrust": False, "left": False, "right": False}
        if self.fuel < 0:
                self.fuel = 0
        for fuelthing in [(keys[pygame.K_w], "thrust", 1),(keys[pygame.K_a], "left", 1/2),(keys[pygame.K_d], "right", 1/2)]:
            if fuelthing[0] and self.fuel>0:
                booleans[fuelthing[1]] = True
                self.fuel-=75 * float(fuelthing[2])
                self.mass-=10 * float(fuelthing[2])
        return {"thrust": booleans["thrust"], "left": booleans["left"], "right": booleans["right"]}
    
    def getPoints(self):
        triangle = [0, (3 * math.pi / 4), (5 * math.pi / 4)]
        return np.array([(self.radius * math.cos(t + self.angle), self.radius * math.sin(t + self.angle)) for t in triangle])

    def getFlamePoints(self):
        triangle = [[(5 * math.pi / 6), 0.9*self.radius],[(7 * math.pi / 6), 0.9*self.radius],[math.pi, 1.5*self.radius]]
        return np.array([(rad * math.cos(t + self.angle), rad * math.sin(t + self.angle)) for [t, rad] in triangle])
    
    def update(self, pressed):
        for key in [(pressed["left"], -0.01), (pressed["right"], 0.01)]:
            if key[0]: self.angleVect += key[1]*movementScale
        if pressed["thrust"]: self.vectors[0] += movementScale * math.cos(self.angle); self.vectors[1] += movementScale * math.sin(self.angle)
        self.angle+=self.angleVect
        self.vertices+=self.vectors

    def draw(self, pressed):
        flamePoints = self.getFlamePoints()
        finalFlamePoints = flamePoints+self.vertices
        if pressed["thrust"]: pygame.draw.polygon(screen, red, finalFlamePoints)
        rocketPoints = self.getPoints()
        finalPoints = rocketPoints+self.vertices
        pygame.draw.polygon(screen, self.color, finalPoints)
    
class lander():
    def __init__(self,vertices,vectors,color, mass,maxthrust,fuel, radius = 20, angle=-math.pi/2, angleVect = 0):
        self.vertices = vertices
        self.vectors = vectors
        self.mass = mass
        self.color = color
        self.maxthrust = maxthrust
        self.fuel = fuel
        self.radius = radius
        self.angle = angle
        self.angleVect = angleVect
        self.mass=mass

    def fuelcheck(self, keys):
        booleans = {"thrust": False, "left": False, "right": False}
        if self.fuel < 0: self.fuel = 0

        for fuelthing in [(keys[pygame.K_w], "thrust", 1),(keys[pygame.K_a], "left", 1/2),(keys[pygame.K_d], "right", 1/2)]:
            if fuelthing[0] and self.fuel>0:
                booleans[fuelthing[1]] = True
                self.fuel-=75 * float(fuelthing[2])
                self.mass-=10 * float(fuelthing[2])
        return {"thrust": booleans["thrust"], "left": booleans["left"], "right": booleans["right"]}

rocket = rocketclass(np.array([400.0,400.0]), np.array([0.0,0.0]), (255,255,255), 6479, 1000, 10000)
top = lander(np.array([(485.0,50.0),(515.0,50.0),(535.0,65.0),(535.0,95.0),(515.0,110.0),(485.0,110.0),(465.0,95.0),(465.0,65.0)]), emptyVectors.copy(), topcolor, 2445,15000,8376)
bottom = lander(np.array([(485.0,110.0),(515.0,110.0),(550.0,135.0),(540.0,135.0),(505.0,115.0),(495.0,115.0),(460.0,135.0),(450.0,135.0)]), emptyVectors.copy(),bottomColor,2034,45000,8248)
top.vectors+=3; bottom.vectors+=3

def updateVect(top,bottom,split,thrustvalue,crash, pressed):
    totalmass=top.mass+bottom.mass if not split else top.mass
    finalthrust = thrustvalue*4000/totalmass if not split else thrustvalue*2500/totalmass
    objlist = [top] if split else [bottom,top]
    downforce = bottom.vectors[5][1]*totalmass
    sideforce = bottom.vectors[5][0]*totalmass
    if not split:
        if top.vertices[2][1]<670:
            for i in range(8):
                for key in [(pressed["thrust"], 1,1), (pressed["left"], 0, 1/2), (pressed["right"], 0, -1/2), (True, 1, -G/finalthrust)]:
                    if key[0]: 
                        for obj in objlist: obj.vectors[i][key[1]] -= finalthrust * key[2]

            for obj in objlist: obj.vertices += obj.vectors        
        else:
            if downforce<15000 and abs(sideforce)<5000:
            #if downforce<150000 and abs(sideforce)<50000:
                split=True
                top.vectors = emptyVectors.copy()
            else:
                crash = True

    elif split:
        for i in range(8):
            for key in [(pressed["thrust"], 1,1), (pressed["left"], 0, 1/2), (pressed["right"], 0, -1/2), (True, 1, -G/finalthrust)]:
                    if key[0]: 
                        for obj in objlist: obj.vectors[i][key[1]] -= finalthrust * key[2]

        top.vertices +=top.vectors
    return top,bottom,split,crash,downforce,sideforce

def drawall(top, bottom, split, pressed):
    pygame.draw.rect(screen,Mooncolor, pygame.Rect(0,760,800,800))
    if pressed["thrust"]: pygame.draw.polygon(screen, (255,0,0), ([(top.vertices[1][0], top.vertices[1][1]+55), (top.vertices[1][0]-30, top.vertices[1][1]+55), (top.vertices[1][0]-15, top.vertices[1][1]+100)]))
    for x in [(pressed["left"], 2, 3, 1), (pressed["right"], 7, 6, -1)]:
        if x[0]: pygame.draw.polygon(screen, (255,0,0), ([(top.vertices[x[1]][0],top.vertices[x[1]][1]+10),(top.vertices[x[2]][0],top.vertices[x[2]][1]-10),(top.vertices[x[1]][0]+10*x[3],top.vertices[x[1]][1]+15)]))

    for obj in [bottom,top]: pygame.draw.polygon(screen, obj.color, (obj.vertices))

    show = bottom if split == False else top
    Text=font.render("Fuel: " + str(show.fuel),False,(255,255,255))
    screen.blit(Text, (20,20))

def drawaftercrash(num,downforce,sideforce):
    screen.fill(black)
    #draw land with a hole
    pygame.draw.rect(screen,Mooncolor, pygame.Rect(0,760,800,800))
    pygame.draw.circle(screen, black, (top.vertices[1][0]-15,500), 290)
    if num < 200:
        num+=10

        #bodies
        for (obj, value) in [(bottom,3), (top,5)]:
            pygame.draw.polygon(screen, obj.color, (obj.vertices-num*obj.vectors[5][1]/value))

        #explosion
        for (num2, color) in [(0,red),(30, orange),(100,yellow),]:
            if num>num2: pygame.draw.circle(screen, color, (top.vertices[1][0]-15,670), num-num2)

    if downforce>15000 and abs(sideforce)> 5000:
        Text=smallfont.render("Both your sideforce and downforce were too high so you crashed!",False,(255,255,255))
    else:
        for (force, limit,text) in [(downforce, 15000, 'downforce'), (sideforce, 5000, 'sideforce')]:
            if abs(force)>limit:
                Text=smallfont.render("Your " + text + " was too high so you crashed!",False,(255,255,255))

    screen.blit(Text, (20,20))

    return num

while run:
    clock.tick(FPS)
    screen.fill(black)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): run = False
    
    keys = pygame.key.get_pressed()

    if phase == 'p1':
        pressed = rocket.fuelcheck(keys)
        rocket.update(pressed)
        rocket.draw(pressed)
        
    elif phase == 'p2':
        if crash == False:
            if split == False:

                pressed = bottom.fuelcheck(keys)
            
                top,bottom,split,crash,downforce,sideforce = updateVect(top, bottom, split, thrustvalue,crash, pressed)

                drawall(top, bottom, split, pressed)

            #A check to make sure you reset you w key so the ascent dosen't immedietly start
            elif split == True and wreset == False:

                if not keys[pygame.K_w]: wreset = True

                drawall(top, bottom, split, pressed)

            elif split == True and wreset == True:
                
                pressed = top.fuelcheck(keys)

                top,bottom,split,crash,downforce, sideforce = updateVect(top,bottom,split, thrustvalue,crash, pressed)

                drawall(top, bottom, split, pressed)

        else:
            num = drawaftercrash(num,downforce,sideforce)

    pygame.display.update()