import sys,os
try:
    from panda3d.core import *
    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
    from ParticleField import ParticleMesh
    from DataSaveLib import DataSet
    from Gui import UserInterface
    from CommandLine import Console
except ModuleNotFoundError:
    ErrorMessage = 'failed to load modules'
    sys.exit(ErrorMessage)

try:
    from pypresence import Presence
    client_id = "664921802761306132"
    RPC = Presence(client_id)
    RPC.connect()
    RPC.update( state= "debugging: developer mode", 
                spectate= "watch", details= "build 05d4a")
except:
    print("[WAVE ENGINE]: failed to connect to discord RPC")
    pass

'''
try:
    os.system("pstats") # debug, you should comment these lines if you don't want the pstats window to pop up
except:
    pass
'''

sys.stdout = open('output.log', 'w') # debug

class mainApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # debugging 
        self.setFrameRateMeter(True)

        # core variables
        self.ParticleSystem = ParticleMesh(20,20,30,10,None) # default size and data (will be displayed when you first open the program)
        self.Memory = DataSet() # stores the simulation results
        self.Gui2d = UserInterface() # buttons and stuff
        
        # console
        self.UserConsole = Console()
        commandDic = {
            "test":self.ParticleSystem.override
        }
        self.UserConsole.create(commandDic)
        
        # these are the tasks that will be executed during the sim
        self.TaskList = [ # I know the syntax isn't easy...
            ["single_static", (10,4), (-3, -1.5, 0.3), [1,2]],
            #["single_following_sine", (4,1), (400,5,0,(0,0,1)), [0,100]],
            #["single_virtual", (4,5), [0,100]]
        ] 

        # lighting
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(0.9, 0.9, 1, 1))
        self.dlnp = render.attachNewNode(dlight)
        self.dlnp.setHpr(0, -60, 0)
        render.setLight(self.dlnp)

        self.set_background_color(VBase3F(0.1,0.1,0.1))

        # initiate computing sequence
        self.task_mgr.add(self.Compute,'ComputingTask')
        self.task_mgr.add(self.UpdateScene,'SceneUpdatingTask')

        self.SimState = 1 # current frame (when reading the precomputed data)

        # user variables
        self.SimLenght = 200 # frames
        self.dt = 0.001 # time step for the simulation (in seconds)
        
        # debug
        self.debug()
        return None


    def Compute(self,task): 
        '''
        [PRECOMPUTING LOOP]
        '''
        if task.frame < self.SimLenght:
            self.Memory.store(self.ParticleSystem.update(self.dt, self.TaskList, task.frame)) # add every the geometry of each frame to the memory, so we can display it later
            return task.cont
        else: # end of computing process
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
        self.Memory.unwrap(wireframe = True)
        
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
            self.SimState += 1
        else:
            print("done")
            return task.done

        return task.cont

    def UpdateScene(self,task): # troubleshooting
        foo = self.camera.getHpr()
        self.dlnp.setHpr(foo)
        return task.cont


    def debug(self):
        self.pstats = True # base inheritance
        PStatClient.connect()
        return None



if __name__=="__main__":
    Simulation = mainApp()
    try:
        Simulation.run()
    except SystemExit:
        print("SystemExit successfull, running exception...")
        sys.exit(0) # avoid annoying systemExit error

