from panda3d.core import * # safety first

class normalizer:
    '''a normalizer object is an actual tool, it allows you to fully automate the normal calcultion process. It scans the model's 
    geomNodes, and for each vertex, calculates the normal of the adjacent surfaces, and get's the average normalized vector'''
    
    def __init__(self):
        return None
    
    def compute_data(self,data,size):
        n = len(data) # readability
        normalData = [LVecBase3f(0,0,0) for i in range(n)] # empty template
        length, width = size[2], size[3]

        for i in range(n): # i = (x-1)*width + y (x is the length index, y is the width index)
            # compute each normal
            if i%width and (i-1)%width and length-1 > i//width > 0: # border check
                scanlist = [
                    i - 1,
                    i - width -1,
                    i - width,
                    i + 1,
                    i + width + 1,
                    i + width
                ]
                normal = LVecBase3f(0,0,0)
                for x in scanlist:
                    try: # I'm lazy, I didn't want to fix the index issue so I solved it with a try except routine
                        normal += LVecBase3f(crossProd(
                            data[x-1] - data[i],
                            data[x] - data[i]
                        ))
                    except:
                        pass
                normalData[i] = normal
            else:
                normal = LVecBase3f(0,0,1)
                normalData[i] = normal
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