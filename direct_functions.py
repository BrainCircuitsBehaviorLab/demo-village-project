import time

from sound_functions import sound_device, whitenoise_generator
from village.manager import manager
from village.devices.camera import cam_box
from village.custom_classes.direct_functions_base import DirectFunctionsBase

class DirectFunctions(DirectFunctionsBase):
    
    def function1(self):
        """ Play Sound"""
        print("play sound")
        sound = whitenoise_generator(2, 0.05, 0.01)
        sound_device.load(left=sound, right=sound)
        sound_device.play()

    def function2(self):
        """ Camera MSG ON """
        cam_box.annotation = "ON"

    def function3(self):
        """ Clear Camera MSG """
        cam_box.annotation = ""

    def function4(self):
        """ Trigger Opto """
        print("trigger opto")
        manager.task.og.trigger()



    


