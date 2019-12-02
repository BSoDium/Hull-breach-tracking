from panda3d.core import *
import numpy as np

def TupleSum(args):
    '''
    concatenates tuples inside lists
    '''
    assert type(args) == list # just in case u were still wondering
    S=()
    for x in args:
        S+=x
    return S

class RectangleSurface:
    def __init__(self,l,w,Vl,Vw,wireframe):
        self.GeomNode = self.create(Vl,Vw,l,w)
        self.GeomNode = render.attachNewNode(self.GeomNode)
        if wireframe:
            self.GeomNode.setRenderModeWireframe()
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
                normal.addData3d(0,0,-1)
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
            '''
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
            '''

        PlateNode = GeomNode('gnode')
        PlateNode.addGeom(tempGeom)
        #PlateNodePath = render.attachNewNode(PlateNode)
        return PlateNode

array = GeomVertexArrayFormat()
array.addColumn("vertex",3,Geom.NTFloat32,Geom.CPoint)
