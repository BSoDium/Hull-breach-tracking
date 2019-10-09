from panda3d.core import *

class Generator:
    def __init__(self):
        # to do
        return None
    def create(figure,args):
        '''
        creates a procedurally generated model,
        the name of the model has to be given as the figure
        var
        '''
        # to do
        if figure == 'cube':
            array = GeomVertexArrayFormat()
            array.addColumn("vertex",3,Geom.NTFloat32,Geom.CPoint)
        return None
    def Create_Cube(self,args)

array = GeomVertexArrayFormat()
array.addColumn("vertex",3,Geom.NTFloat32,Geom.CPoint)