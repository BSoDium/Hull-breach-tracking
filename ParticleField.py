from panda3d.core import * # needs to be improved later on (maybe)
from ProceduralGen import *
from copy import deepcopy
from physX import engine

class ParticleMesh:
    
    def __init__(self,l,w,Vl,Vw,extraArgs):
        '''
        ParticleMesh
        ===
        this is a particle array, it reacts to mechanical stresses.
        Arguments needed: lenght and width in 3d units, length and width in amount of vertices (the four must be ints).
        '''
        self.surface = RectangleSurface(l,w,Vl,Vw)
        self.engine = engine(self.surface.GetNormalData()) # initialize with RNS
        self.engine.SetSize(Vl,Vw)
        return None

    def update(self,dt):
        # MODIFY THE SURFACE (somehow)
        CurrentState = self.surface.GetPosData()
        NormalState = self.surface.GetNormalData() # unfinished

        NextState = self.engine.bake(CurrentState, NormalState, dt)
        self.surface.deform(NextState) # modifies the mesh and calculates the normals accordingly

        mesh = deepcopy(self.surface.GeomNode) # copy after it has been modified
        return mesh
