import glfw
from OpenGL.GL import *
import numpy as np
from OpenGL.GLU import *

def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)

    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)

    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)

    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)

    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)

    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glEnd()


def drawCubeArray():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                glPushMatrix()
                glTranslatef(i, j, -k - 1)
                glScalef(.5, .5, .5)
                drawUnitCube()
                glPopMatrix()


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([1., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 1., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0]))
    glVertex3fv(np.array([0., 0., 1.]))
    glEnd()

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    glLoadIdentity()

    gluPerspective(45, 1, 1, 10)

    # Replace this call with two glRotatef() calls and one glTranslatef() call
    # gluLookAt(3,3,3, 0,0,0, 0,1,0)

    glRotatef(36.264, 1, 0, 0)
    glRotatef(45, 0, -1, 0)
    glTranslate(-3, -3, -3)

    drawFrame()
    glColor3ub(255, 255, 255)
    drawCubeArray()

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, '2020060100-4-2', None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()
if __name__ == "__main__":
    main()




# import glfw
# from OpenGL.GL import *
# import numpy as np
# from OpenGL.GLU import *
#
#
# def render(gComposedM):
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glEnable(GL_DEPTH_TEST)
#     glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
#
#     glLoadIdentity()
#     gluPerspective(45, 1, 1, 10)
#     gluLookAt(.2, .5, 2, 0, 0, 0, 0, 1, 0)
#
#     drawFrame(np.identity(4))
#     drawFrame(gComposedM)
#
#     gluLookAt(3, 3, 3, 0, 0, 0, 0, 1, 0)
#     glColor3ub(255, 255, 255)
#     drawCubeArray()
#
#
# def key_callback(window, key, scancode, action, mods):
#     if action == glfw.PRESS or action == glfw.REPEAT:
#         global gComposedM
#         if key == glfw.KEY_W:
#             newM = np.array([[1., 0., 0., 0.],
#                              [0., 1., 0., 0.],
#                              [0., 0., 1., -.5],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_Z:
#             newM = np.array([[1., 0., 0., 0.],
#                              [0., 1., 0., 0.],
#                              [0., 0., 1., .5],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_U:
#             newM = np.array([[1., 0., 0., -.5],
#                              [0., 1., 0., 0.],
#                              [0., 0., 1., 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_X:
#             newM = np.array([[1., 0., 0., .5],
#                              [0., 1., 0., 0.],
#                              [0., 0., 1., 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_V:
#             newM = np.array([[1., 0., 0., 0.],
#                              [0., 1., 0., -.5],
#                              [0., 0., 1., 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_Y:
#             newM = np.array([[1., 0., 0., 0.],
#                              [0., 1., 0., .5],
#                              [0., 0., 1., 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_1:
#             th = np.radians(36.264)
#             newM = np.array([[1., 0., 0., 0.],
#                              [0., np.cos(th), -np.sin(th), 0.],
#                              [0., np.sin(th), np.cos(th), 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_2:
#             th = np.radians(-36.264)
#             newM = np.array([[1., 0., 0., 0.],
#                              [0., np.cos(th), -np.sin(th), 0.],
#                              [0., np.sin(th), np.cos(th), 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_3:
#             th = np.radians(3)
#             newM = np.array([[np.cos(th), 0., np.sin(th), 0.],
#                              [0., 1., 0., 0.],
#                              [-np.sin(th), 0., np.cos(th), 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_4:
#             th = np.radians(-3)
#             newM = np.array([[np.cos(th), 0., np.sin(th), 0.],
#                              [0., 1., 0., 0.],
#                              [-np.sin(th), 0., np.cos(th), 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_5:
#             th = np.radians(3)
#             newM = np.array([[np.cos(th), -np.sin(th), 0., 0.],
#                              [np.sin(th), np.cos(th), 0., 0.],
#                              [0., 0., 1., 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_6:
#             th = np.radians(-3)
#             newM = np.array([[np.cos(th), -np.sin(th), 0., 0.],
#                              [np.sin(th), np.cos(th), 0., 0.],
#                              [0., 0., 1., 0.],
#                              [0., 0., 0., 1.]])
#             gComposedM = newM @ gComposedM
#
#         elif key == glfw.KEY_I:
#             gComposedM = np.identity(4)
#
#
# def drawUnitCube():
#     glBegin(GL_QUADS)
#     glVertex3f(0.5, 0.5, -0.5)
#     glVertex3f(-0.5, 0.5, -0.5)
#     glVertex3f(-0.5, 0.5, 0.5)
#     glVertex3f(0.5, 0.5, 0.5)
#
#     glVertex3f(0.5, -0.5, 0.5)
#     glVertex3f(-0.5, -0.5, 0.5)
#     glVertex3f(-0.5, -0.5, -0.5)
#     glVertex3f(0.5, -0.5, -0.5)
#
#     glVertex3f(0.5, 0.5, 0.5)
#     glVertex3f(-0.5, 0.5, 0.5)
#     glVertex3f(-0.5, -0.5, 0.5)
#     glVertex3f(0.5, -0.5, 0.5)
#
#     glVertex3f(0.5, -0.5, -0.5)
#     glVertex3f(-0.5, -0.5, -0.5)
#     glVertex3f(-0.5, 0.5, -0.5)
#     glVertex3f(0.5, 0.5, -0.5)
#
#     glVertex3f(-0.5, 0.5, 0.5)
#     glVertex3f(-0.5, 0.5, -0.5)
#     glVertex3f(-0.5, -0.5, -0.5)
#     glVertex3f(-0.5, -0.5, 0.5)
#
#     glVertex3f(0.5, 0.5, -0.5)
#     glVertex3f(0.5, 0.5, 0.5)
#     glVertex3f(0.5, -0.5, 0.5)
#     glVertex3f(0.5, -0.5, -0.5)
#     glEnd()
#
#
# def drawCubeArray():
#     for i in range(5):
#         for j in range(5):
#             for k in range(5):
#                 glPushMatrix()
#                 glTranslatef(i, j, -k - 1)
#                 glScalef(.5, .5, .5)
#                 drawUnitCube()
#                 glPopMatrix()
#
#
# def drawFrame(gComposedM):
#     glBegin(GL_LINES)
#     glColor3ub(255, 0, 0)
#     glVertex3fv((gComposedM @ np.array([0., 0., 0., 1.]))[:-1])
#     glVertex3fv((gComposedM @ np.array([1., 0., 0., 1.]))[:-1])
#     glColor3ub(0, 255, 0)
#     glVertex3fv((gComposedM @ np.array([0., 0., 0., 1.]))[:-1])
#     glVertex3fv((gComposedM @ np.array([0., 1., 0., 1.]))[:-1])
#     glColor3ub(0, 0, 255)
#     glVertex3fv((gComposedM @ np.array([0., 0., 0., 1.]))[:-1])
#     glVertex3fv((gComposedM @ np.array([0., 0., 1., 1.]))[:-1])
#     glEnd()
#
#
# def main():
#     global gComposedM
#     if not glfw.init():
#         return
#     window = glfw.create_window(480, 480, 'local and world', None, None)
#     if not window:
#         glfw.terminate()
#         return
#     glfw.make_context_current(window)
#     glfw.set_key_callback(window, key_callback)
#     glfw.swap_interval(1)
#
#     while not glfw.window_should_close(window):
#         glfw.poll_events()
#         render(gComposedM)
#         glfw.swap_buffers(window)
#
#     glfw.terminate()
#
#
# if __name__ == "__main__":
#     gComposedM = np.identity(4)
#     main()