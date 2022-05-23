import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)   # 색 추가
    glVertex2fv(np.array([0.,0.]))  # 점 추가
    glVertex2fv(np.array([1.,0.]))  # 점 추가 => 선 연결
    glColor3ub(0, 255, 0)   # 색 추가
    glVertex2fv(np.array([0.,0.]))  # 점 추가
    glVertex2fv(np.array([0.,1.]))  # 점 추가 => 선 연결
    glEnd()
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)       # 삼각형 색 흰색으로 설정
    glVertex2fv((T @ np.array([.0,.5,1.]))[:-1] )
    glVertex2fv((T @ np.array([.0,.0,1.]))[:-1] )
    glVertex2fv((T @ np.array([.5,.0,1.]))[:-1] )
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global gCamAng
    th = np.radians(10)

    if key == glfw.KEY_Q:
        if action == glfw.PRESS:
            gCamAng = gCamAng @ np.array([[1., 0., -.1],
                                          [0., 1., .0],
                                          [0., 0., 1.]])
    elif key == glfw.KEY_E:
        if action == glfw.PRESS:
            gCamAng = np.array([[1., 0., .1],
                                [0., 1., .0],
                                [-.1, 0., 1.]]) @ gCamAng
    elif key == glfw.KEY_A:
        if action == glfw.PRESS:
            gCamAng = gCamAng @ np.array([[np.cos(th), -np.sin(th), 0.],
                                          [np.sin(th), np.cos(th), 0.],
                                          [0., 0., 1.]])
    elif key == glfw.KEY_D:
        if action == glfw.PRESS:
            gCamAng = gCamAng @ np.array([[np.cos(-th), -np.sin(-th), 0.],
                                          [np.sin(-th), np.cos(-th), 0.],
                                          [0., 0., 1.]])
    elif key == glfw.KEY_1:
        if action == glfw.PRESS:
            gCamAng = np.array([[1., 0., 0.],
                                [0., 1., 0.],
                                [0., 0., 1.]])
    elif key == glfw.KEY_W:
        if action == glfw.PRESS:
            gCamAng = gCamAng @ np.array([[.9, 0., 0.],
                                          [0., 1., 0.],
                                          [0., 0., 1.]])
    elif key == glfw.KEY_S:
        if action == glfw.PRESS:
            gCamAng = np.array([[np.cos(th), -np.sin(th), 0.],
                                [np.sin(th), np.cos(th), 0.],
                                [0., 0., 1.]]) @ gCamAng



def main():
    global gCamAng
    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2020060100-3-1", None, None);
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)

    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render(gCamAng)
        glfw.swap_buffers(window)
    glfw.terminate()
if __name__ == "__main__":
    gCamAng = np.array([[1., 0., 0.],
                        [0., 1., 0.],
                        [0., 0., 1.]])
    main()



