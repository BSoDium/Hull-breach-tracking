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
                    temp = self.lenght((x,y),u)
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
        for n in range(sizey):
            try:
                test = BufferTable[0][n] # triggers the exception when needed
                ScanOrder.append([(x , n - x) for x in range(n+1)])
            except:
                pass
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
        name = 'terrain.bmp'
        img.save(name)
        print("\n",end='\r')
        print("done")
        print("saved as "+ name)

        return output

    def lenght(self,posA,posB):
        dx, dy = posB[0] - posA[0], posB[1] - posA[1]
        return sqrt(dx**2 + dy**2)

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