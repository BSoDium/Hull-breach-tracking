import sys,os
try:
    from panda3d.core import *
    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
    from ParticleField import ParticleMesh
    from DataSaveLib import DataSet
    from Gui import UserInterface
    from CommandLine import Console
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    ErrorMessage = 'failed to load modules'
    sys.exit(ErrorMessage)

try:
    from pypresence import Presence
    client_id = "664921802761306132"
    RPC = Presence(client_id)
    RPC.connect()
    RPC.update( state= "debugging: developer mode", 
                spectate= "watch", details= "build 05d4a", large_image = "logo2")
except:
    print("[WAVE ENGINE]: failed to connect to discord RPC")
    pass




sys.stdout = open('output.log', 'w') # debug

class mainApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # debugging 
        self.setFrameRateMeter(True)

        # core variables
        self.ParticleSystem = ParticleMesh(20,20,30,10,None) # default size and data (will be displayed when you first open the program)
        self.Memory = DataSet() # stores the simulation results
        self.Gui2d = UserInterface(False) # buttons and stuff
        
        # console
        self.UserConsole = Console()
        commandDic = {
            "recompute":undefined, # I still need to code those
            "addTask":undefined,
            "showActiveTasks":undefined,
            "removeTask":undefined,
            "toggleDebugMode":self.debug,
            "toggleFullscreen":self.Gui2d.toggleFullScreen,
            "Track":self.TrackMotion,
            "SetFrame":self.SetFrame,
            "GetFrame":self.GetFrame,
            "Play":self.Play,
            "Pause":self.Pause,
            "exit":stop
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
        self.using_pstats = False # by default, debug mode is off

        # initiate computing sequence
        self.task_mgr.add(self.Compute,'ComputingTask')
        self.task_mgr.add(self.UpdateScene,'SceneUpdatingTask')

        self.SimState = 1 # current frame (when reading the precomputed data)
        self.is_playing = False

        # user variables
        self.SimLenght = 200 # frames
        self.dt = 0.001 # time step for the simulation (in seconds)

        # user imput
        self.accept("f11", self.Gui2d.toggleFullScreen)
        
        return None


    def Compute(self,task): 
        '''
        [PRECOMPUTING LOOP]
        '''
        if task.frame < self.SimLenght:
            self.Memory.store(*self.ParticleSystem.update(self.dt, self.TaskList, task.frame)) # add every the geometry of each frame to the memory, so we can display it later
            return task.cont
        else: # end of computing process
            self.transition()
            return task.done
    
    def transition(self):
        '''
        should contain all of the gui stuff
        '''
        # debug
        self.UserConsole.ConsoleOutput("Computing process completed successfully")
        self.UserConsole.ConsoleOutput("Loading and displaying content...")
        self.UserConsole.ConsoleOutput("is_playing = %s" % self.is_playing)

        self.taskMgr.add(self.Display,'PostProcessingTask')
        self.Memory.unwrap(wireframe = True)
        
        return None

    def Display(self,task):
        '''
        [DISPLAYING LOOP]
        '''
        if self.SimState < self.SimLenght:
            if self.is_playing:
                try:
                    self.Memory.getFrameData(self.SimState-1).hide()
                except:
                    pass
                self.Memory.getFrameData(self.SimState).show()
                self.SimState += 1
        else:
            self.UserConsole.ConsoleOutput("done")
            self.is_playing = False
            return task.done

        return task.cont

    def UpdateScene(self,task): # troubleshooting
        foo = self.camera.getHpr()
        self.dlnp.setHpr(foo)
        return task.cont

    def SetFrame(self,frame):
        '''
        Warp to selected frame, and pause the displaying loop
        '''
        if frame > self.SimLenght or frame < 0:
            self.UserConsole.ConsoleOutput("Frame index out of range, could not perform operation")
            return IndexError
        # scene updating
        self.Memory.getFrameData(self.SimState).hide()
        self.Memory.getFrameData(frame).show()
        self.is_playing = False
        self.SimState = frame
    
    def GetFrame(self):
        self.UserConsole.ConsoleOutput("Currently displayed frame is %s out of %d" % (self.SimState,self.SimLenght))
    
    def Play(self):
        self.is_playing = True
        self.UserConsole.ConsoleOutput("Now Playing from frame %s" % self.SimState)
    
    def Pause(self):
        self.is_playing = False
        self.UserConsole.ConsoleOutput("Paused")
    
    def TrackMotion(self, 
                    StartingFrame, 
                    EndFrame, 
                    Xindex, 
                    Yindex,
                    datatype):
        '''
        Displays the requested data for one node in a matplotlib external window
        Xindex = width index
        Yindex = length index
        '''
        if StartingFrame >= EndFrame or StartingFrame < 0 or EndFrame > self.SimLenght :
            self.UserConsole.ConsoleOutput("Invalid frame index provided")
            return None # abort
        self.UserConsole.ConsoleOutput("Processing...")
        Pos = []
        Speed = []
        Accel = []
        for x in range(StartingFrame,EndFrame + 1):
            localPos = self.Memory.getFramePosData(x)[Yindex][Xindex]
            Pos.append(localPos)
            if datatype == 'speed' or datatype == 'Speed':
                if x - StartingFrame - 1 >=0:
                    Speed.append((localPos - Pos[x - StartingFrame - 1])/self.dt)
                else:
                    Speed.append(LVecBase3f(0,0,0))
                
            elif datatype == 'accel' or datatype == 'Accel':
                if x - StartingFrame - 1 >=0:
                    Speed.append((localPos - Pos[x - StartingFrame - 1])/self.dt)
                    Accel.append((Speed[x - StartingFrame] - Speed[x - StartingFrame - 1])/self.dt)
                else:
                    Speed.append(LVecBase3f(0,0,0))    
                    Accel.append(LVecBase3f(0,0,0))
                
        if datatype == 'speed' or datatype == 'Speed':
            plt.plot([self.dt*i for i in range(StartingFrame, EndFrame + 1)],
                        Speed)
        elif datatype == 'accel' or datatype == 'Accel':
            plt.plot([self.dt*i for i in range(StartingFrame, EndFrame + 1)],
                        Accel)
        elif datatype == 'pos' or datatype == 'Pos':
            plt.plot([self.dt*i for i in range(StartingFrame, EndFrame + 1)],
                        Pos)
        else:
            self.UserConsole.ConsoleOutput("Wrong datatype provided")
            return None
        plt.show()
        self.UserConsole.ConsoleOutput("Done")
        return None

    def debug(self):
        '''
        Toggles pstats task graph if available. If not, please make sure that pstats is installed on your machine, and execute it using cmd with the command 'pstats'
        '''
        try:
            if not self.using_pstats:
                PStatClient.connect()
                assert PStatClient.isConnected
                self.using_pstats = True
                portVar = ConfigVariableString('pstats-port')
                self.UserConsole.ConsoleOutput('Connected to pstats server at port %s' % portVar.getValue())
            else:
                PStatClient.disconnect()
                self.using_pstats = False
                self.UserConsole.ConsoleOutput('Disconnected from pstats server successfully')
        except:
            self.UserConsole.ConsoleOutput('Could not establish connection with pstats server')
        return None




def undefined():
    '''
    This function hasn't been implemented yet
    '''
    return NotImplemented

def stop():
    os._exit(0)
    
if __name__=="__main__":
    Simulation = mainApp()
    try:
        Simulation.run()
    except SystemExit:
        print("SystemExit successfull, running exception...")
        sys.exit(0) # avoid annoying systemExit error

