from panda3d.core import *
from copy import deepcopy

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

    def bake(self, PosData, NormalState, SpeedState, TimeShift):
        
        try:
            assert len(self.size)==2
        except:
            print("Please provide correct table size data before computing physics")
            return 1

        MainPosBuffer = deepcopy(LinArrayFormat(PosData, self.size)) # we will only modify the buffer\
        MainNormalBuffer = deepcopy(NormalState)
        MainSpeedBuffer = deepcopy(SpeedState)

        self.LastPos = MainPosBuffer # update last known position (used for Bdf)
        
        length, width = len(MainPosBuffer), len(MainPosBuffer[0])

        for l in range(length): # actually len(MainPosBuffer) = length
            for w in range(width):
                pos = Vec3(MainPosBuffer[l][w]) # convert to vec3 for easier vector manipulation
                speed = Vec3(MainSpeedBuffer[l][w])
                normals = []
                for x in MainNormalBuffer[l][w][1:]:
                    try:
                        normals.append(Vec3(x))
                    except:
                        normals.append(None)

                AppliedForce = Vec3(0, 0, 0)

                neighbours = [
                            (w+1,l),
                    (w,l-1),        (w-1,l),
                            (w,l+1)
                ]

                for x in range(4):
                    a,b = neighbours[x]
                    if 0 < a < width and 0 < b < length:
                        RestingJointVector = normals[x] 
                        CurrentJointVector = Vec3(MainPosBuffer[b][a]) - pos
                        angle = RestingJointVector.normalized().angleDeg(CurrentJointVector.normalized())
                        resultingTorque = self.attributes['rigidconst'] * angle


                

        
        
        return ArrayLinFormat(MainPosBuffer), MainSpeedBuffer, MainNormalBuffer # currently does nothing sry

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


class HarmoscLink(engine): 
    def __init__(self, index1, index2, rgdCoef):
        self.Index2d = (index1, index2)
        self.destroyed = False # may be changed at some point during the sim
        self.RigidCoef = rgdCoef
        self.vector = None # currently unused

        return None

# engine procedures come next

def Bdf(): # not done yet
    return None


def NextPos_Verlet():

    return None

def NextPos_Euler():

    return None

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