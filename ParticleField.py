from panda3d.core import * # needs to be improved later on (maybe)
from ProceduralGen import *

class ParticleMesh:
    def __init__(self,l,w,Vl,Vw,extraArgs):
        '''
        ParticleMesh
        ===
        this is a particle array, it reacts to stress, or other kinds of mechanical stress.
        Arguments needed: lenght and width in 3d units, length and width in amount of vertices (the four must be ints).
        '''
        self.surface = Generator(l,w,Vl,Vw) 
        return None

    def update(self):
        # updating function
        return None