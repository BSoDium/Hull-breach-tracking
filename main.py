import sys,os
try:
    from panda3d.core import *
    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
    from ParticleField import ParticleMesh
    from DataSaveLib import DataSet
    from Gui import UserInterface
except:
    ErrorMessage = 'failed to load modules'
    sys.exit(ErrorMessage)

'''
try:
    os.system("pstats") # debug, you should comment these lines if you don't want the pstats window to pop up
except:
    pass
'''

class mainApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # core variables
        self.ParticleSystem = ParticleMesh(20,20,10,10,None)
        self.Memory = DataSet() # stores the simulation results
        self.Gui2d = UserInterface() # buttons and stuff

        # lighting
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(0.9, 0.9, 1, 1))
        self.dlnp = render.attachNewNode(dlight)
        self.dlnp.setHpr(0, -60, 0)
        render.setLight(self.dlnp)

        self.set_background_color(VBase3F(0.1,0.1,0.1))

        self.task_mgr.add(self.Compute,'ComputingTask')
        self.task_mgr.add(self.UpdateScene,'SceneUpdatingTask')

        self.SimState = 1 # current frame (when reading the precomputed data)
        self.SimLenght = 400
        self.dt = 0.001 # time step for the simulation (in seconds)
        
        # debug
        self.debug()
        return None


    def Compute(self,task): 
        '''
        [PRECOMPUTING LOOP]
        '''
        if task.frame < self.SimLenght:
            self.Memory.store(self.ParticleSystem.update(self.dt)) # add every the geometry of each frame to the memory, so we can display it later
            return task.cont
        else:
            self.transition()
            return task.done
    
    def transition(self):
        '''
        should contain all of the gui stuff
        '''
        # debug
        print("Computing process completed successfully")
        print("Loading and displaying content...")

        self.taskMgr.add(self.Display,'PostProcessingTask')
        self.Memory.unwrap()
        
        return None

    def Display(self,task):
        '''
        [DISPLAYING LOOP]
        '''
        if self.SimState < self.SimLenght:
            try:
                self.Memory.getFrameData(self.SimState-1).hide()
            except:
                pass
            self.Memory.getFrameData(self.SimState).show()
            self.SimState +=1

        return task.cont

    def UpdateScene(self,task): # troubleshooting
        foo = self.camera.getHpr()
        self.dlnp.setHpr(foo)
        return task.cont


    def debug(self):
        self.pstats = True # base inheritance
        PStatClient.connect()
        return None


'''
if __name__=="__main__":
    Simulation = mainApp()
    try:
        Simulation.run()
    except:
        print("SystemExit successfull, running exception...")
        sys.exit(0) # avoid annoying systemExit error

'''
Simulation = mainApp()
Simulation.run() # debug
