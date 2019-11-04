from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from PIL import Image
import numpy as np # first time I'm using that crappy lib for game dev
import sys

# this is a tutorial, and a test at the same time

# tuple(L[:1])+TupleSum([(L[x],L[x-1]) for x in range(2,len(L),2)])

loadPrcFileData('','window-title procedural_gen beta')

def TupleSum(args):
    '''
    concatenates tuples inside lists
    '''
    assert type(args) == list # just in case u were still wondering
    S=()
    for x in args:
        S+=x
    return S


class testApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        #self.doubleFaceTriangle()
        im = Image.open('voronoi_output01.png', 'r')
        self.imageMode = im.mode
        #im = Image.open('estuaire gironde nord Height Map (ASTER 30m).png','r')
        zArray = im.getdata()
        IMwidth, IMheight = im.size
        self.doubleFacedRectangle(IMwidth,IMheight,400,400,(0,0,0),zArray)
        self.set_background_color(VBase3F(0,0,0))
        #self.CreateSomeLighting()
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
        
        vdata = GeomVertexData('triangle',format, Geom.UHStatic)
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
    
    def doubleFacedRectangle(self,Vlenght,Vwidth,length,width,cornercoord,zArray): 
        '''
        creates a triangulated rectangle 
        '''
        VertexCount = Vlenght*Vwidth 
        array = GeomVertexArrayFormat()
        array.add_column('vertex',3, Geom.NTFloat32, Geom.CPoint) # we'll work only with vertex coordinates rn, I don't want to mess with lighting and shit
        # I'm leaving gaps because I still suck and I'm scared of getting lost
        format = GeomVertexFormat.getV3() # calling the format this way makes it already predefined
        LocalVdata = GeomVertexData('DynamicPlate',format,Geom.UH_static)
        LocalVdata.setNumRows(VertexCount)
        # some useless spacing again
        vertex = GeomVertexWriter(LocalVdata,'vertex')

        #LSpacing , WSpacing = length/Vlenght , width/Vwidth  # not necessary since we're using numpy to calculate coordinates
        LCoord , WCoord = np.linspace(-length/2,length/2,Vlenght) , np.linspace(-width/2,width/2,Vwidth)
        localZ = 0 # defines Z height of the plane (DynamicPlate)
        for x in range(len(LCoord)):
            for y in range(len(WCoord)):
                if self.imageMode == "I":
                    localZ = -(zArray.getpixel((x,y))-1000)/1000 # 1000 means above water level
                elif self.imageMode == "RGBA":
                    localZ = zArray.getpixel((x,y))[0]/255 # between 0 and 1
                vertex.addData3f(LCoord[x],WCoord[y],localZ)
        # vertex data has been created, we still need the geomprimitives
        #GPrimList = [] 
        tempGeom = Geom(LocalVdata)
        for i in range(Vwidth-1):
            TempData = TupleSum([(x+i-1,x+i) for x in range(1,VertexCount,Vwidth)]) # this tuple contains the list of indexes for the vertices of each geomtristrip (one band at a time)
            primitive = GeomTristrips(Geom.UHStatic)
            for j in TempData:
                #assert j < LocalVdata.get_num_rows() # debug
                primitive.add_vertex(j)
            primitive.close_primitive()
            #GPrimList.append(primitive)
            tempGeom.add_primitive(primitive)
            
            # kinda long code for such a simple thing
            TempData = list(TempData)
            bufferData = list(tuple(TempData[:1])+TupleSum([(TempData[x],TempData[x-1]) for x in range(2,len(TempData),2)]))
            if len(bufferData) != len(TempData):
                bufferData.append(TempData[len(TempData)-1])
            TempData = bufferData
            TempData = tuple(TempData)
            primitive = GeomTristrips(Geom.UHStatic)
            for j in TempData:
                primitive.add_vertex(j)
            primitive.close_primitive()
            tempGeom.add_primitive(primitive)
            
            
        node = GeomNode('gnode')
        node.addGeom(tempGeom)
        PlateNodePath = render.attachNewNode(node)
        PlateNodePath.setRenderModeWireframe()
        PlateNodePath.setPos(0,0,0)
        PlateNodePath.setHpr(0,180,0)
        return None
    
    def CreateSomeLighting(self): # useless as we didn't define any normals on our meshes
        plight = PointLight('plight01')
        plight.setColor(VBase4(0.5,1,1,1))
        plight.setAttenuation((0, 0, 1))
        plnp = render.attachNewNode(plight)
        plnp.setPos(0, 20, 1)
        render.setLight(plnp)
        return None

    def actualLoop(self,task):
        pass
        return None
    
test = testApp()
try:
    test.run()
except:
    print("SystemExit successfull, running exception...")
    sys.exit(0) # avoid systemExit error