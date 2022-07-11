import math
from telnetlib import XASCII
import glfw
import sys
import pdb
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import ArrayDatatype
import time
import numpy as np
import ctypes
from PIL.Image import open
import OBJ
from Ray import *



# global variables
wld2cam=[]                      # cam list
cam2wld=[]                      # cam list
cow2wld=None                    # 소
animCow = np.zeros((4, 4))
direction = []                # controlPoints 에서의 접선의 방향
cursorOnCowBoundingBox = False  # 박스그리기용 boolean
pickInfo=None                   # mouse click 
floorTexID=0
animState = False                # cow를 그리는 boolean 변수
animStartTime = 0
animTime = 0
playTime = 0
HermiteConversion = np.array([[2, -2, 1, 1],
                              [-3, 3, -2, -1],
                              [0, 0, 1, 0],
                              [1, 0, 0, 0]])
CatmullRomCoefficient = np.array([[0, 1, 0, 0],
                                  [0, 0, 1, 0],
                                  [-.5, 0, .5, 0],
                                  [0, -.5, 0, .5]])
cameras= [
	[28,18,28, 0,2,0, 0,1,0],   
	[28,18,-28, 0,2,0, 0,1,0], 
	[-28,18,28, 0,2,0, 0,1,0], 
	[-12,12,0, 0,2,0, 0,1,0],  
	[0,100,0,  0,0,0, 1,0,0]
]
controlPoints = []
camModel=None
cowModel=None
H_DRAG=1
V_DRAG=2
isOnclick = False
# dragging state
isDrag=0
currentPos = np.array([.0, .0, .0])

class PickInfo:
    def __init__(self, cursorRayT, cowPickPosition, cowPickConfiguration, cowPickPositionLocal):
        self.cursorRayT = cursorRayT                            # 내 시점을 기준으로 한 ray
        self.cowPickPosition = cowPickPosition.copy()           # cow slab 랑 cursorRay와 만나는 점
        self.cowPickConfiguration = cowPickConfiguration.copy() # 
        self.cowPickPositionLocal = cowPickPositionLocal.copy()

def vector3(x,y,z):
    return np.array((x,y,z))
def position3(v):
    # divide by w
    w=v[3]
    return vector3(v[0]/w, v[1]/w, v[2]/w)

def vector4(x,y,z):
    return np.array((x,y,z,1))

def rotate(m,v):
    return m[0:3, 0:3]@v
def transform(m, v):
    return position3(m@np.append(v,1))

def getTranslation(m):
    return m[0:3,3]
def setTranslation(m,v):
    m[0:3,3]=v

def makePlane(a,  b,  n):
    v = a.copy()
    for i in range(3):
        if n[i]==1.0:
            v[i]=b[i]
        elif n[i]==-1.0:
            v[i]=a[i]
        else:
            assert(n[i]==0.0)            
    return Plane(rotate(cow2wld,n),transform(cow2wld,v))

def onKeyPress( window, key, scancode, action, mods):
    global cameraIndex
    if action == glfw.RELEASE:
        return  # do nothing
    # If 'c' or space bar are pressed, alter the camera.
    # If a number is pressed, alter the camera corresponding the number.
    if key == glfw.KEY_C or key == glfw.KEY_SPACE:
        print( "Toggle camera %s\n"% cameraIndex )
        cameraIndex += 1

    if cameraIndex >= len(wld2cam):
        cameraIndex = 0

def drawOtherCamera():
    global cameraIndex,wld2cam, camModel
    for i in range(len(wld2cam)):
        if (i != cameraIndex):
            glPushMatrix()												# Push the current matrix on GL to stack. The matrix is wld2cam[cameraIndex].matrix().
            glMultMatrixd(cam2wld[i].T)
            drawFrame(5)											# Draw x, y, and z axis.
            frontColor = [0.2, 0.2, 0.2, 1.0]
            glEnable(GL_LIGHTING)									
            glMaterialfv(GL_FRONT, GL_AMBIENT, frontColor)			# Set ambient property frontColor.
            glMaterialfv(GL_FRONT, GL_DIFFUSE, frontColor)			# Set diffuse property frontColor.
            glScaled(0.5,0.5,0.5)										# Reduce camera size by 1/2.
            glTranslated(1.1,1.1,0.0)									# Translate it (1.1, 1.1, 0.0).
            camModel.render()
            glPopMatrix()												# Call the matrix on stack. wld2cam[cameraIndex].matrix() in here.

def drawFrame(leng):
    glDisable(GL_LIGHTING)	# Lighting is not needed for drawing axis.
    glBegin(GL_LINES)		# Start drawing lines.
    glColor3d(1,0,0)		# color of x-axis is red.
    glVertex3d(0,0,0)			
    glVertex3d(leng,0,0)	# Draw line(x-axis) from (0,0,0) to (len, 0, 0). 
    glColor3d(0,1,0)		# color of y-axis is green.
    glVertex3d(0,0,0)			
    glVertex3d(0,leng,0)	# Draw line(y-axis) from (0,0,0) to (0, len, 0).
    glColor3d(0,0,1)		# color of z-axis is  blue.
    glVertex3d(0,0,0)
    glVertex3d(0,0,leng)	# Draw line(z-axis) from (0,0,0) - (0, 0, len).
    glEnd()			# End drawing lines.

def getAngle(vec1, vec2):
    vec2[1] = 0         # y 좌표를 0으로 바꿔줘야 해
    u = normalize(vec1)
    v = normalize(vec2)
#*********************************************************************************
# Draw 'cow' object.
#*********************************************************************************/

def drawCow(_cow2wld, drawBB):

    glPushMatrix()		# Push the current matrix of GL into stack. This is because the matrix of GL will be change while drawing cow.

    # The information about location of cow to be drawn is stored in cow2wld matrix.
    # (Project2 hint) If you change the value of the cow2wld matrix or the current matrix, cow would rotate or move.
    glMultMatrixd(_cow2wld.T)

    drawFrame(5)										# Draw x, y, and z axis.
    frontColor = [0.8, 0.2, 0.9, 1.0]
    glEnable(GL_LIGHTING)
    glMaterialfv(GL_FRONT, GL_AMBIENT, frontColor)		# Set ambient property frontColor.
    glMaterialfv(GL_FRONT, GL_DIFFUSE, frontColor)		# Set diffuse property frontColor.
    cowModel.render()	# Draw cow. 
    glDisable(GL_LIGHTING)
    if drawBB:
        glBegin(GL_LINES)
        glColor3d(1,1,1)
        cow=cowModel
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmax[2])

        glColor3d(1,1,1)
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmax[2])

        glColor3d(1,1,1)
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmax[2])


        glColor3d(1,1,1)
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmax[2])

        glColor3d(1,1,1)
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmin[1], cow.bbmax[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmin[0], cow.bbmax[1], cow.bbmax[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmin[2])
        glVertex3d( cow.bbmax[0], cow.bbmax[1], cow.bbmax[2])
        glEnd()
    glPopMatrix()			# Pop the matrix in stack to GL. Change it the matrix before drawing cow.
    
def drawFloor():

    glDisable(GL_LIGHTING)

    # Set color of the floor.
    # Assign checker-patterned texture.
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, floorTexID )

    # Draw the floor. Match the texture's coordinates and the floor's coordinates resp. 
    nrep=4
    glBegin(GL_POLYGON)
    glTexCoord2d(0,0)
    glVertex3d(-12,-0.1,-12)		# Texture's (0,0) is bound to (-12,-0.1,-12).
    glTexCoord2d(nrep,0)
    glVertex3d( 12,-0.1,-12)		# Texture's (1,0) is bound to (12,-0.1,-12).
    glTexCoord2d(nrep,nrep)
    glVertex3d( 12,-0.1, 12)		# Texture's (1,1) is bound to (12,-0.1,12).
    glTexCoord2d(0,nrep)
    glVertex3d(-12,-0.1, 12)		# Texture's (0,1) is bound to (-12,-0.1,12).
    glEnd()

    glDisable(GL_TEXTURE_2D)	
    drawFrame(5)				# Draw x, y, and z axis.

def display():
    global cameraIndex, cow2wld, animState, animTime, animStartTime, CatmullRomCoefficient, HermiteConversion, isOnclick, isDrag, animCow
    glClearColor(0.8, 0.9, 0.9, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)				# Clear the screen
    # set viewing transformation.
    glLoadMatrixd(wld2cam[cameraIndex].T)

    drawOtherCamera()												# Locate the camera's position, and draw all of them.
    drawFloor()													    # Draw floor.

    # TODO: 
    # update cow2wld here to animate the cow.
    # animTime=glfw.get_time()-animStartTime
    # you need to modify both the translation and rotation parts of the cow2wld matrix every frame.
    # you would also probably need a state variable for the UI.    
    if len(controlPoints) == 6 and animState == False:
        animState = True
        animStartTime = glfw.get_time()
    else:
        if animState == False:
            for cow in controlPoints:
                drawCow(cow, False)
    
    if animState == True:
        animTime = glfw.get_time() - animStartTime
        
        firstIndex = math.floor(animTime)
        beforeIndex = firstIndex - 1
        nextIndex = firstIndex + 1
        lastIndex = firstIndex + 2
        
        animTime = animTime - int(animTime)
        
        if firstIndex % 6 == 0:
            beforeIndex = 5
        
        animCow = cow2wld
        # animCow = cow2wld.copy()
                
        beforePoint = getTranslation(controlPoints[beforeIndex % 6])
        firstPoint = getTranslation(controlPoints[firstIndex % 6])
        nextPoint = getTranslation(controlPoints[nextIndex % 6])
        lastPoint = getTranslation(controlPoints[lastIndex % 6])

        position = np.array([beforePoint, firstPoint, nextPoint, lastPoint])
        
        var = np.array([animTime ** 3, animTime ** 2, animTime, 1])
        
        # 방향벡터 구해서 하면 되나?
        # R = vector4(R[0], R[1], R[2])
        nextPos = var @ HermiteConversion @ CatmullRomCoefficient @ position

####################################################################################################
# 여기까지가 경로 이동 처리
####################################################################################################
        # 여기서부터 방향 설정
        # local의 새로운 x, y, z 축을 계산
        newX = normalize(nextPos - getTranslation(animCow))
        newZ = normalize(np.cross(newX, np.array([0, 1, 0])))
        newY = normalize(np.cross(newZ, newX))
        
        # animCow 에 새로운 x, y, z 축 적용
        animCow[:3, 0] = newX
        animCow[:3, 1] = newY
        animCow[:3, 2] = newZ

        setTranslation(animCow, nextPos)
        
        # 3바퀴 돌기 때문에 18로 설정
        if nextIndex <= 18:
            drawCow(animCow, False)
        else:
            animState = False
            cow2wld = controlPoints[0]
            controlPoints.clear()
            isOnclick = False
            isDrag = 0
            cow2wld[0:3, 0] = np.array([1, 0, 0])
            cow2wld[0:3, 1] = np.array([0, 1, 0])
            cow2wld[0:3, 2] = np.array([0, 0, 1])
            drawCow(cow2wld, cursorOnCowBoundingBox)     
            
    else:       # animState == False
        drawCow(cow2wld, cursorOnCowBoundingBox)		# Draw cow.    
        # 더이상 cow를 그리면 안됨
        # original cow 도 그리면 안되고
        # mouse input 도 받으면 안돼
        # 반복문으로 돌려서 cow2wld 를 움직이게 하기
        # 근데 여기서 i 가 0 이면 -1 index에 접근이 안되니까
        # 가중치를 계산해서 그래프 그리기
        # 말고 일단 움직이는게 궁금하니까 direction에 곱해서 한번 그려보자
        # 3바퀴 돌아야 해서 18로 설정
        # cow2wld = controlPoints[0]      # original cow2wld에 초기 상태의 controlPoints 저장
        # 롤러코스터 돌려주고 태초마을로 보내줘야돼
        # animCow 초기 세팅을 cow2wld 로 해줘서 시작지점을 받을 수 있게 설정
    glFlush()

def reshape(window, w, h):
    width = w
    height = h
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)            # Select The Projection Matrix
    glLoadIdentity()                       # Reset The Projection Matrix
    # Define perspective projection frustum
    aspect = width/(float)(height)
    gluPerspective(45, aspect, 1, 1024)
    matProjection=glGetDoublev(GL_PROJECTION_MATRIX).T
    glMatrixMode(GL_MODELVIEW)             # Select The Modelview Matrix
    glLoadIdentity()                       # Reset The Projection Matrix

def initialize(window):
    global cursorOnCowBoundingBox, floorTexID, cameraIndex, camModel, cow2wld, cowModel, currentPos
    cursorOnCowBoundingBox=False
    # Set up OpenGL state
    glShadeModel(GL_SMOOTH)         # Set Smooth Shading
    glEnable(GL_DEPTH_TEST)         # Enables Depth Testing
    glDepthFunc(GL_LEQUAL)          # The Type Of Depth Test To Do
    # Use perspective correct interpolation if available
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    # Initialize the matrix stacks
    width, height = glfw.get_window_size(window)
    reshape(window, width, height)
    # Define lighting for the scene
    lightDirection   = [1.0, 1.0, 1.0, 0]
    ambientIntensity = [0.1, 0.1, 0.1, 1.0]
    lightIntensity   = [0.9, 0.9, 0.9, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientIntensity)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightIntensity)
    glLightfv(GL_LIGHT0, GL_POSITION, lightDirection)
    glEnable(GL_LIGHT0)

    # initialize floor
    im = open('bricks.bmp')
    try:
        ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGB", 0, -1)
    except SystemError:
        ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBX", 0, -1)

    # Make texture which is accessible through floorTexID. 
    floorTexID=glGenTextures( 1)
    glBindTexture(GL_TEXTURE_2D, floorTexID)		
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, ix, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
    # initialize cow
    cowModel = OBJ.OBJrenderer("cow.obj")

    # initialize cow2wld matrix
    glPushMatrix()		        # Push the current matrix of GL into stack.
    glLoadIdentity()		        # Set the GL matrix Identity matrix.
    glTranslated(0,-cowModel.bbmin[1],-8)	# Set the location of cow.
    glRotated(-90, 0, 1, 0)		# Set the direction of cow. These information are stored in the matrix of GL.
    cow2wld = glGetDoublev(GL_MODELVIEW_MATRIX).T # convert column-major to row-major 
    glPopMatrix()			# Pop the matrix on stack to GL.

    # 현재 소의 위치를 좌표로 변환
    currentPos = getTranslation(cow2wld)
    
    # intialize camera model.
    camModel = OBJ.OBJrenderer("camera.obj")


    # initialize camera frame transforms.

    cameraCount=len(cameras)
    for i in range(cameraCount):
        # 'c' points the coordinate of i-th camera.
        c = cameras[i]										
        glPushMatrix()													# Push the current matrix of GL into stack.
        glLoadIdentity()												# Set the GL matrix Identity matrix.
        gluLookAt(c[0],c[1],c[2], c[3],c[4],c[5], c[6],c[7],c[8])		# Setting the coordinate of camera.
        wld2cam.append(glGetDoublev(GL_MODELVIEW_MATRIX).T)
        glPopMatrix()													# Transfer the matrix that was pushed the stack to GL.
        cam2wld.append(np.linalg.inv(wld2cam[i]))
    cameraIndex = 0

def onMouseButton(window,button, state, mods):
    global isDrag, V_DRAG, H_DRAG, isOnclick, cow2wld
    GLFW_DOWN=1
    GLFW_UP=0
    x, y=glfw.get_cursor_pos(window)
    if button == glfw.MOUSE_BUTTON_LEFT: 
        if state == GLFW_DOWN:
            if isDrag == H_DRAG:        # horizontal drag
                isDrag = 0
            else:
                isDrag = V_DRAG            
            print( "Left mouse down-click at %d %d\n" % (x,y))
            if isDrag == 0:
                # controlPoints.append(cow2wld)
                isDrag = V_DRAG
            # start vertical dragging
        elif state == GLFW_UP and isDrag != 0:
            isDrag = H_DRAG
            if isOnclick == False:
                isOnclick = True
            else:
                controlPoints.append(cow2wld)
            print( "Left mouse up\n")
            # start horizontal dragging using mouse-move events.
    elif button == glfw.MOUSE_BUTTON_RIGHT:
        if state == GLFW_DOWN:
            print( "Right mouse click at (%d, %d)\n"%(x,y) )
    

def onMouseDrag(window, x, y):
    global isDrag,cursorOnCowBoundingBox, pickInfo, cow2wld, currentPos, controlPoints
    if animState == True:       # animation 진행 하는 동안 마우스 개입 불가능하게 막아둠
        return
    if isDrag:  # drag 가 되고 있는지 확인
        print( "in drag mode %d\n"% isDrag)
        if  isDrag == V_DRAG:           # vertical dragging
            # vertical dragging
            # TODO:
            # create a dragging plane perpendicular to the ray direction, 
            # and test intersection with the screen ray.
            ray = screenCoordToRay(window, x, y)
            pp = pickInfo
            p = Plane(ray.direction, currentPos)
            c = ray.intersectsPlane(p)                  # pair<boolean, position>
            currentPos[1] = ray.getPoint(c[1])[1]       # y 좌표만 바꿔야 하므로
            T = np.eye(4)
            setTranslation(T, currentPos - pp.cowPickPosition)
            cow2wld = T @ pp.cowPickConfiguration        
            print("currentPos: ", currentPos)
        else:
            # horizontal dragging
            # Hint: read carefully the following block to implement vertical dragging.
            if cursorOnCowBoundingBox:                  # 커서가 박스 안에 들어가 있을 경우
                ray = screenCoordToRay(window, x, y)
                pp = pickInfo                           # pickInfo => 처음에 클릭한 위치
                p = Plane(np.array((0,1,0)), [0, currentPos[1], 0])    # Plane(normalvec, point)
                # intersectsPlane => 평면과 충돌하는 점 찾기 => 이 plane 이 y좌표가 바뀌어야 함
                c = ray.intersectsPlane(p)                         # ray => 점과 방향
                # c => 만나는 점 (pair<false, point>) , 가까운 점 을 집어넣음
                currentPos = ray.getPoint(c[1])                     # 현재 소의 위치 = pair 에서 뒤의 값 받아줌
                T = np.eye(4)
                setTranslation(T, currentPos - pp.cowPickPosition)
                cow2wld = T @ pp.cowPickConfiguration
                print("p: ", pp.cowPickPosition)
                
    else:               # drag가 되고 있지 않다면
        ray = screenCoordToRay(window, x, y)

        planes = []
        cow = cowModel
        bbmin = cow.bbmin
        bbmax = cow.bbmax

        # cow slab
        planes.append(makePlane(bbmin, bbmax, vector3(0,1,0)))
        planes.append(makePlane(bbmin, bbmax, vector3(0,-1,0)))
        planes.append(makePlane(bbmin, bbmax, vector3(1,0,0)))
        planes.append(makePlane(bbmin, bbmax, vector3(-1,0,0)))
        planes.append(makePlane(bbmin, bbmax, vector3(0,0,1)))
        planes.append(makePlane(bbmin, bbmax, vector3(0,0,-1)))

        o = ray.intersectsPlanes(planes)                        # inserectPoint 찾기
        cursorOnCowBoundingBox = o[0]                           # true false 받아옴
        cowPickPosition = ray.getPoint(o[1])                    # cursor ray 와 만나는 점의 좌표
        
        # 이건 뭐냐? 일단 pass
        cowPickLocalPos = transform(np.linalg.inv(cow2wld), cowPickPosition)        
        pickInfo = PickInfo(o[1], cowPickPosition, cow2wld, cowPickLocalPos)

def screenCoordToRay(window, x, y):
    width, height = glfw.get_window_size(window)

    matProjection = glGetDoublev(GL_PROJECTION_MATRIX).T
    matProjection = matProjection@wld2cam[cameraIndex] # use @ for matrix mult.
    invMatProjection = np.linalg.inv(matProjection)
    # -1<=v.x<1 when 0<=x<width
    # -1<=v.y<1 when 0<=y<height
    vecAfterProjection = vector4(
            (float(x - 0))/(float(width))*2.0-1.0,
            -1*(((float(y - 0))/float(height))*2.0-1.0),
            -10)

    #std::cout<<"cowPosition in clip coordinate (NDC)"<<matProjection*cow2wld.getTranslation()<<std::endl
	
    vecBeforeProjection = position3(invMatProjection @ vecAfterProjection)

    rayOrigin = getTranslation(cam2wld[cameraIndex])
    return Ray(rayOrigin, normalize(vecBeforeProjection - rayOrigin))

def main():
    if not glfw.init():
        print ('GLFW initialization failed')
        sys.exit(-1)
    width = 800
    height = 600
    window = glfw.create_window(width, height, 'PA2_2020060100', None, None)
    if not window:
        glfw.terminate()
        sys.exit(-1)

    glfw.make_context_current(window)
    glfw.set_key_callback(window, onKeyPress)
    glfw.set_mouse_button_callback(window, onMouseButton)
    glfw.set_cursor_pos_callback(window, onMouseDrag)
    glfw.swap_interval(1)

    initialize(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        display()

        glfw.swap_buffers(window)
	
    glfw.terminate()
if __name__ == "__main__":
    main()
