from panda3d.core import *
import numpy as np

def TupleSum(args): # used in 
    '''
    concatenates tuples inside lists
    '''
    assert type(args) == list # just in case u were still wondering
    S=()
    for x in args:
        S+=x
    return S

class RectangleSurface:
    def __init__(self,l,w,Vl,Vw):
        self.GeomNode = self.create(Vl,Vw,l,w)
        #self.GeomNode.setRenderModeWireframe()
        self.SizeData = (l,w,Vl,Vw)
        return None

    def create(self,Vlenght,Vwidth,length,width):
        '''
        creates a triangulated rectangle
        '''
        VertexCount = Vlenght*Vwidth
        array = GeomVertexArrayFormat()
        array.add_column('vertex',3, Geom.NTFloat32, Geom.CPoint) # we'll work only with vertex coordinates rn, I don't want to mess with lighting and shit
        array.add_column('normal',3, Geom.NTFloat32, Geom.CNormal)
        # I'm leaving gaps because I still suck and I'm scared of getting lost
        format = GeomVertexFormat.getV3n3() # calling the format this way makes it already predefined
        LocalVdata = GeomVertexData('DynamicPlate', format, Geom.UH_static)
        LocalVdata.setNumRows(VertexCount)
        # some useless spacing again
        vertex = GeomVertexWriter(LocalVdata,'vertex')
        normal = GeomVertexWriter(LocalVdata,'normal')

        #LSpacing , WSpacing = length/Vlenght , width/Vwidth  # not necessary since we're using numpy to calculate coordinates
        LCoord , WCoord = np.linspace(-length/2,length/2,Vlenght) , np.linspace(-width/2,width/2,Vwidth)
        localZ = 0 # defines Z height of the plane (DynamicPlate)
        for x in LCoord:
            for y in WCoord:
                vertex.addData3f(x,y,localZ)
                normal.addData3d(0,0,-1) # initial vector
        # vertex data has been created, we still need the geomprimitives
        #GPrimList = [] 
        tempGeom = Geom(LocalVdata)
        for i in range(Vwidth-1):
            TempData = TupleSum([(x+i-1,x+i) for x in range(1,VertexCount,Vwidth)]) # this tuple contains the list of indexes for the vertices of each geomtristrip (one band at a time)
            
            '''
            primitive = GeomTristrips(Geom.UHStatic)
            for j in TempData:
                #assert j < LocalVdata.get_num_rows() # debug
                primitive.add_vertex(j)
            primitive.close_primitive()
            #GPrimList.append(primitive)
            tempGeom.add_primitive(primitive)
            '''
            # kinda long code for such a simple thing
            
            TempData = list(TempData)
            bufferData = list(tuple(TempData[:1]) + TupleSum([(TempData[x],TempData[x-1]) for x in range(2, len(TempData),2)]))
            if len(bufferData) != len(TempData):
                bufferData.append(TempData[len(TempData)-1])
            TempData = bufferData
            TempData = tuple(TempData)
            primitive = GeomTristrips(Geom.UHStatic)
            for j in TempData:
                primitive.add_vertex(j)
            primitive.close_primitive()
            tempGeom.add_primitive(primitive)    
            
        '''
        WARNING: FURTHER AUTOMATED NORMAL CALCULATION SHOULD BE INSERTED HERE 
        (the vertices and [primitives have been defined, but the node hasn't
        been created yet)
        '''

        PlateNode = GeomNode('gnode')
        PlateNode.addGeom(tempGeom)
        #PlateNodePath = render.attachNewNode(PlateNode)
        return PlateNode
    
    def GetData(self):
        # https://docs.panda3d.org/1.10/python/programming/internal-structures/other-manipulation/reading-existing-geometry#reading-existing-geometry-data
        PosOutput = [] # vertices
        for i in range(self.GeomNode.getNumGeoms()): # we know it only contains one in this particular algorithm
            geom = self.GeomNode.getGeom(i)
            #state = self.GeomNode.getGeomState(i) # unused variable (that's why I commented it)
            vdata = geom.getVertexData() # at this point we have all the positions stored here

            # creating readers
            vertex = GeomVertexReader(vdata, "vertex")

            # I need to transfer the positional data to the ouput list (one sublist per geom)
            BufferPosList = []
            
            # vertex scanning 
            while not vertex.isAtEnd():
                BufferPosList.append(vertex.getData3()) # stored data for this particular geom
            
            PosOutput.append(BufferPosList)

        return PosOutput[0] # format: two dimensionnal array, one sublist per encountered geom, each sublist contains LVecBase3f positional values (we only need the first and only geom)
    
    def deform(self,data): # data is the position map 
        # I will now replace the old geomvertexData according to the data scheme
        format = GeomVertexFormat.getV3n3() 
        vdata = GeomVertexData('DynamicPlate', format, Geom.UH_static)
        vdata.setNumRows(self.SizeData[2]*self.SizeData[3]) 
        vertex = GeomVertexWriter(vdata,'vertex')
        for x in data:
            vertex.addData3f(x)
        geom = self.surface.getGeom(0) # first and only one

        return None # should actually return the deformed geometry


def processGeomNode(): # I'm working on it
    return None

array = GeomVertexArrayFormat()
array.addColumn("vertex",3,Geom.NTFloat32,Geom.CPoint)