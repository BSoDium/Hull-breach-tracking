from panda3d.core import *
import numpy as np
from Geometry import normalizer

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
        self.NormalTool = normalizer()
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
        (the vertices and primitives have been defined, but the node hasn't
        been created yet)
        ...
        nvm solved it
        '''

        PlateNode = GeomNode('gnode')
        PlateNode.addGeom(tempGeom)
        #PlateNodePath = render.attachNewNode(PlateNode)
        return PlateNode
    
    def GetPosData(self):
        '''
        Provides positional data for each vertex. Output format: LVecBase3f List
        '''
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

        return PosOutput[0] # format: 1D array, one sublist per encountered geom, each sublist contains LVecBase3f positional values (we only need the first and only geom)
    
    def GetNormalData(self):
        '''
        Provides normal data for each vertex. Output format: LVecBase3f List
        '''
        NormalOutput = []
        for i in range(self.GeomNode.getNumGeoms()):
            geom = self.GeomNode.getGeom(i)
            vdata = geom.getVertexData()
            normal = GeomVertexReader(vdata, "normal")
            vertex = GeomVertexReader(vdata, "vertex")

            BufferNormalList = []

            while not vertex.isAtEnd():
                vertex.getData3() # while condition toggling
                BufferNormalList.append(normal.getData3()) # a - sign is necessary
            
            NormalOutput.append(BufferNormalList)
        
        return NormalOutput[0] # there's only one geomNode, I created a list in case I need to add more stuff

    def deform(self,data): # data is the position map 
        geom = self.GeomNode.modifyGeom(0)
        vdata = geom.modifyVertexData()
        # prim = geom.modifyPrimitive(0) # not necessary here, could be usefull in any other situation tho
        vertexWriter = GeomVertexRewriter(vdata, 'vertex')

        for i in range(len(data)):
            assert (type(data[i][0]) == float and type(data[i][1]) == float and type(data[i][2]) == float)
            vertexWriter.setRow(i)
            vertexWriter.setData3f(data[i])

        output = self.NormalTool.compute_data(data, self.SizeData)
        self.NormalTool.blit_normals(output, geom) # apply changes
        return None # this function modifies the geomNode as a global var


array = GeomVertexArrayFormat()
array.addColumn("vertex",3,Geom.NTFloat32,Geom.CPoint)