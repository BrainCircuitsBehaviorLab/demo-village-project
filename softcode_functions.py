import time
from PyQt5.QtGui import QColor
from sound_functions import sound_device, tone_600
from video_functions import (
    draw_square,
    draw_triangle,
    draw_circle,
    draw_bouncing_circle,
    draw_square_with_task_parameters,
    draw_static_image,
    draw_video,
)
from village.manager import manager


def function1():
    manager.behavior_window.load_draw_function(draw_square)
    # sound = tone_600(duration=1, gain=0.01)
    # sound_device.load(sound, sound)


def function2():
    # manager.behavior_window.load_draw_function(draw_square_with_task_parameters)
    manager.behavior_window.load_draw_function(
        draw_static_image, image=manager.task.settings.image_jpg
    )


def function3():
    # manager.behavior_window.load_draw_function(draw_circle)
    manager.behavior_window.load_draw_function(
        draw_video, video=manager.task.settings.video
    )


def function4():
    manager.behavior_window.load_draw_function(draw_bouncing_circle)


def function5():
    manager.behavior_window.load_draw_function(draw_triangle)


def function6():
    # manager.behavior_window.load_draw_function(draw_gabor)
    manager.behavior_window.load_draw_function(
        draw_video, video=manager.task.settings.video
    )


def function7():
    manager.behavior_window.load_draw_function(
        draw_static_image, image=manager.task.settings.image_png
    )


def function8():
    manager.behavior_window.start_drawing()
    # sound_device.play()
    # task.send_softcode_to_bpod(1)


def function9():
    # is it also possible to change the background color of the window
    # the background color is used in all drawing functions to clean the window
    # the change is persistent until changed again
    manager.behavior_window.background_color = QColor(100, 100, 100)


# def function9():
#     sound = tone_600(duration=1, gain=0.05)
#     sound_device.load(sound, sound)
#     sound_device.play()


def function10():
    # to test overriding outputs
    manager.task.bpod.manual_override_output(("PWM1", 255))  # funciona
    time.sleep(1)
    manager.task.bpod.manual_override_output(("PWM1", 0))  # funciona
    time.sleep(1)
    manager.task.bpod.manual_override_output("Valve1")   # funciona
    time.sleep(1)
    manager.task.bpod.manual_override_output("Valve1Off")   # funciona
    time.sleep(1)
    manager.task.bpod.manual_override_output("BNC1High")  # funciona
    time.sleep(1)
    manager.task.bpod.manual_override_output("BNC1Low")  # funciona


def function11():
    # to test overriding inputs
    manager.task.bpod.manual_override_input("Port1In")  # funciona
    time.sleep(1)
    manager.task.bpod.manual_override_input("Port1Out")  # funciona
    time.sleep(1)


def function33():
    start_time = time.time()
    sound_device.play()
    end_time = time.time()
    print("play delay: ", end_time - start_time)
