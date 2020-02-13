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

        upper_normals = LinArrayFormat(self.surface.GetNormalData(), (Vl,Vw)) # these are the upper normals,  we need to add link normals
        self.NodeGeometry = [] # initialize
        for y in range(Vl):
            line = []
            for x in range(Vw):
                temp = [upper_normals[y][x]]
                indexlist = [ # je crois que c'est la que j'ai foire les indices mais ca marche donc chut
                    (x+1, y),
                    (x, y-1),
                    (x-1, y),
                    (x, y+1)
                ]
                for a in indexlist:
                    if 0 <= a[0] < Vw and 0 <= a[1] < Vl: # check if a does actually refer to one of the neighbours
                        vect = Vec3(self.CurrentPosState[a[0] + a[1]*Vw] - self.CurrentPosState[x + y*Vw])
                        temp.append(vect.normalized().angleDeg(temp[0].normalized())) 
                    else:
                        temp.append(None) # need to keep the indices right
                line.append(temp)
            self.NodeGeometry.append(line)
            # the node geometry contains 5 elements long lists: orientation normal, angle1, angle2, angle3, angle4

        # we now have some correct normal data

        self.speedData = [[LVecBase3f(0,0,0) for i in range(Vw)] for j in range(Vl)] # initialize at zero speed
        self.accelData = [[LVecBase3f(0,0,0) for i in range(Vw)] for j in range(Vl)] # could've just deepcopied the speedData

        # use the provided physics engine (see physX file)
        self.engine = engine()
        self.engine.SetSize(Vl,Vw)
        
        '''
        self.linkData = [] # creates the link table (array-like structure)
        for i in range(2 * Vl - 1):
            if i%2:  # odd i
                loc = [((i-1, j) , (i, j)) for j in range(Vw)]
            else:
                loc = [((i , j) , (i , j+1)) for j in range(Vw - 1)]
            self.linkData.append([HarmoscLink(a, b, self.engine.attributes['rigidconst']) for a,b in loc])
        '''
        return None # ya I need to stop writing this someday 

    def update(self,dt):
        # MODIFY THE SURFACE (somehow)
        self.CurrentPosState = self.surface.GetPosData() # get data from the mesh (used when baking) and update

        PosState, self.speedData, self.accelData = self.engine.bake(self.CurrentPosState, self.NodeGeometry, self.speedData, self.accelData,dt) # 
        
        self.surface.deform(PosState) # modifies the mesh and calculates the normals accordingly

        Vl, Vw = self.engine.GetSize()
        upper_normals = LinArrayFormat(self.surface.GetNormalData(), (Vl,Vw))
        for y in range(len(self.NodeGeometry)): # updating orientation normals
            for x in range(len(self.NodeGeometry[y])):
                self.NodeGeometry[y][x][0] = upper_normals[y][x]
        
        mesh = deepcopy(self.surface.GeomNode) # copy after it has been modified
        return mesh
