from PyQt5.QtCore import QRect, Qt
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor, QPainter, QPolygonF

import math


def draw_circle_generator(window, duration, x_pos, y_pos, diameter, color):

    def draw():
        with QPainter(window) as painter:
            # no transparency and no antialiasing (drawing is faster)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.setRenderHint(QPainter.Antialiasing, False)

            # clean the window with background color
            painter.fillRect(painter.viewport(), window.background_color)

            # use the parameters to draw the circle for the specified duration
            if window.elapsed_time < duration:
                painter.setPen(Qt.NoPen)
                painter.setBrush(color)
                painter.drawEllipse(QRect(x_pos, y_pos, diameter, diameter))

    return draw


def draw_rectangle_generator(
    window, duration, x_pos, y_pos, width, height, color
):

    def draw():
        with QPainter(window) as painter:
            # no transparency and no antialiasing (drawing is faster)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.setRenderHint(QPainter.Antialiasing, False)

            # clean the window with background color
            painter.fillRect(painter.viewport(), window.background_color)

            # use the parameters to draw the rectangle for the specified duration
            if window.elapsed_time < duration:
                painter.setPen(Qt.NoPen)
                painter.setBrush(color)
                painter.drawRect(x_pos, y_pos, width, height)

    return draw


def draw_moving_circle_generator(
    window, duration, diameter, color
):

    def draw():
        with QPainter(window) as painter:
            # no transparency and no antialiasing (drawing is faster)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.setRenderHint(QPainter.Antialiasing, False)

            # clean the window with background color
            painter.fillRect(painter.viewport(), window.background_color)

            # use the parameters to draw the circle for the specified duration
            if window.elapsed_time < duration:
                x_pos = int(100 * math.sin(window.elapsed_time * 2 * math.pi))
                painter.setPen(QColor("red"))
                painter.setBrush(color)
                painter.drawEllipse(QRect(x_pos, 0, diameter, diameter))

    return draw


def draw_triangle_generator(window, duration, color):
    def draw():
        with QPainter(window) as painter:
            # no transparency and no antialiasing (drawing is faster)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.setRenderHint(QPainter.Antialiasing, False)

            # clean the window with background color
            painter.fillRect(painter.viewport(), window.background_color)

            # use the parameters to draw the triangle for the specified duration
            if window.elapsed_time < duration:
                # get window size
                width = painter.viewport().width()
                height = painter.viewport().height()

                # border and fill
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(color))

                # draw the triangle
                points = QPolygonF(
                    [
                        QPointF(width / 2, height / 2 - 100),
                        QPointF(width / 2 - 100, height / 2 + 100),
                        QPointF(width / 2 + 100, height / 2 + 100),
                    ]
                )
                painter.drawPolygon(points)

    return draw


def draw_image_generator(window, duration, x_pos, y_pos):
    def draw():
        with QPainter(window) as painter:
            # no transparency and no antialiasing (drawing is faster)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.setRenderHint(QPainter.Antialiasing, False)

            # clean the window with the background color
            painter.fillRect(painter.viewport(), window.background_color)

            # use the parameters to draw the image for the specified duration
            if window.elapsed_time < duration:
                painter.drawPixmap(x_pos, y_pos, window.image)

    return draw

def draw_image_with_alpha_generator(window, duration, x_pos, y_pos):
    def draw():
        with QPainter(window) as painter:
            # in this case we use transparency as the image is a png with alpha channel
            # CompositionMode_SourceOver instead of CompositionMode_Source
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setRenderHint(QPainter.Antialiasing, False)

            # clean the window with the background color
            painter.fillRect(painter.viewport(), window.background_color)

            # use the parameters to draw the image for the specified duration
            if window.elapsed_time < duration:
                painter.drawPixmap(x_pos, y_pos, window.image)

    return draw


def draw_video_generator(window, duration):
    def draw():
        with QPainter(window) as painter:
            # no transparency and no antialiasing (drawing is faster)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.setRenderHint(QPainter.Antialiasing, False)

            # clean the window with the background color
            painter.fillRect(painter.viewport(), window.background_color)

            # draw the video for the specified duration
            if window.elapsed_time < duration:
                # get the last frame from the video source
                frame = window.get_video_frame()
                # draw the last frame from the video source
                if frame is not None:
                    painter.drawImage(0, 0, frame)

    return draw
