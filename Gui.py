from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
import ctypes



class UserInterface:
    def __init__(self, fullscreen:bool = False):
        self.interface01 = [] # loading animation
        self.interface02 = [] # displaying preloaded data
        self.fullscreen = fullscreen
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