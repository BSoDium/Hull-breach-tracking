from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

# this is a tutorial, and a test at the same time

class testApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # create an empty GeomVertexArrayFormat
        array = GeomVertexArrayFormat()
        # add 3 vertex columns
        array.addColumn("vertex", 3, Geom.NTFloat32, Geom.CPoint)

        format = GeomVertexFormat.getV3n3cpt2()
        vdata = GeomVertexData('MetalPlate',format,Geom.UHStatic)
        vdata.setNumRows(4)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')

        vertex.addData3f(1, 0, 0)
        vertex.addData3f(1,1,0)
        vertex.addData3f(0,1,0)
        vertex.addData3f(0,0,0)

        color.addData4f(1,1,1,1)


        # insert code here


        return None
    def actualLoop(self,task):
        return None
    
test = testApp()
test.run()