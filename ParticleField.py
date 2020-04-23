from panda3d.core import * # needs to be improved later on (maybe)
from ProceduralGen import *
from copy import deepcopy
from physX import engine, PhysXNode, LinArrayFormat, ArrayLinFormat
from NodeStates import State

class ParticleMesh:
    
    def __init__(self,l,w,Vl,Vw,extraArgs):
        '''
        ParticleMesh
        ===
        this is a particle array, it reacts to mechanical stresses.
        Arguments needed: lenght and width in 3d units, length and width in amount of vertices (the four must be ints).
        '''
        # core variables
        self.size = (Vl,Vw)
        self.surface = RectangleSurface(l,w,Vl,Vw)
        PosState = LinArrayFormat(self.surface.GetPosData(), (Vl, Vw))
        self.Nodes = [[PhysXNode(j,i,PosState[j][i],1,"free") for i in range(Vw)] for j in range(Vl)] # Attention ! Erreur d'indices possible
        ''' # useless, this chunk of code will be deleted in a few hours, if you see this years later, this project might be dead
        self.RuleData = [[State("free") for i in range(Vw)] for j in range(Vl)] # node behavior
        self.CurrentPosState = self.surface.GetPosData()
        upper_normals = LinArrayFormat(self.surface.GetNormalData(), (Vl,Vw)) # these are the upper normals,  we need to add link normals
        self.speedData = [[LVecBase3f(0,0,0) for i in range(Vw)] for j in range(Vl)] # initialize at zero speed
        self.accelData = [[LVecBase3f(0,0,0) for i in range(Vw)] for j in range(Vl)] # could've just deepcopied the speedData
        '''
        # use the provided physics engine (see physX file)
        self.engine = engine()

        return None # ya I need to stop writing this someday 


    def update(self, dt, physXtasks, frame, memory):
        # MODIFY THE SURFACE
        Vl, Vw = self.size
        '''
        posdata = LinArrayFormat(self.surface.GetPosData())
        for i in range(Vl):
            for j in range(Vw):
                self.Nodes[i][j].setPos(posdata[i][j])
        '''
        # Now we have to deal with rules
        for task in physXtasks: # scan the user data
            chosen_rule = task[0].strip().split("_")
            type, rule = chosen_rule[0], chosen_rule[1] # type may be highlighted but is still a str just type type(type) and you'll know :p
            
            
            if rule == "static" and task[3][0] <= frame <= task[3][0]: # pas tres propre je sais mais il est une heure du mat merde
                Fstart, Fend = task[3]
                PosData = memory.getFramePosData(Fstart)


                if type == 'line': # more than one override
                    currentCenter = Vec3(0,0,0) # initialize the center of the line
                    
                    for i in range(Vw):
                        currentCenter += PosData[task[1]-1][i]
                    med = currentCenter/Vw
                    coord = troubleShoot_NoneTypes(task[2], med)

                    displacement = coord - med # this is the displacement vector
                    for i in range(Vw):
                        self.Nodes[task[1]-1][i].state.setRule('static', coord = PosData[task[1]-1][i] + displacement)
                elif type == 'column':
                    currentCenter = Vec3(0,0,0) # initialize the center of the column
                    for i in range(Vl):
                        currentCenter += PosData[i][task[1]-1]
                    med = currentCenter/Vl
                    coord = troubleShoot_NoneTypes(task[2], med)

                    displacement = coord - med # this is the displacement vector
                    for i in range(Vl):
                        self.Nodes[i][task[1]-1].state.setRule('static', coord = PosData[i][task[1]-1] + displacement)
                elif type == 'single':
                    coord = troubleShoot_NoneTypes(task[2], PosData[task[1][0]-1][task[1][1]-1])
                    self.Nodes[task[1][0]-1][task[1][1]-1].state.setRule('static', coord = coord)
                
            elif rule == "following":
                func = chosen_rule[2]

                begin, end = task[3][0], task[3][1]
                settings = [x for x in task[2][:3]] + [Vec3(task[2][3])]
                if begin <= frame <= end:
                    self.Nodes[task[1][0]-1][task[1][1]-1].state.setRule(rule, followingFunc = func, FuncSettings = settings)
                else:
                    self.Nodes[task[1][0]-1][task[1][1]-1].state.setRule("free")
            
            elif rule == "virtual":
                begin, end = task[2][0], task[2][1]
                if begin <= frame <= end:
                    self.Nodes[task[1][0]-1][task[1][1]-1].state.setRule(rule)
                else:
                    self.Nodes[task[1][0]-1][task[1][1]-1].state.setRule("free")
            

        # Update Nodes
        NodeOutput = self.engine.bake(self.Nodes, dt, frame) 
        for i in range(Vl): 
            for j in range(Vw):
                self.Nodes[i][j].update(NodeOutput[i][j], frame)

        self.surface.deform(ArrayLinFormat([[NodeOutput[i][j].pos for i in range(Vl)] for j in range(Vw)])) # modifies the mesh and calculates the normals accordingly
        mesh = deepcopy(self.surface.GeomNode) # copy after it has been modified
        return mesh, [[self.Nodes[i][j].pos for i in range(Vl)] for j in range(Vw)]

    def override(self, coord, *args):
        return None
    

def troubleShoot_NoneTypes(Vec, replaceVec):
    output = Vec
    if None in Vec:
        for i in range(len(Vec)):
            if Vec[i] == None:
                output[i] = replaceVec[i]            
    return Vec3(output)