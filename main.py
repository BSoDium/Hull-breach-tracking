import sys
try:
    from panda3d.core import *
    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
    from ParticleField import ParticleMesh
    from DataSaveLib import DataSet
    from Gui import UserInterface
except:
    print('failed to load modules')
    sys.exit()




class mainApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # core variables
        self.ParticleSystem = ParticleMesh(20,20,10,10,None)
        self.Memory = DataSet() # stores the simulation results
        self.Gui2d = UserInterface() # buttons and stuff

        # ligting
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(0.9, 0.9, 1, 1))
        self.dlnp = render.attachNewNode(dlight)
        self.dlnp.setHpr(0, -60, 0)
        render.setLight(self.dlnp)

        self.set_background_color(VBase3F(0.1,0.1,0.1))
        self.task_mgr.add(self.Compute,'ComputingTask')
        self.dt = 0.001 # time step for the simulation (in seconds)
        return None

    def Compute(self,task):
        self.Memory.store(self.ParticleSystem.update(self.dt)) # add every the geometry of each frame to the memory, so we can display it later
        return task.cont


Simulation = mainApp()
try:
    Simulation.run()
except:
    print("SystemExit successfull, running exception...")
    sys.exit(0) # avoid annoying systemExit error

if __name__ == "__main__":
    pass # temporary