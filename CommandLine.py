from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
import sys,os

MAINDIR = Filename.from_os_specific(os.path.abspath(sys.path[0])).getFullpath()


class Console:
    def __init__(self):
        return None
        
    def create(self, CommandDictionary):
        base.a2dBottomLeft.set_bin('background', 123) # avoid drawing order conflict
        self.CommandDictionary = {**CommandDictionary,**{"usage":self.helper,"help":self.showCommands}} # copy for further use in other methods
        self.hidden = False
        self.textscale = 0.04
        self.Lines = 47
        self.font = loader.loadFont(MAINDIR + '/assets/fonts/terminus-ttf-4.47.0/TerminusTTF-4.47.0.ttf')
        self.background = OnscreenImage(image = str(MAINDIR)+"/assets/images/bg.png",pos = (0.65,0,1), parent = base.a2dBottomLeft)
        self.background.setTransparency(TransparencyAttrib.MAlpha)
        self.SavedLines = [OnscreenText(text = '', 
                                            pos = (0.01, 0.1 + x*self.textscale), 
                                            scale = self.textscale, 
                                            align = TextNode.ALeft, 
                                            fg = (1,1,1,1), 
                                            parent = base.a2dBottomLeft,
                                            font= self.font) for x in range(self.Lines)]
        self.loadConsoleEntry()
        self.commands = self.CommandDictionary
        self.callBackIndex = -1
        self.InputLines = []
        #self.entry.reparent_to(App)
        base.accept('f1',self.toggle)
        base.accept('arrow_up',self.callBack,[True])
        base.accept('arrow_down',self.callBack,[False])

        self.ConsoleOutput('- Panda3d runtime console by Balrog -',color = Vec4(0,0,1,1))
        self.ConsoleOutput('successfully loaded all components',color = Vec4(0,1,0,1))
        self.toggle() # initialize as hidden
        return None
    
    def loadConsoleEntry(self): #-1.76, 0, -0.97
        self.entry = DirectEntry(scale=self.textscale,
                                    frameColor=(0,0,0,1),
                                    text_fg = (1,1,1,1),
                                    pos = (0.015, 0, 0.03),
                                    overflow = 1,
                                    command=self.ConvertToFunction,
                                    initialText="",
                                    numLines = 1,
                                    focus=True,
                                    width = 40,
                                    parent = base.a2dBottomLeft,
                                    entryFont = self.font)
        return None
    
    def toggle(self):
        if self.hidden:
            for i in self.SavedLines:
                i.show()
            self.entry.show()
            self.background.show()
        else:
            for i in self.SavedLines:
                i.hide()
            self.entry.hide()
            self.background.hide()
        self.hidden = not(self.hidden)
        return None
    
    def clearText(self):
        self.entry.enterText('')
        return None
    
    def ConvertToFunction(self,data):
        # callback stuff
        self.callBackIndex = -1
        self.InputLines.append(data)

        # gui
        self.entry.destroy()
        self.loadConsoleEntry()
        self.ConsoleOutput(" ")
        self.ConsoleOutput(str(MAINDIR)+"> "+data)

        Buffer = [""]
        for x in range(len(data)): # I know the way I did this sucks but I didn't want to think a lot
            if data[x] == "(":
                Buffer.append("(")
                if x != len(data) - 1 and data[x+1] != ")":
                    Buffer.append("")
                else:pass
            elif data[x] == ")":
                Buffer.append(")")
                if x != len(data) - 1:
                    Buffer.append("")
                else:pass
            elif data[x] == ",":
                if x != len(data) - 1:
                    Buffer.append("")
                else:pass
            else:
                Buffer[len(Buffer)-1] += data[x]

        # check for unnecessary spaces
        for i in range(len(Buffer)):
            Buffer[i] = Buffer[i].strip()


        try:
            ChosenCommand = self.commands[Buffer[0]] # check if the command exists
            if len(Buffer)-1 and Buffer[1] == "(" and Buffer[len(Buffer)-1] == ")": # check if the command has some arguments
                args = Buffer[2:len(Buffer)-1]
                for i in range(len(args)):
                    try:
                        if str(int(args[i])) == args[i]:
                            args[i] = int(args[i])
                        elif str(float(args[i])) == args[i]:
                            args[i] = float(args[i])
                    except ValueError:
                        args[i] = str(args[i])
                try:
                    ChosenCommand(*args)
                except:
                    self.ConsoleOutput("Wrong arguments provided", (1,0,0,1))
            elif len(Buffer) - 1 and Buffer[len(Buffer)-1] != ")":
                self.ConsoleOutput('Missing parenthesis ")" in "'+ data + '"', (1,0,0,1))
            else:
                try:
                    ChosenCommand()
                except:
                    self.ConsoleOutput('This command requires (at least) one argument', (1,0,0,1))

        except:
            self.CommandError(Buffer[0])
        
        return None

    def SError(self,report):
        self.ConsoleOutput("Traceback (most recent call last):", (1,0,0,1))
        self.ConsoleOutput("Incorrect use of the "+str(report)+" command", (1,0,0,1))
        return None
    
    def CommandError(self,report):
        self.ConsoleOutput("Traceback (most recent call last):", (1,0,0,1))
        self.ConsoleOutput("SyntaxError: command "+str(report)+" is not defined", (1,0,0,1))
    
    def ConsoleOutput(self,output, color:Vec4 = Vec4(1,1,1,1), mode:str = 'add'):
        #maxsize = self.entry['width']
        
        maxsize = 81
        #maxsize = 66 # hermit font
        discretized = [output[i:i+maxsize] for i in range(0,len(output),maxsize)]
        if mode == 'add':
            for i in discretized: # for each line
                for x in range(self.Lines-1,0,-1):
                    self.SavedLines[x].text = self.SavedLines[x-1].text
                    self.SavedLines[x].fg = self.SavedLines[x-1].fg
                self.SavedLines[0].text = i
                self.SavedLines[0].fg = color
        elif mode == 'edit':
            n = len(discretized)
            for i in range(n):
                self.SavedLines[i].text = discretized[n - i - 1]
                self.SavedLines[i].fg = color
        return None
    
    def helper(self,index):
        '''
        Provides help concerning a given command
        '''
        try:
            i = self.CommandDictionary[index]
            self.ConsoleOutput("Help concerning command '%s':" % str(index))
            self.ConsoleOutput("- associated function name is '%s'" % str(i.__name__))
            self.ConsoleOutput("- Documentation provided: ")
            doc = self.TextToLine(str(i.__doc__))
            
            self.ConsoleOutput(doc.strip())

            self.ConsoleOutput("- Known arguments: ")
            self.ConsoleOutput(str(i.__code__.co_varnames))
        except KeyError:
            self.ConsoleOutput("Unknown command '%s'" % str(index), (1,0,0,1))
        return None
    
    def showCommands(self):
        '''
        Shows a list of available commands
        '''
        self.ConsoleOutput("List of available commands: ")
        for i in self.CommandDictionary:
            self.ConsoleOutput("- "+str(i))
        self.ConsoleOutput(" ")
        self.ConsoleOutput("Use usage(command) for more details on a specific command")
        return None

    def callBack(self, key : bool):
        invertedInput = self.InputLines[::-1]
        if key: # up key pressed
            try: # avoid out of range errors
                if self.callBackIndex < len(invertedInput):
                    self.callBackIndex += 1
                    self.entry.enterText(invertedInput[self.callBackIndex])
            except: pass
        else:
            try:
                if self.callBackIndex >= 0:
                    self.callBackIndex -= 1
                    self.entry.enterText(([''] + invertedInput)[self.callBackIndex])
            except: pass
        
    def TextToLine(self,text):
        try:
            text = text.replace("\n","")
        except:
            pass
        return text