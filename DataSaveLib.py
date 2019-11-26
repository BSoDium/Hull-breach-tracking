from panda3d.core import *

class DataSet:
    def __init__(self):
        self.time = float(0.0)
        self.RawData = [] # stores the meshes from each frame
        self.buffer = None
        return None
    
    def append(self,Node):
        self.RawData.append(Node)
        return None
    
    def insert(self,Node,index):
        return None
    
