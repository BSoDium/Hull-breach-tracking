from panda3d.core import Vec3, LVecBase3f, NodePath, Filename
from copy import deepcopy
from Geometry import crossProd
from math import isinf, cos, sin, pi
import NodeStates, os, sys
import numpy as np


MAINDIR = Filename.from_os_specific(os.path.abspath(sys.path[0])).getFullpath()

class engine:
    def __init__(self): 
        self.Id = "metal_softbody - 4pernode_harmosc" # not sure about the syntax yet
        self.attributes = {
            "linearRigidConst":5, #
            "linearDefaultPos":2, # should become more dynamic in a future version
            "nodemass":1, # kg usi
            "friction":0

        }

        self.LastPos = None # local buffer
        
        return None

    ''' # reference when changing, must be deleted later
    def bake(self, PosData, 
                NodeGeometry,
                LinSpeedState, 
                LinAccelState, 
                RuleTable,
                TimeShift,
                frame): # cf https://docs.blender.org/manual/en/latest/physics/baking.html
    '''
    def bake(self, Nodes, TimeShift, frame): 
        '''
        cf https://docs.blender.org/manual/en/latest/physics/baking.html
        '''
        Vl, Vw = (len(Nodes), len(Nodes[0])) # might be usefull
        '''
        MainPosBuffer = deepcopy([[Nodes[i][j].pos for i in range(Vl)] for j in range(Vw)]) # we will only modify the buffer\
        MainNodeGeomBuffer = deepcopy([[Nodes[i][j].getAxisVect(render) for i in range(Vl)] for j in range(Vw)])
        MainLinSpeedBuffer = deepcopy([[Nodes[i][j].linSpeed for i in range(Vl)] for j in range(Vw)])
        MainLinAccelBuffer = deepcopy([[Nodes[i][j].linAccel for i in range(Vl)] for j in range(Vw)])
        '''
        # this may be faster than creating a buffer for every single type of data (older version)
        MainNodeBuffer = deepcopy(Nodes)

        for l in range(Vl):
            for w in range(Vw):
                if Nodes[l][w].state.getRule().__class__.__name__=="free":
                    pos = Vec3(Nodes[l][w].getPos()) # convert to vec3 for easier vector manipulation
                    linSpeed = Vec3(Nodes[l][w].linSpeed)
                    Hpr = Vec3(Nodes[l][w].Hpr)
                    rotSpeed = Vec3(Nodes[l][w].rotSpeed)
                    NodeGeometry = Nodes[l][w].getAxisVect(render) # unused by now

                    # Initialize variables
                    AppliedForce = Vec3(0, 0, 0) 
                    AppliedTorque = Vec3(0, 0, 0)
                
                    neighbours = [ # connected nodes
                                (w,l-1),
                        (w-1,l),        (w+1,l),
                                (w,l+1)
                    ]
                    # I know the indices aren't ordered properly but I somehow fucked the format up at some point so here we are

                    for x in range(len(neighbours)): # ie 4
                        a,b = neighbours[x]
                        if 0 <= a < Vw and 0 <= b < Vl: # side limit
                            # this still has to be somehow modified because every single line of it is fundamentally WRONG
                            DistVect = Vec3(Nodes[b][a].pos) - pos
                            NormDistVect = DistVect.normalized()
                            currentL = DistVect.length()
                            AppliedForce += Vec3(NormDistVect * self.attributes['linearRigidConst']*(currentL - self.attributes['linearDefaultPos']))

                    methods = {
                        "euler":NextPos_Euler,
                        "verlet":NextPos_Verlet
                    }

                    # we will be using euler at first
                    procedure = methods['euler']

                    alias = MainNodeBuffer[l][w]
                    alias.linAccel, alias.linSpeed, alias.pos, alias.rotAccel, alias.rotSpeed, alias.Hpr = procedure(
                        AppliedForce, 
                        AppliedTorque,
                        Nodes[l][w].mass,
                        Nodes[l][w].inertia,
                        pos,
                        linSpeed*(1-self.attributes["friction"]),
                        Hpr,
                        rotSpeed,
                        TimeShift)
                elif Nodes[l][w].state.getRule().__class__.__name__=="virtual":
                    alias = MainNodeBuffer[l][w]
                    alias.linAccel, alias.linSpeed, alias.rotAccel, alias.rotSpeed = LVecBase3f(0,0,0), LVecBase3f(0,0,0), LVecBase3f(0,0,0), LVecBase3f(0,0,0)
                else:
                    '''
                    pt0 = Vec3(0,0,0)
                    MainLinAccelBuffer[l][w], MainLinSpeedBuffer[l][w], MainPosBuffer[l][w] = LVecBase3f(0,0,0), LVecBase3f(0,0,0), LVecBase3f(tuple(RuleTable[l][w].getPos(frame, pt0)))
                    '''
                    pass # we'll just leave it for now

        
        
        return MainNodeBuffer

    def GetId(self):
        '''
        The engine is fully modular and the physX file is a tiny piece of the
        software, that any developer should be able to replace, in order to 
        simulate different materials and situations without rewriting the whole
        code. this function is therefore necessary if you need to identify the 
        engine you're using
        '''
        return self.Id


class PhysXNode: # stores data for each node
    def __init__(self, index1, index2, pos, frame:int , state:str, Hpr:Vec3 = Vec3(0,0,0)): # frame indicates the starting frame

        self.index2d = (index1, index2)
        self.frame = 1 # default
        self.mass = 1 # default (0 generates errors)
        self.radius = 0.1
        J = self.mass * self.radius**2
        A, B, C, D, E, F = J, J, J, 0, 0, 0 # cstes d'inertie SI
        self.inertia = np.array([
            [ A,-F,-E],
            [-F, B,-D],
            [-E,-D, C]
        ])
        self.pos = pos # default
        self.Hpr = Hpr
        self.linSpeed = (0,0,0)
        self.linAccel = (0,0,0)
        self.rotSpeed = (0,0,0) # deg/s (rad trop compliques a gerer)
        self.rotAccel = (0,0,0) # deg/s**2

        assert type(state) is str
        self.state = NodeStates.State(str(state)) # STATE VAR (behavior)
        self.nodePath = NodePath('Part%s' %str(index1)+"_"+str(index2))
        self.nodePath.reparentTo(render)
        self.nodePath.setPos(self.pos)
        self.nodePath.setHpr(self.Hpr)
        
        self.axis = loader.loadModel(MAINDIR+'/assets/meshes/axis.egg')
        self.axis.reparentTo(self.nodePath)
        self.axis.setScale(0.5)
        self.axis.hide() # on startup, debugging axis will not be shown
        
        self.axisVect = [
            Vec3(1,0,0),
            Vec3(0,1,0),
            Vec3(0,0,1)
        ]
        self.debugMode = False
        
    
    def update(self, PXNode, frame):
        
        self.frame = frame
        self.pos = PXNode.pos
        self.Hpr = PXNode.Hpr
        self.linSpeed = PXNode.linSpeed
        self.linAccel = PXNode.linAccel
        self.rotSpeed = PXNode.rotSpeed
        self.rotAccel = PXNode.rotAccel

        self.nodePath.setPos(self.pos)
        self.nodePath.setHpr(self.Hpr)
    
    def toggleAxis(self):
        '''
        toggles local axis display
        '''
        if self.debugMode:
            self.axis.hide()
        else:
            self.axis.show()
        self.debugMode = not self.debugMode
    
    def getAxisVect(self, node):
        '''
        returns the vectors from the axis as seen from the provided node
        '''
        return tuple([node.getRelativeVector(self.nodePath, i) for i in self.axisVect])
    
    def getPos(self):
        return self.pos
    
    def setPos(pos:Vec3):
        self.pos = pos
        self.nodePath.setPos(pos)
    
    def setHpr(Hpr:Vec3):
        self.Hpr = Hpr
        self.nodePath.setHpr(Hpr)

# engine procedures come next


def NextPos_Verlet(force, mass, initialPos, initialSpeed, dt):
    raise NotImplementedError

def NextPos_Euler(force, torque, mass, inertia:np.array, initialPos, initialSpeed, initialHpr, initialRotSpeed, dt):
    '''
    be aware that the following operations are made using Vec3 objects,
    which implies that the THREE vector components are being handled
    '''
    # LIN
    accel = force/mass
    speed = initialSpeed + accel*dt
    pos = initialPos + speed*dt

    # ROT
    r1, r2, r3 = torque[0], torque[1], torque[2]
    
    A, B, C, D, E, F = inertia[0,0], inertia[1,1], inertia[2,2], -inertia[1,2], -inertia[0,2], -inertia[0,1]
    '''
    H = - (D + F*E/A) * E*F/(B*A - F**2) - (E**2)/A - D*A/(B*A - F**2)*(D + F*E/A) - D
    U = r3 + E*r1/A + E*F/(B*A - F**2) * r2 + E*F**2*r1/(A*(B*A - F**2)) + D*A*(r2 + F*r1/A)/(B*A - F**2)
    
    dw3 = U/H
    dw2 = A/(B*A - F**2) * (r2 + F*r1/A + dw3 * (D + F*E/A))
    dw1 = r1/A + F/A * dw2 + E/A * dw3
    '''
    dw1, dw2, dw3 = r1/A, r2/B, r3/C
    rotAccel = Vec3(dw1, dw2, dw3)
    rotSpeed = initialRotSpeed + rotAccel*dt # USE DEGREES !!!
    Hpr = initialHpr + rotSpeed*dt

    return accel, speed, pos, rotAccel, rotSpeed, Hpr

def LinArrayFormat(data, size):
    '''
    Converts vertex 1d lists to 2d arrays using the provided size information
    '''

    Vl, Vw = size[0], size[1] # helps with understanding the function
    
    LocalBuffer = []
    for x in range(0,len(data),Vw):
        LocalBuffer.append(data[x:x+Vw])
    
    try: # debugging
        assert len(LocalBuffer) == Vl
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

