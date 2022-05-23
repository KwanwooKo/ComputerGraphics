import glfw
from OpenGL.GL import *
import numpy as np
from OpenGL.GLU import *
gCamAng = 0
def render(camAng):
    # enable depth test (we'll see details later)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()

    # projection transformation
    glOrtho(-1,1, -1,1, -1,1)

    # viewing transformation
    gluLookAt(.1*np.sin(camAng),.1, .1*np.cos(camAng), 0,0,0, 0,1,0)

    drawFrame()             # 제 1좌표계 (블루)
    t = glfw.get_time()

    # modeling transformation
    # blue base transformation
    glPushMatrix()                  # 스택 푸쉬(기본박스)
    glTranslatef(np.sin(t), 0, 0)   # 기본 박스가 x축으로 이동
    # blue base drawing
    glPushMatrix()                  # 스택 푸쉬(블루박스)
    drawFrame()
    glScalef(.2, .2, .2)            # 스케일 조정
    glColor3ub(0, 0, 255)           # 블루(색칠)
    drawBox()                       # 블루 그리기
    glPopMatrix()                   # 블루 팝
    # red arm transformation
    glPushMatrix()                  # 레드박스  (현재상태: 기본박스 -> 레드박스)
    glRotatef(t * (180 / np.pi), 0, 0, 1)   # 회전시키는 함수(레드박스)
    glTranslatef(.5, 0, .01)                # 레드 박스 원점 평행이동
    # red arm drawing
    glPushMatrix()                          # 레드박스 스케일
    drawFrame()
    glScalef(.5, .1, .1)
    glColor3ub(255, 0, 0)                   # 레드(색칠)
    drawBox()                               # 레드 그리기
    glPopMatrix()                           # draw만 하고 팝    # 현재 상태 red arm
    # 현재 상태 기본 박스
    glPushMatrix()          # green 박스
    glTranslatef(.5, 0, .01)  # 평행이동
    glPushMatrix()          # 그림그리는 박스
    glRotatef(t * (180 / np.pi), 0, 0, 1)  # 회전시키는 함수
    drawFrame()
    glScalef(.1, .1, .0)
    glColor3ub(0, 255, 0)
    drawBox()
    glPopMatrix()   # 그림 그리기
    glPopMatrix()   # rotate 용
    glPopMatrix()
    glPopMatrix()


def drawBox():
    glBegin(GL_QUADS)
    glVertex3fv(np.array([1,1,0.]))
    glVertex3fv(np.array([-1,1,0.]))
    glVertex3fv(np.array([-1,-1,0.]))
    glVertex3fv(np.array([1,-1,0.]))
    glEnd()

def drawFrame():
    # draw coordinate: x in red, y in green, z in blue
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([1., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 1., 0.]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global gCamAng, gComposedM

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key == glfw.KEY_3:
            gCamAng += np.radians(10)

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480,"2020060100-4-1", None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render(gCamAng)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()