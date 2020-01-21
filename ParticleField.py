from panda3d.core import * # needs to be improved later on (maybe)
from ProceduralGen import *
from copy import deepcopy
from physX import engine, HarmoscLink, LinArrayFormat, ArrayLinFormat

class ParticleMesh:
    
    def __init__(self,l,w,Vl,Vw,extraArgs):
        '''
        ParticleMesh
        ===
        this is a particle array, it reacts to mechanical stresses.
        Arguments needed: lenght and width in 3d units, length and width in amount of vertices (the four must be ints).
        '''
        self.surface = RectangleSurface(l,w,Vl,Vw)
        self.CurrentPosState = self.surface.GetPosData()

        upper_normals = LinArrayFormat(self.surface.GetNormalData(), (Vl,Vw))# these are the upper normals,  we need to add link normals
        self.NormalState = [] # initialize
        for y in range(Vl):
            line = []
            for x in range(Vw):
                temp = [upper_normals[y][x]]
                indexlist = [
                    (x+1, y),
                    (x, y-1),
                    (x-1, y),
                    (x, y+1)
                ]
                for a in indexlist:
                    if 0 <= a[0] < Vw and 0 <= a[1] < Vl:
                        temp.append(self.CurrentPosState[a[0] + a[1]*Vw] - self.CurrentPosState[x + y*Vw]) 
                    else:
                        temp.append(None) # need to keep the indices right
                line.append(temp)
            self.NormalState.append(line)

        # we now have some correct normal data

        self.speedData = [[LVecBase3f(0,0,0) for i in range(Vw)] for j in range(Vl)] # initialize at zero speed
        
        self.engine = engine()
        
        '''
        self.linkData = [] # creates the link table (array-like structure)
        for i in range(2 * Vl - 1):
            if i%2:  # odd i
                loc = [((i-1, j) , (i, j)) for j in range(Vw)]
            else:
                loc = [((i , j) , (i , j+1)) for j in range(Vw - 1)]
            self.linkData.append([HarmoscLink(a, b, self.engine.attributes['rigidconst']) for a,b in loc])
        '''
        
        self.engine.SetSize(Vl,Vw)
        return None

    def update(self,dt):
        # MODIFY THE SURFACE (somehow)
        self.CurrentPosState = self.surface.GetPosData() # get data from the mesh (used when baking)

        PosState, self.speedData, self.NormalState = self.engine.bake(self.CurrentPosState, self.NormalState, self.speedData, dt) # 
        self.surface.deform(PosState) # modifies the mesh and calculates the normals accordingly

        mesh = deepcopy(self.surface.GeomNode) # copy after it has been modified
        return mesh
