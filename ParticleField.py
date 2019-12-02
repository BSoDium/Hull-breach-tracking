from panda3d.core import * # needs to be improved later on (maybe)
from ProceduralGen import *

class ParticleMesh:
    
    def __init__(self,l,w,Vl,Vw,extraArgs):
        is_wireframed = False
        '''
        ParticleMesh
        ===
        this is a particle array, it reacts to stress, or other kinds of mechanical stresses.
        Arguments needed: lenght and width in 3d units, length and width in amount of vertices (the four must be ints).
        '''
        self.surface = RectangleSurface(l,w,Vl,Vw,is_wireframed)
        return None

    def update(self,dt):
        mesh = self.surface
        return mesh