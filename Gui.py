from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
import ctypes



class UserInterface:
    def __init__(self, fullscreen : bool = False):
        self.interface01 = [] # loading animation
        self.interface02 = [] # displaying preloaded data
        self.fullscreen = fullscreen

        self.using_captions = False
        self.Indicators = []
        return None
    
    def create(self):
        # do stuff
        return None
    
    def show(self,element):
        # do stuff
        return None
    
    def hide(self,element):
        # do stuff
        return None
    
    def toggleFullScreen(self):
        self.fullscreen = not self.fullscreen

        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.window_properties = WindowProperties()
        if self.fullscreen:
            self.window_properties.setFullscreen(1)
            self.window_properties.setSize(screensize)
        else:
            self.window_properties.setFullscreen(0)
            
        
        base.win.requestProperties(self.window_properties)
    
    def toggleIndicators(self):
        self.using_captions = not self.using_captions
        if self.using_captions:
            if not len(self.Indicators):# never created before
                for x in range(4):
                    node = TextNode('text%s' % str(x))
                    node.setText('') # default
                    textNdp = render.attachNewNode(node)
                    self.Indicators.append(textNdp)
            else:
                for x in self.Indicators:
                    x.show()
                    
            ShowBase.task_mgr.add(self.updateIndicators,'captionUpdatingTask')
        else:
            for x in self.Indicators:
                x.hide()
    
    def updateIndicators(self, task, data):
        if self.using_captions:

            return task.cont
        else:
            return task.done
