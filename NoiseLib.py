from PIL import Image
from random import randrange
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
        if name == "voronoi":
            self.table = self.voronoi(size,args)
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
                BufferTable[y][x] = (int(255*(d/FadeoutDistance)),int(255*(d/FadeoutDistance)),int(255*(d/FadeoutDistance)),255)
        
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
    
    def lenght(self,posA,posB):
        dx, dy = posB[0] - posA[0], posB[1] - posA[1]
        return sqrt(dx**2 + dy**2)

noise = Noise()
noise.create("voronoi",(400,400),(109,110,0.2)) # testing the voronoi noise specifically