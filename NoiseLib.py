from PIL import Image
from random import randrange
import random
from math import sqrt

class Noise:
    def __init__(self):
        self.table = []
        self.ColorMode = "RGBA" # initialize as RGBA color table
        self.GenMode = "local" # global should (theoretically) generate an infinite field, I have no idea how to achieve this though
        return None

    def create(self,name,size,args):
        '''
        creates a noise image, corresponding to the requested name and size (size is a tuple)
        args contains the point sample count interval, which is a two values tuple, and the Fadeout Distance percentage
        '''
        table = {"voronoi":self.voronoi, "STerrain":self.StepTerrain}
        if name in table:
            self.ret = table[name](size,args)
        return None

    def voronoi(self,size,args): # this version of the algorithm doesn't use 
        a,b = args[0],args[1] # args 0 and 1 are the limits for samplecount randomization
        sample_count = randrange(a,b)
        sizex, sizey= size[0], size[1]
        FadeoutDistance = args[2]*max(sizex,sizey)
        BufferTable = [[(0,0,0,1) for i in range(sizey)] for j in range(sizex)] # create an empty pic data
        CellList = [[randrange(0,sizex),randrange(0,sizey)] for i in range(sample_count)] 
        for y in range(len(BufferTable)):
            print("processing voronoi noise...  "+str(y/len(BufferTable)*100)[:4]+"% ",end='\r') # tell the user something is actually happening
            for x in range(len(BufferTable[y])): # we could just use BufferTable[0], same result
                d = -1 # negative for "undefined"
                for u in CellList:
                    temp = lenght((x,y),u)
                    if temp < d or d < 0:
                        d = temp
                # now we know the distance to the closest point
                BufferTable[y][x] = (int(255*smoothstep(d/FadeoutDistance)),int(255*smoothstep(d/FadeoutDistance)),int(255*smoothstep(d/FadeoutDistance)),255)
        
        output = []
        for x in BufferTable:
            output+=x
        output = tuple(output)


        img = Image.new('RGBA', (sizex, sizey))
        img.putdata(output)
        name = 'voronoi.png'
        img.save(name)
        print("\n",end='\r')
        print("done")
        print("saved as "+ name)

        return output
    
    def StepTerrain(self,size,args):
        sizex, sizey= size[0], size[1]
        BufferTable = [[(0,0,0,1) for i in range(sizey)] for j in range(sizex)]
        ScanOrder = []
        for n in range(max(sizex,sizey)): #topleft triangle
            new = []
            i,p = n,0
            while p < min(sizex,sizey):
                new.append((i,p))
                i -= 1
                p += 1  
            ScanOrder.append(new)
        '''
        for p in range(min(sizex,sizey),-1,-1): #bottomright triangle // go up while scanning the left stairs
            new = []
            i,n = p,max(sizex,sizey) # initalize local pointers
            while n >= 0:
                new.append((n,i))
                i -= 1
                n -= 1
            ScanOrder.append(new)
        '''
        temprand = randrange(0,255)
        BufferTable[0][0] = (temprand,temprand,temprand,1) # initalize
        for a in range(len(ScanOrder[1:])):
            for b in range(len(ScanOrder[a])):
                temprand = random.choice([1,-1])*random.randrange(0,10) # variation
                coord = ScanOrder[a][b]
                try:
                    choice = random.choice([0,1])
                    if choice: # the computer chooses column alteration
                        if 0 <= BufferTable[coord[0]-1][coord[1]] [0] + temprand <= 255: # range check
                            pass
                        else:
                            temprand *= -1
                        BufferTable[coord[0]][coord[1]] = (BufferTable[coord[0]-1][coord[1]] [0] + temprand,
                                                        BufferTable[coord[0]-1][coord[1]] [1] + temprand,
                                                        BufferTable[coord[0]-1][coord[1]] [2] + temprand,
                                                        1)
                    else: # line alteration
                        if 0 <= BufferTable[coord[0]][coord[1]-1] [0] + temprand <= 255: # range check
                            pass
                        else:
                            temprand *= -1
                        BufferTable[coord[0]][coord[1]] = (BufferTable[coord[0]][coord[1]-1] [0] + temprand,
                                                        BufferTable[coord[0]][coord[1]-1] [1] + temprand,
                                                        BufferTable[coord[0]][coord[1]-1] [2] + temprand,
                                                        1)
                except:
                    pass

        output = []
        for x in BufferTable:
            output+=x
        output = tuple(output)
        
        img = Image.new('RGBA', (sizex, sizey))
        img.putdata(output)
        img.show()
        name = 'terrain.png'
        img.save(name)
        print("\n",end='\r')
        print("done")
        print("saved as "+ name)

        return output
    
    def Perlin(self,size,args):
        gridRes = (4,4) # gridres[0]=gridres[1]|size[0]
        # create Buffer
        BufferTable = [[(0,0,0,1) for i in range(sizey)] for j in range(sizex)]
        # create grid
        ProceduralVectField = [[(randrange(0,360), randrange(0,360), i*gridRes[0], j*gridRes[1]) for i in range(size[0]//gridRes[0])] for j in range(size[1]//gridRes[1])]
        # dot product
        for i in range(size[0]):
            #per column iteration
            for j in range(size[1]):
                # per pixel iteration
                Interval = [(i - i%4, i - i%4 + 4), # previous and next point on the grid
                            (j - j%4, j - j%4 + 4)]
                index = [(Interval[0][0]/4,Interval[0][1]/4),
                        (Interval[1][0]/4,Interval[1][1]/4)]
                scan = [(index[0][0],index[1][0]),
                        (index[0][1],index[1][0]),
                        (index[0][0],index[1][1]),
                        (index[0][1],index[1][1])] # closest grid points
                for x in scan:
                    dist = vector(ProceduralVectField [x[0]] [x[1]] [2:], (i, j) ) # vecteur distance
                    actualVect = ProceduralVectField [x[0]] [x[1]] [:2]



        return None

def lenght(posA,posB):
    dx, dy = posB[0] - posA[0], posB[1] - posA[1]
    return sqrt(dx**2 + dy**2)
    
def vector(posA,posB):
    dx, dy = posB[0] - posA[0], posB[1] - posA[1]
    return (dx,dy)


def smoothstep(x):
    '''math function smoothstep'''
    if x <= 0:
        return 0
    elif x >= 1:
        return 1
    else:
        return 3*x**2 - 2*x**3

noise = Noise()
noise.create("STerrain",(400,400),None)
#noise.create("voronoi",(400,400),(109,110,0.15)) # testing the voronoi noise specifically