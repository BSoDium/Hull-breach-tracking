import sys
try:
    from panda3d.core import *
    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
    from ParticleField import ParticleMesh
except:
    print('failed to load modules')
    sys.exit()

class mainApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.ParticleSystem = ParticleMesh(20,50,70,70,None)
        self.set_background_color(VBase3F(0,0,0))
        self.task_mgr.add(self.MainLoop,'ScreenUpdatingTask')
        return None
    def MainLoop(self,task):
        self.ParticleSystem.update()
        return None

Simulation = mainApp()
try:
    Simulation.run()
except:
    print("SystemExit successfull, running exception...")
    sys.exit(0) # avoid systemExit error