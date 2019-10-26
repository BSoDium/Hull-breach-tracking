from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

# this is a tutorial, and a test at the same time

class testApp(ShowBase):
    def __init__(self):
        self.doubleFaceTriangle()
        self.singleFaceRectangle(10,5,5,2.5,(0,0,0))
        return None
    
    def doubleFaceTriangle(self):
        ShowBase.__init__(self)

        # create an empty GeomVertexArrayFormat
        array = GeomVertexArrayFormat()
        # add 3 vertex columns
        array.addColumn("vertex", 3, Geom.NTFloat32, Geom.CPoint) # not sure what this does
        '''
        array.addColumn("texcoord",2,Geom.NTFloat32, Geom.CTexcoord)
        '''
        format  = GeomVertexFormat()
        format.addArray(array)
        format = GeomVertexFormat.registerFormat(format) # always register the format before using it

        #or you can use the single line definition:
        #format = GeomVertexFormat.getV3()
        
        vdata = GeomVertexData('MetalPlate',format, Geom.UHStatic)
        vdata.setNumRows(4) # specify the number of rows (points I guess)

        # now we need to create several geomvertexwriters
        # actually, I chose a formal that only requires the vertex geomvertexwriter
        vertex = GeomVertexWriter(vdata, 'vertex')
        '''
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        '''

        vertex.addData3f(1, 0, 1)
        vertex.addData3f(1,1,0)
        vertex.addData3f(0,1,0)
        vertex.addData3f(0,0,0)

        # now we need to create the GeomPrimitive "guideline(s)"
        Gprimup, Gprimdwn= GeomTriangles(Geom.UHStatic), GeomTriangles(Geom.UHStatic)
        Gprimup.addVertices(0,1,2)
        Gprimdwn.addVertices(2,1,0)

        # let's actually add this triangle to the scene graph
        # we need to create a geom at first
        tempGeom = Geom(vdata)
        tempGeom.add_primitive(Gprimup)
        tempGeom.add_primitive(Gprimdwn)
        node = GeomNode('gnode')
        node.addGeom(tempGeom)

        OutputNodePath = render.attachNewNode(node)



        return None
    
    def singleFaceRectangle(self,Vlenght,Vwidth,length,width,cornercoord):
        array = GeomVertexArrayFormat()
        array.add_column('vertex',3, Geom.NTFloat32, Geom.CPoint)
        return None
    
    def actualLoop(self,task):
        return None
    
test = testApp()
test.run()