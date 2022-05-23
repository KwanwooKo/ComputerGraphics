import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def render(primitiveType):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(primitiveType)
    for i in range(0, 12):
        th = np.radians(30 * i)
        glVertex2fv(np.array([np.cos(th), np.sin(th)]))
    glEnd()


def key_callback(window, key, scancode, action, mods):
    global primitiveType
    if key == glfw.KEY_1:
        if action == glfw.PRESS:
            primitiveType = GL_POINTS
    elif key == glfw.KEY_2:
        if action == glfw.PRESS:
            primitiveType = GL_LINES
    elif key == glfw.KEY_3:
        if action == glfw.PRESS:
            primitiveType = GL_LINE_STRIP
    elif key == glfw.KEY_4:
        if action == glfw.PRESS:
            primitiveType = GL_POINTS
    elif key == glfw.KEY_5:
        if action == glfw.PRESS:
            primitiveType = GL_TRIANGLES
    elif key == glfw.KEY_6:
        if action == glfw.PRESS:
            primitiveType = GL_TRIANGLE_STRIP
    elif key == glfw.KEY_7:
        if action == glfw.PRESS:
            primitiveType = GL_TRIANGLE_FAN
    elif key == glfw.KEY_8:
        if action == glfw.PRESS:
            primitiveType = GL_QUADS
    elif key == glfw.KEY_9:
        if action == glfw.PRESS:
            primitiveType = GL_QUAD_STRIP
    elif key == glfw.KEY_0:
        if action == glfw.PRESS:
            primitiveType = GL_POLYGON


def main():
    global primitiveType

    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2020060100-2-1", None, None);
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)

    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render(primitiveType)
        glfw.swap_buffers(window)
    glfw.terminate()
if __name__ == "__main__":
    primitiveType = GL_LINE_LOOP
    main()


