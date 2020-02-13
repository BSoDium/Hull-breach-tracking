from panda3d.core import *
from copy import deepcopy
from Geometry import crossProd

class engine:
    def __init__(self): 
        self.Id = "metal_softbody - 4pernode_harmosc" # not sure about the syntax yet
        self.attributes = {
            "rigidconst":10, # kg/m
            "nodemass":0.1, # kg usi
            "fictionalradius":0.01, # m

        }
        self.size = None

        self.LastPos = None # local buffer
        
        return None

    def bake(self, PosData, 
                NodeGeometry, 
                SpeedState, 
                AccelState, 
                TimeShift ):
        
        try:
            assert len(self.size) == 2 # debug
        except:
            print("Please provide correct table size data before computing physics")
            return 1

        MainPosBuffer = deepcopy(LinArrayFormat(PosData, self.size)) # we will only modify the buffer\
        MainNodeGeomBuffer = deepcopy(NodeGeometry)
        MainSpeedBuffer = deepcopy(SpeedState)
        MainAccelBuffer = deepcopy(AccelState)

        self.LastPos = MainPosBuffer # save last known position as engine data (used for BDF)
        
        length, width = len(MainPosBuffer), len(MainPosBuffer[0])

        ''' 
        JointTable = [] # Le systeme que l'on etudie est en realite la table des liens (nommes "joints")
        # je suis obligé de construire la table explicitement (organisation non lineaire trop complexe a gerer)
        for y in range(2*length - 1):
            Line = []
            for x in range(width - (y+1)%2):
                if not y%2: # even y ie we're creating a horizontal joint (width of them actually)
                    #print("horizal")
                    Line.append(HarmoscLink((y//2,x),
                                            (y//2,x+1),
                                            self.attributes['rigidconst'], 
                                            MainPosBuffer))
                else: # vertical joint, odd y 
                    #print("vertical")
                    Line.append(HarmoscLink((y//2,x),
                                            (y//2+1,x),
                                            self.attributes['rigidconst'],
                                            MainPosBuffer))
            JointTable.append(Line)
        # done
        ''' # en fait non tout ça ne sert a rien, 1h de debugging pour rien p*tain


        for l in range(length): # actually len(MainPosBuffer) = length
            for w in range(width):
                pos = Vec3(MainPosBuffer[l][w]) # convert to vec3 for easier vector manipulation
                speed = Vec3(MainSpeedBuffer[l][w])
                accel = Vec3(MainAccelBuffer[l][w])
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
                    if 0 < a < width and 0 < b < length: # side limit
                        ReferenceNormal = NodeGeometry[0] # la normale qui reste constante et montre l'orientation du noeud
                        RestingAngle = NodeGeometry[x+1] # +1 because of the reference normal at the begining of the list

                        CurrentJointVector = Vec3(MainPosBuffer[b][a]) - pos
                        CurrentAngle = CurrentJointVector.normalized().angleDeg(ReferenceNormal.normalized())

                        delta = RestingAngle - CurrentAngle # ecart
                        TorqueVect = Vec3(crossProd(ReferenceNormal,CurrentJointVector)).normalized()
                        resultingTorque = TorqueVect * self.attributes['rigidconst'] * delta   # a partir de la mes calculs sont plus qu'approximatifs 
                        
                        JointLength = CurrentJointVector.length()
                        AppliedForce += resultingTorque/JointLength # physique a deux balles
                
                methods = {
                    "euler":NextPos_Euler,
                    "verlet":NextPos_Verlet
                }

                # we will be using euler at first
                procedure = methods['euler']

                MainAccelBuffer[l][w], MainSpeedBuffer[l][w], MainPosBuffer[l][w] = procedure(AppliedForce, 
                                                                                                self.attributes['nodemass'],
                                                                                                pos,
                                                                                                speed,
                                                                                                TimeShift)

                

        
        
        return ArrayLinFormat(MainPosBuffer), MainSpeedBuffer, MainAccelBuffer # currently does nothing sry

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