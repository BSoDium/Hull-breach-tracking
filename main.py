import sys,os
try:
    from panda3d.core import *
    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
    from ParticleField import ParticleMesh
    from DataSaveLib import DataSet
    from Gui import UserInterface
    from pconsole import Console
    import matplotlib.pyplot as plt
    import matplotlib
    from direct.stdpy import threading
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



MAINDIR = Filename.from_os_specific(os.path.abspath(sys.path[0])).getFullpath()
sys.stdout = open('output.log', 'w') # debug

class mainApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # debugging 
        self.setFrameRateMeter(True)
        self.frameRateMeter.setFont(loader.loadFont(MAINDIR+'/assets/fonts/terminus-ttf-4.47.0/TerminusTTF-4.47.0.ttf'))
        self.axis = loader.loadModel(MAINDIR+'/assets/meshes/axis.egg')
        self.axis.reparentTo(render)
        self.axis.setScale(2)

        # core variables
        self.ParticleSystem = ParticleMesh(20,20,30,10,None) # default size and data (will be displayed when you first open the program)
        self.Memory = DataSet() # stores the simulation results
        self.Gui2d = UserInterface(False) # buttons and stuff
        
        # console
        self.UserConsole = Console()
        commandDic = {
            "recompute":undefined, # I still need to code those
            "addTask":self.addTask,
            "showActiveTasks":self.showActiveTasks,
            "removeTask":self.delTask,
            "highlight":undefined,
            "toggleDebugMode":undefined,
            "toggleFullscreen":self.Gui2d.toggleFullScreen,
            "toggleIndicators":undefined,
            "track":self.init_ThreadGraph,
            "setFrame":self.SetFrame,
            "getFrame":self.GetFrame,
            "pstats":self.pstats,
            "play":self.Play,
            "pause":self.Pause,
            "exit":stop,
            "progressbar":self.progressBarDemo
        }
        self.UserConsole.create(commandDic, app = self)
        
        # these are the tasks that will be executed during the sim
        self.TaskList = [ # I know the syntax isn't easy...
            ["single_static", (10,4), (-3, -1.5, 0.3), (2,100)],
            #["single_following_sine", (4,1), (400,5,0,(0,0,1)), [0,100]],
            #["single_virtual", (4,5), [0,100]]
        ] 
        '''
        ----------- More details on the PhysXTask syntax -----------
        there are three types of tasks: single, line, column
        -- Details:
        - a single task overrides the position of only one node. This particular
        physXNode will not be simulated as a physical object, and will move according to
        the applied rule and/or law
        - a line or column override does the same thing, but on an entire line/column
        
        three possible behavior/rules: static, following, virtual
        -- Details:
        - a static rule keeps the node in place, other nodes can however still interact with 
        the static node
        - a following rule forces the node to follow a law of evolution in 3d space
        - a virtual rule 'destroys' it, therefore there will be absolutely 
        no interaction between the node and its environnement

        the following rule requires a third argument, which is the followed law/function. 
        atm, only the sine function has been implemented

        ----------- Actually writing this down -----------
        ['single_static', (LineCoord, ColumnCoord), (x, y, z), (StartingFrame, EndingFrame)]
        ['line_static', (LineCoord), (center_x, center_y, center_z), (StartingFrame, EndingFrame)]
        ['column_static', (ColumnCoord), (center_x, center_y, center_z), (StartingFrame, EndingFrame)]
        ['single_following_sine', (LineCoord, ColumnCoord), ()]

        '''
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

        # chart display threading
        self.chart_thread = None
        self.opened_charts = 0

        # user variables
        self.SimLenght = 100 # frames
        self.dt = 0.01 # time step for the simulation (in seconds)

        # user imput
        self.accept("f11", self.Gui2d.toggleFullScreen)
        
        return None


    def Compute(self,task): 
        '''
        [PRECOMPUTING LOOP]
        '''
        if task.frame < self.SimLenght:
            self.Memory.store(*self.ParticleSystem.update(self.dt, self.TaskList, task.frame, self.Memory)) # add every the geometry of each frame to the memory, so we can display it later
            return task.cont
        else: # end of computing process
            self.transition()
            return task.done
    
    def transition(self):
        '''
        should contain all of the gui stuff
        '''
        # debug
        self.UserConsole.ConsoleOutput("Computing process completed successfully", color=(0,1,0,1))
        self.UserConsole.ConsoleOutput("Loading and displaying content...")
        self.UserConsole.ConsoleOutput("is_playing = %s" % self.is_playing)

        self.taskMgr.add(self.Display,'PostProcessingTask')
        self.Memory.unwrap(wireframe = True)
        
        return None

    def Display(self,task):
        '''
        [DISPLAYING LOOP]
        '''
        if self.SimState <= self.SimLenght:
            if self.is_playing:
                try:
                    self.Memory.getFrameData(self.SimState-1).hide()
                except:
                    pass
                self.Memory.getFrameData(self.SimState).show()
                self.SimState += 1
        else:
            self.SimState -= 1 # necessary if we want to know the actual displayed frame
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
        if frame > self.SimLenght or frame <= 0:
            self.UserConsole.ConsoleOutput("Frame index out of range, could not perform operation", (1,0,0,1))
            return IndexError
        # scene updating
        self.Memory.getFrameData(self.SimState).hide()
        self.Memory.getFrameData(frame).show()
        self.is_playing = False
        self.SimState = frame
    
    def GetFrame(self):
        '''
        outputs the current frame (the one displayed on screen atm)
        '''
        self.UserConsole.ConsoleOutput("Currently displayed frame is %s out of %d" % (self.SimState,self.SimLenght))
    
    def Play(self):
        if not self.taskMgr.hasTaskNamed('ComputingTask'):
            self.taskMgr.add(self.Display,'PostProcessingTask') # restart player
            self.is_playing = True
            self.UserConsole.ConsoleOutput("Now Playing from frame %s" % self.SimState)
        else:
            self.UserConsole.ConsoleOutput("Please wait for the simulation to end, positionnal data isn't available yet", (1,0,0,1))
    
    def Pause(self):
        self.is_playing = False
        self.UserConsole.ConsoleOutput("Paused")
    
    def init_ThreadGraph(self,
                    StartingFrame, 
                    EndFrame, 
                    Xindex, 
                    Yindex,
                    datatype):
        if self.chart_thread == None or not self.chart_thread.is_alive():
            self.chart_thread = threading.Thread(target = self.TrackMotion, 
                        args = (StartingFrame, 
                        EndFrame, 
                        Xindex, 
                        Yindex,
                        datatype))
            self.chart_thread.start()
        else:
            self.TrackMotion(
                    StartingFrame, 
                    EndFrame, 
                    Xindex, 
                    Yindex,
                    datatype)
        

    def TrackMotion(self, 
                    StartingFrame, 
                    EndFrame, 
                    Xindex, 
                    Yindex,
                    datatype):
        '''
        Displays the requested data for one node in a matplotlib external window
        Xindex = length index
        Yindex = width index
        '''
        if StartingFrame >= EndFrame or StartingFrame <= 0 or EndFrame > self.SimLenght :
            self.UserConsole.ConsoleOutput("Invalid frame index provided", (1,0,0,1))
            return None # abort
        self.UserConsole.ConsoleOutput("Processing...")
        Pos = []
        Speed = []
        Accel = []
        for x in range(StartingFrame,EndFrame + 1):
            try:
                localPos = self.Memory.getFramePosData(x)[Xindex][Yindex]
            except:
                self.UserConsole.ConsoleOutput("Simulation is not ready, please wait", (1,0,0,1))
            Pos.append(localPos)
            if datatype == 'speed' or datatype == 'Speed': # primitif mais tant pis
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
            self.UserConsole.ConsoleOutput("Wrong datatype provided", (1,0,0,1))
            return None
        try:
            plt.show()
        except:
            plt.draw()
        self.UserConsole.ConsoleOutput("Done", (0,1,0,1))
        return None

    def showActiveTasks(self):
        for x in self.TaskList:
            self.UserConsole.ConsoleOutput(str(x))

    def addTask(self,
        type:str,
        *extraArgs):
        '''
        adds a constraint to the node
        '''
        self.TaskList.append([type, *extraArgs])
        return None
    
    def delTask(self,index):
        return None

    def pstats(self):
        '''
        Toggles pstats task graph if available. If not, please make sure that pstats is installed on your machine, and execute it using cmd with the command 'pstats'
        '''
        try:
            if not self.using_pstats:
                PStatClient.connect()
                assert PStatClient.isConnected
                self.using_pstats = True
                portVar = ConfigVariableString('pstats-port')
                self.UserConsole.ConsoleOutput('Connected to pstats server at port %s' % portVar.getValue(), (0,1,0,1))
            else:
                PStatClient.disconnect()
                self.using_pstats = False
                self.UserConsole.ConsoleOutput('Disconnected from pstats server successfully')
        except:
            self.UserConsole.ConsoleOutput('Could not establish connection with pstats server', (1,0,0,1))
        return None
    
    # this demo uses the 'edit' mode of the ConsoleOuput routine 
    def progressBarDemo(self):
        '''
        this function animates a tiny progress bar demo (showcases the console line edit mode)
        '''
        self.taskMgr.add(self.progressbarUpdate, "progressbarDemo")
        self.demodog = 0
    
    def progressbarUpdate(self, task):
        limit = 50
        if self.demodog <= limit:
            self.UserConsole.ConsoleOutput('[downloading '+"{0:0=3d}".format(2*self.demodog)+'%  |' + '█'*self.demodog + ' '*(limit-self.demodog) + '|',
                                            color=Vec4((limit-self.demodog)/limit, self.demodog/limit, 0, 1), 
                                            mode = 'edit')
            self.demodog += 1
            return task.cont
        else: return task.done
        

# end class mainApp



def undefined(*args):
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
        stop()

