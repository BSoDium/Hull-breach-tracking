from panda3d.core import * # safety first

class normalizer:
    '''a normalizer object is an actual tool, it allows you to fully automate the normal calcultion process. It scans the model's 
    geomNodes, and for each vertex, calculates the normal of the adjacent surfaces, and get's the average normalized vector'''
    def __init__(self):
        return None