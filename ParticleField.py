from panda3d.core import * # needs to be improved later on (maybe)
from ProceduralGen import *
from copy import deepcopy
from physX import engine, HarmoscLink, LinArrayFormat, ArrayLinFormat
from NodeStates import State

class ParticleMesh:
    
    def __init__(self,l,w,Vl,Vw,extraArgs):
        '''
        ParticleMesh
        ===
        this is a particle array, it reacts to mechanical stresses.
        Arguments needed: lenght and width in 3d units, length and width in amount of vertices (the four must be ints).
        '''
        self.surface = RectangleSurface(l,w,Vl,Vw)
        
        self.RuleData = [[State("free") for i in range(Vw)] for j in range(Vl)] # node behavior

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

    def update(self, dt, physXtasks, frame):
        # MODIFY THE SURFACE (somehow)
        self.CurrentPosState = self.surface.GetPosData() # get data from the mesh (used when baking) and update
        Vl, Vw = self.engine.GetSize() # we'll use these later


        # update the RuleData
        for task in physXtasks: # scan the user data
            chosen_rule = task[0].split("_")
            type, rule = chosen_rule[0], chosen_rule[1]
            if len(chosen_rule)==3: # means it's a following rule
                func = chosen_rule[2]
            
            # you need to implement multiple overrides !!!!!
            if rule == "static": # pas tres propre je sais mais il est une heure du mat merde
                try:
                    coord = Vec3(task[2])
                except TypeError: # means some of the given coords are None, which means 'keep the original coordinates'
                    coord = list(task[2])
                    for i in range(3):
                        if coord[i] == None:
                            coord[i] = self.CurrentPosState[(task[1][0]-1)*Vw + task[1][1]][i] # uses Linear format

                begin, end = task[3][0], task[3][1]
                if begin <= frame <= end:
                    self.RuleData[task[1][0]][task[1][1]].setRule(rule, coord = coord)
                else: 
                    self.RuleData[task[1][0]][task[1][1]].setRule("free")

            elif rule == "following":
                begin, end = task[3][0], task[3][1]
                settings = [x for x in task[2][:3]] + [Vec3(task[2][3])]
                if begin <= frame <= end:
                    self.RuleData[task[1][0]][task[1][1]].setRule(rule, followingFunc = func, FuncSettings = settings)
                else:
                    self.RuleData[task[1][0]][task[1][1]].setRule("free")
            
            elif rule == "virtual":
                begin, end = task[2][0], task[2][1]
                if begin <= frame <= end:
                    self.RuleData[task[1][0]][task[1][1]].setRule(rule)
                else:
                    self.RuleData[task[1][0]][task[1][1]].setRule("free")
            

        # update pos, speed and accel data
        PosState, self.speedData, self.accelData = self.engine.bake(self.CurrentPosState, 
                                                                    self.NodeGeometry, 
                                                                    self.speedData, 
                                                                    self.accelData, 
                                                                    self.RuleData, 
                                                                    dt,
                                                                    frame) # 
        
        self.surface.deform(PosState) # modifies the mesh and calculates the normals accordingly


        upper_normals = LinArrayFormat(self.surface.GetNormalData(), (Vl,Vw))
        for y in range(len(self.NodeGeometry)): # updating orientation normals
            for x in range(len(self.NodeGeometry[y])):
                self.NodeGeometry[y][x][0] = upper_normals[y][x]
        
        mesh = deepcopy(self.surface.GeomNode) # copy after it has been modified
        return mesh, LinArrayFormat(PosState,(Vl,Vw))

    def override(self, coord, *args):
        return None
    
