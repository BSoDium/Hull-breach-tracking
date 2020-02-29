from panda3d.core import Vec3, LVecBase3f
from copy import deepcopy
from Geometry import crossProd
from math import isinf, cos, sin, pi

class engine:
    def __init__(self): 
        self.Id = "metal_softbody - 4pernode_harmosc" # not sure about the syntax yet
        self.attributes = {
            "angularRigidconst":10, # kg/m
            "linearRigidconst":5,
            "nodemass":0.1, # kg usi
            "friction":1

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

                            # CALCUL DE LA FORCE GENEREE PAR L'ANGLE DE TORSION
                            ReferenceNormal = NodeGeometry[0] # la normale qui reste constante et montre l'orientation du noeud
                            RestingAngle = NodeGeometry[x+1] # +1 because of the reference normal at the begining of the list

                            CurrentJointVector = Vec3(MainPosBuffer[b][a]) - pos
                            CurrentAngle = CurrentJointVector.normalized().angleDeg(ReferenceNormal.normalized())
                            

                            delta = CurrentAngle - RestingAngle # ecart
                            TorqueVect = Vec3(crossProd(CurrentJointVector, ReferenceNormal)).normalized()
                            resultingTorque = TorqueVect * self.attributes['angularRigidconst'] * delta   # a partir de la mes calculs sont plus qu'approximatifs 
                        
                            JointLength = CurrentJointVector.length()
                            AppliedForce += Vec3(crossProd(resultingTorque, -CurrentJointVector)).normalized() * (resultingTorque.length()/JointLength)  # physique a deux balles

                            # AJOUT DE LA FORCE TRANSMISE PAR LES LIENS RIGIDES
                            '''
                            CurrentJointVector *= -1
                            print("pos = ", MainPosBuffer[b][a])
                            print("AppliedForce = ",AppliedForce)
                            print("accel = ", MainLinAccelBuffer[b][a])
                            tempForce = MainLinAccelBuffer[b][a] * self.attributes['nodemass']
                            projectionAngle = CurrentJointVector.normalized().angleRad(tempForce.normalized())
                            if projectionAngle <= pi/2:
                                sign = 1
                            else:
                                sign = -1
                            projection = CurrentJointVector.normalized() * tempForce.length() * cos(projectionAngle) * sign
                            
                            print("projection = ", projection)
                            AppliedForce -= projection*0.0001 # coefficient obligatoire pour pouvoir observer les effets du bug de transmission

                            if isinf(tempForce.length()):
                                raise TypeError
                            '''
                            # AJOUT DE L'ASSERVISSEMENT DE DISTANCE
                            

                    methods = {
                        "euler":NextPos_Euler,
                        "verlet":NextPos_Verlet
                    }

                    # we will be using euler at first
                    procedure = methods['euler']

                    MainLinAccelBuffer[l][w], MainLinSpeedBuffer[l][w], MainPosBuffer[l][w] = procedure(AppliedForce, 
                                                                                                    self.attributes['nodemass'],
                                                                                                    pos,
                                                                                                    speed*self.attributes["friction"],
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


class HarmoscLink(engine): # turns out to be useless
    def __init__(self, index1, index2, rgdCoef, MainPosBuffer):
        self.Index2d = (index1, index2)
        self.pos = (MainPosBuffer[index1[0]][index1[1]] + MainPosBuffer[index2[0]][index2[1]]) / 2 # point median
        self.destroyed = False # may be changed at some point during the sim
        self.RigidCoef = rgdCoef
        self.vector = None # currently unused

        return None

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
    Converts vertex 2d lists to 3d arrays using the provided size information
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