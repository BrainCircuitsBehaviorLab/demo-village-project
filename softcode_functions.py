import time
from PyQt5.QtGui import QColor
from sound_functions import sound_device, tone_generator, whitenoise_generator
from video_functions import (
    draw_circle_generator,
    draw_rectangle_generator,
    draw_moving_circle_generator,
    draw_triangle_generator,
    draw_image_generator,
    draw_image_with_alpha_generator,
    draw_video_generator,
)
from village.manager import manager


# genero un sonido y lo cargo en el dispositivo de sonido con el mismo volumen en
# ambos canales
def function1():
    gain = 0.05
    sound = tone_generator(duration=1, frequency=2000, ramp_time=0.005)
    sound *= gain
    sound_device.load(sound, sound)


# generamos un sonido de ruido blanco y hacemos que suene solo por el canal derecho,
# en este caso la ganancia y la duracion dependen de la tarea
def function2():
    gain = manager.task.sound_gain
    sound = whitenoise_generator(
        duration=manager.task.sound_duration, ramp_time=0.005
    )
    sound *= gain
    sound_device.load(None, sound)


# generamos un sonido de ruido blanco y hacemos que suene por ambos canales con
# ganancias obtenidas de la calibración
def function3():
    gain_left = manager.sound_calibration.get_sound_gain(
        speaker=0, dB=70, sound_name="whitenoise"
    )
    gain_right = manager.sound_calibration.get_sound_gain(
        speaker=1, dB=70, sound_name="whitenoise"
    )
    sound = whitenoise_generator(
        duration=manager.task.sound_duration, ramp_time=0.005
    )
    sound_left = sound * gain_left
    sound_right = sound * gain_right
    sound_device.load(sound_left, sound_right)


# obtenemos un sonido a partir de un archivo wav y lo cargamos en el dispositivo de sonido
# usamos la ganancia adecuada para ese sonido segun la calibracion
# esta funcion asume que el archivo bac.wav esta en la carpeta media del proyecto
# y que es un archivo mono o stereo (1 o 2 canales)
# simpre devuelve un array para left y otro para right (en caso de mono, left = right)
def function4():
    gain_left = manager.sound_calibration.get_sound_gain(
        speaker=0, dB=70, sound_name="whitenoise"
    )
    gain_right = manager.sound_calibration.get_sound_gain(
        speaker=1, dB=70, sound_name="whitenoise"
    )
    sound_file = manager.task.sound_file
    sound_left, sound_right = sound_device.get_sound_from_wav(sound_file)
    sound_left *= gain_left
    sound_right *= gain_right
    sound_device.load(sound_left, sound_right)


# rproducir el sonido previamente cargado
def function5():
    sound_device.play()

# detener la reproduccion de sonido
def function6():
    sound_device.stop()

# dibujar un circulo blanco en la posicion definida en la tarea y durante la duracion
# definida en la tarea
def function7():
    window = manager.behavior_window
    duration = manager.task.stimulus_duration
    x_pos = manager.task.stimulus_x_pos
    y_pos = manager.task.stimulus_y_pos
    diameter = 300
    color = QColor("white")
    draw_function = draw_circle_generator(
        window, duration, x_pos, y_pos, diameter, color
    )
    manager.behavior_window.load_draw_function(draw_function)

# dibujar un rectangulo rojo en la posicion definida en la tarea y durante la duracion
# definida en la tarea
def function8():
    window = manager.behavior_window
    duration = manager.task.stimulus_duration
    x_pos = manager.task.stimulus_x_pos
    y_pos = manager.task.stimulus_y_pos
    width = 300
    height = 300
    color = QColor("#FF0000")
    draw_function = draw_rectangle_generator(
        window, duration, x_pos, y_pos, width, height, color
    )
    manager.behavior_window.load_draw_function(draw_function)

# dibujar un circulo blanco que oscila en el centro de la panatalla,
# en la posicion definida en la tarea y durante la duracion definida en la tarea
def function9():
    window = manager.behavior_window
    duration = manager.task.stimulus_duration
    diameter = 300
    color = QColor("white")
    draw_function = draw_moving_circle_generator(
        window, duration, diameter, color
    )
    manager.behavior_window.load_draw_function(draw_function)

# dibujar un triangulo verde indeterminadamente, hasta que otra accion lo interrumpa,
# usamos un valor de duracion muy alto
def function10():
    window = manager.behavior_window
    duration = 100000
    color = QColor("green")
    draw_function = draw_triangle_generator(
        window, duration, color
    )
    manager.behavior_window.load_draw_function(draw_function)


# dibujar la imagen definida en la tarea en la posicion definida en la tarea y durante
# la duracion definida en la tarea
def function11():
    window = manager.behavior_window
    duration = manager.task.stimulus_duration
    x_pos = manager.task.stimulus_x_pos
    y_pos = manager.task.stimulus_y_pos
    image_file = manager.task.image_file

    draw_function = draw_image_generator(window, duration, x_pos, y_pos)
    manager.behavior_window.load_draw_function(draw_function, image=image_file)

# dibujar la imagen definida en la tarea con canal alfa, en la posicion definida en
# la tarea y durante la duracion definida en la tarea
def function12():
    window = manager.behavior_window
    duration = manager.task.stimulus_duration
    x_pos = manager.task.stimulus_x_pos
    y_pos = manager.task.stimulus_y_pos
    image_file = manager.task.image_file2

    draw_function = draw_image_with_alpha_generator(window, duration, x_pos, y_pos)
    manager.behavior_window.load_draw_function(draw_function, image=image_file)


# reproducir el video definido en la tarea durante la duracion definida en la tarea
def function13():
    window = manager.behavior_window
    duration = manager.task.stimulus_duration
    video_file = manager.task.video_file

    draw_function = draw_video_generator(window, duration)
    manager.behavior_window.load_draw_function(draw_function, video=video_file)

# comenzar a dibujar en la ventana
def function14():
    manager.behavior_window.start_drawing()

# detener a dibujar en la ventana
def function15():
    manager.behavior_window.stop_drawing()


# cambiar el color de fondo de la ventana
# the background color is used in all drawing functions to clean the window
# the change is persistent until changed again
def function16():
    manager.behavior_window.background_color = QColor(100, 100, 100)
