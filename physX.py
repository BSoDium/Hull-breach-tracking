from panda3d.core import Vec3, LVecBase3f, NodePath
from copy import deepcopy
from Geometry import crossProd
from math import isinf, cos, sin, pi
import NodeStates

class engine:
    def __init__(self): 
        self.Id = "metal_softbody - 4pernode_harmosc" # not sure about the syntax yet
        self.attributes = {
            "linearRigidConst":5, #
            "linearDefaultPos":2, # should become more dynamic in a future version
            "nodemass":1, # kg usi
            "friction":0

        }
        self.size = None

        self.LastPos = None # local buffer
        
        return None

    def bake(self, PosData, 
                NodeGeometry,
                LinSpeedState, 
                LinAccelState, 
                RuleTable,
                TimeShift,
                frame): # cf https://docs.blender.org/manual/en/latest/physics/baking.html
        
        try:
            assert len(self.size) == 2 # debug
        except:
            print("Please provide correct table size data before computing physics")
            return 1

        MainPosBuffer = deepcopy(LinArrayFormat(PosData, self.size)) # we will only modify the buffer\
        MainNodeGeomBuffer = deepcopy(NodeGeometry)
        MainLinSpeedBuffer = deepcopy(LinSpeedState)
        MainLinAccelBuffer = deepcopy(LinAccelState)

        self.LastPos = MainPosBuffer # save last known position as engine data (used for BDF)
        
        length, width = len(MainPosBuffer), len(MainPosBuffer[0])

        for l in range(length): # actually len(MainPosBuffer) = length
            for w in range(width):
                if RuleTable[l][w].getRule().__class__.__name__=="free":
                    pos = Vec3(MainPosBuffer[l][w]) # convert to vec3 for easier vector manipulation
                    speed = Vec3(MainLinSpeedBuffer[l][w])
                    NodeGeometry = MainNodeGeomBuffer[l][w] 

                    AppliedForce = Vec3(0, 0, 0) # utilise pour le BAME
                
                    neighbours = [ # connected nodes
                                (w+1,l),
                        (w,l-1),        (w-1,l),
                                (w,l+1)
                    ]
                    # I know the indices aren't ordered properly but I somehow fucked the format up at some point so here we are

                    for x in range(len(neighbours)): # ie 4
                        a,b = neighbours[x]
                        if 0 <= a < width and 0 <= b < length and not RuleTable[b][a].getRule.__class__.__name__=="virtual": # side limit
                            DistVect = Vec3(MainPosBuffer[b][a]) - pos
                            NormDistVect = DistVect.normalized()
                            currentL = DistVect.length()
                            AppliedForce += Vec3(NormDistVect * self.attributes['linearRigidConst']*(currentL - self.attributes['linearDefaultPos']))

                    methods = {
                        "euler":NextPos_Euler,
                        "verlet":NextPos_Verlet
                    }

                    # we will be using euler at first
                    procedure = methods['euler']

                    MainLinAccelBuffer[l][w], MainLinSpeedBuffer[l][w], MainPosBuffer[l][w] = procedure(AppliedForce, 
                                                                                                    self.attributes['nodemass'],
                                                                                                    pos,
                                                                                                    speed*(1-self.attributes["friction"]),
                                                                                                    TimeShift)
                elif RuleTable[l][w].getRule().__class__.__name__=="virtual":
                    MainLinAccelBuffer[l][w], MainLinSpeedBuffer[l][w] = LVecBase3f(0,0,0), LVecBase3f(0,0,0)
                else:
                    # how do I define the pt0 ?????
                    pt0 = Vec3(0,0,0)
                    MainLinAccelBuffer[l][w], MainLinSpeedBuffer[l][w], MainPosBuffer[l][w] = LVecBase3f(0,0,0), LVecBase3f(0,0,0), LVecBase3f(tuple(RuleTable[l][w].getPos(frame, pt0)))
                

        
        
        return ArrayLinFormat(MainPosBuffer), MainLinSpeedBuffer, MainLinAccelBuffer # currently does nothing sry

    def GetId(self):
        '''
        The engine is fully modular and the physX file is a tiny piece of the
        software, that any developer should be able to replace, in order to 
        simulate different materials and situations without rewriting the whole
        code. this function is therefore necessary if you need to identify the 
        engine you're using
        '''
        return self.Id

    def SetSize(self, VertexLength, VertexWidth):
        self.size = (VertexLength, VertexWidth)
        return None
    
    def GetSize(self):
        return self.size


class PhysXNode: # stores data for each node
    def __init__(self, index1, index2, pos, frame:int , state:str, Hpr:Vec3 = Vec3(0,0,0)): # frame indicates the starting frame

        self.index2d = (index1, index2)
        self.frame = 1 # default
        self.mass = 1 # default (0 generates errors)
        self.radius = 0.1
        J = self.mass * self.radius**2
        self.inertia = [
            [J , 0 , 0],
            [0 , J , 0],
            [0 , 0 , J]
        ]
        self.pos = pos # default
        self.Hpr = Hpr
        self.linSpeed = (0,0,0)
        self.linAccel = (0,0,0)
        self.rotSpeed = (0,0,0) # deg/s (rad trop compliques a gerer)
        self.rotAccel = (0,0,0) # deg/s**2

        self.destroyed = False # may be changed at some point during the sim

        assert type(state) is str
        self.state = NodeStates.State(str(state)) # by default
        self.nodePath = NodePath('Part%s' %str(index1)+"_"+str(index2))
        self.nodePath.reparentTo(render)
        self.nodePath.setPos(self.pos)
        self.nodePath.setHpr(self.Hpr)
        
        self.axis = loader.loadModel('assets/meshes/axis.egg')
        self.axis.reparentTo(self.nodePath)
        self.axis.hide() # on startup, debugging axis will not be shown
        self.debugMode = False
        
    
    def update(self,
        pos,
        Hpr,
        linSpeed,
        linAccel,
        rotSpeed,
        rotAccel):
    
        self.pos = pos
        self.Hpr = Hpr
        self.linSpeed = linSpeed
        self.linAccel = linAccel
        self.rotSpeed = rotSpeed
        self.rotAccel = rotAccel

        self.nodePath.setPos(self.pos)
        self.nodePath.setHpr(self.Hpr)
    
    def toggleDebug(self):
        if self.debugMode:
            self.axis.hide()
        else:
            self.axis.show()
        self.debugMode = not self.debugMode
    
    def getPos(self):
        return self.pos
# engine procedures come next


def NextPos_Verlet(force, mass, initialPos, initialSpeed, dt):

    return None

def NextPos_Euler(force, mass, initialPos, initialSpeed, dt):
    accel = force/mass
    speed = initialSpeed + accel*dt
    pos = initialPos + speed*dt
    return accel, speed, pos

def LinArrayFormat(data, size):
    '''
    Converts vertex 1d lists to 2d arrays using the provided size information
    '''

    length, width = size[0], size[1] # helps with understanding the function
    
    LocalBuffer = []
    for x in range(0,len(data),width):
        LocalBuffer.append(data[x:x+width])
    
    try: # debugging
        assert len(LocalBuffer)==length
    except:
        print("you stupid idiot the converter is broken again")
        pass

    return LocalBuffer


def ArrayLinFormat(data):
    '''
    Same as LinArrayFormat, but inverted
    '''
    
    LocalBuffer = []
    for x in data:
        for y in x:
            LocalBuffer.append(y)
    
    return LocalBuffer

