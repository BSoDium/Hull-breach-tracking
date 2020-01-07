from panda3d.core import *
from copy import deepcopy

class engine:
    def __init__(self, RNS): 
        '''
        The RNS is the reference normal state, it will be used later to determine
        the point where deformation becomes platic, and the springs don't come back
        to their initial state
        '''
        self.Id = "metal_softbody - 4pernode_harmosc" # not sure about the syntax yet
        self.attributes = {
            "rigidconst":10, # kg/m
            "nodemass":0.1, # kg usi

        }
        self.size = None
        self.ReferenceNormalState = RNS # store it so we can use it later
        return None
    
    def bake(self, PosData, NormalState, TimeShift):
        
        try:
            assert len(self.size)==2
        except:
            print("Please provide correct table size data before computing physics")
            return 1

        MainBuffer = deepcopy(LinArrayFormat(PosData, self.size)) # we will only modify the buffer
        
        
        
        return ArrayLinFormat(MainBuffer) # currently does nothing sry

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

class HarmoscNode:
    def __init__(self, index, mass):
        self.Index2d = index
        self.movable = True # may be changed at some point during the sim
        self.mass = mass

        return None

# engine procedures come next

def Bdf(): # not done yet
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