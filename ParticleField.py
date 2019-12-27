from panda3d.core import * # needs to be improved later on (maybe)
from ProceduralGen import *
from copy import deepcopy

class ParticleMesh:
    
    def __init__(self,l,w,Vl,Vw,extraArgs):
        #is_wireframed = False
        '''
        ParticleMesh
        ===
        this is a particle array, it reacts to mechanical stresses.
        Arguments needed: lenght and width in 3d units, length and width in amount of vertices (the four must be ints).
        '''
        self.surface = RectangleSurface(l,w,Vl,Vw)
        return None

    def update(self,dt):
        # MODIFY THE SURFACE (somehow)
        CurrentState = self.surface.GetData() # still unused
        mesh = deepcopy(self.surface.GeomNode)

        CurrentState[0] = LVecBase3f(0,0,0.01) + CurrentState[0] # test
        self.surface.deform(CurrentState)
        
        return mesh
