from panda3d.core import * # safety first
from numpy import sqrt

class normalizer:
    '''a normalizer object is an actual tool, it allows you to fully automate the normal calcultion process. It scans the model's 
    geomNodes, and for each vertex, calculates the normal of the adjacent surfaces, and get's the average normalized vector'''
    
    def __init__(self):
        return None
    
    def compute_data(self,data,size):
        '''
        computes the normals for the array define by the provided data
        '''
        n = len(data) # readability

        normalData = [LVecBase3f(0,0,1) for i in range(n)] # empty template
        length, width = size[2], size[3]

        # convert list to array
        buffer = [data[i*width:
                    (i+1)*width ] for i in range(length)]

        for i in range(length):
            for j in range(width):
                scanlist = [
                    (i , j+1),
                    (i-1 , j),
                    (i , j-1),
                    (i+1 , j), # only use the 4 closest vertices because cmon it's easier 
                ]
                normal = LVecBase3f(0,0,0)
                for a in range(len(scanlist)):
                    if 0 <= scanlist[a][0] < length and 0 <= scanlist[a][1] < width and 0 <= scanlist[a-1][0] < length and 0 <= scanlist[a-1][1] < width:
                        previous, current = scanlist[a-1], scanlist[a]
                        normal += LVecBase3f(
                            crossProd(
                                buffer[ previous[0] ][ previous[1]] - buffer[i][j],
                                buffer[ current[0] ][ current[1] ] - buffer[i][j]
                            )
                        )
                normalData[ (i-1)*width + j] = LVecBase3f(Vec3(normal).normalized())
        
        return normalData
    
    def blit_normals(self,normalData,geom):
        vdata = geom.modifyVertexData()
        vertex = GeomVertexReader(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')

        i = 0
        while not vertex.isAtEnd():
            v = vertex.getData3f()
            normal.setData3f(normalData[i])
            i+=1
        
        return None

def crossProd(vectA, vectB):
    output = [
        vectA[1]*vectB[2] - vectA[2]*vectB[1],
        vectA[2]*vectB[0] - vectA[0]*vectB[2],
        vectA[0]*vectB[1] - vectA[1]*vectB[0]
    ]
    return tuple(output) # easier LVecBase3f conversion

def normalize(vect): # unused
    norm = sqrt(vect[0]**2 + vect[1]**2 + vect[2]**2)
    output = LVecBase3f((
        abs(vect[0]),
        abs(vect[1]),
        abs(vect[2])
        ))
    output /= norm
    return output