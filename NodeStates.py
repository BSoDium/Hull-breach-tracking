from panda3d.core import Vec3
from direct.showbase.ShowBase import ShowBase # unused
from math import pi, sin
import random

# MAIN CLASS STATE

class State:
    def __init__(self,
                rule,
                coord: Vec3 = Vec3(0,0,0),
                followingFunc: str = "",
                FuncSettings: list = [1, 1, 0, Vec3(0,0,1)] ):
        '''
        rule: "free", "static", "following", "virtual"
        coord: Vec3(x,y,z)
        followingFunc: "sine", "binary", "linearSpikes", "noise"
        FuncSettings: Amplitude (3d unit), frequency (Hz), phase shift (s), orientation vector (Vec3 object)
        '''
        self.RuleTable = {
        "free":free,
        "static":static,
        "following":following,
        "virtual":virtual
        }

        self.setRule(rule, coord = coord, followingFunc = followingFunc, FuncSettings = FuncSettings)

        return None

    def setRule(self,
                rule,
                coord: Vec3 = Vec3(0,0,0),
                followingFunc: str = "",
                FuncSettings: list = [1, 1, 0, Vec3(0,0,1)] ):
        
        self.usePhysics = (rule == "free" or rule == "virtual")
        try: 
            self.method = self.RuleTable[rule](coord, followingFunc, FuncSettings)
        except:
            self.method = None
            raise NotImplementedError
        
        return None
    
    def getRule(self):
        try:
            return self.method
        except NameError:
            return "No rule defined"
    
    def getPos(self, frame, pt0):
        if self.usePhysics:
            return "Unable to handle 'free' or 'virtual' node, calculation must be made by the engine"
        else:
            return self.method.getPos(frame, pt0)

# NODE STATES

class free(State):
    def __init__(self, *args):
        # empty class
        pass
    
    def getPos(self, frame, *args):
        return None
    
class static(State):
    def __init__(self, coord, *args):
        self.coord = coord
        return None

    def getPos(self, frame, *args):
        return self.coord

class following(State):
    def __init__(self, coord, func, Settings, *args):
        self.FollowingTable = {
        "sine":DynSine,
        "binary":DynBin,
        "linearSpikes":DynLin,
        "noise":DynNoise
        }
        
        self.Settings = Settings # actually it doesn't make any sense to save the settings as they get resetted every frame
        try:
            self.func = self.FollowingTable[func]
        except:
            self.func = None 
            raise NotImplementedError

        return None

    def getPos(self, frame, Pt0): # Pt0 = position at t=0
        return self.func(self.Settings[0], self.Settings[3].normalized(), Pt0, self.Settings[1], self.Settings[2], frame)

class virtual(State):
    def __init__(self, *args):
        # empty class
        pass
    
    def getPos(self, frame, *args):
        return None


# FOLLOWING FUNCTIONS


def DynSine(A, vect, pt0, f, delta, t): # vect must be normalized
    omega = 2*pi*f
    phi = -delta * omega
    output = A*sin(omega*t + phi)
    return vect*output + pt0 # vector projection

def DynBin(A, vect, pt0, f, phi, t):
    raise NotImplementedError
    #return vect*output

def DynLin(A, vect, pt0, f, phi, t):
    raise NotImplementedError
    #return vect*output

def DynNoise(A, vect, pt0, *args): # *args allows us to avoid extra args errors
    output = ((-1)**random.randint(0,1))*A*random.random() # generates a number between -A and A
    return vect*output + pt0

