Computer Graphics
Programming Assignment2 (Cow roller coaster)
2020060100 고관우

추가한 변수
    animState, animStartTime, animTime, HermiteConversion, CatmullRomCoefficient, controlPoints, isOnclick, currentPos
변경한 함수
    display, onMouseButton, onMouseDrag
 
animState: animation이 진행 중인지 진행 중이지 않는지 구분해주는 변수
animStartTime: animation이 시작될 때 시간을 계산해줘서 controlPoints 의 index에 접근할 때 다음 index로 넘길 수 있게 해준다
animTime: animTime 을 이용해서 index에 접근할 수 있게 한다
HermiteConversion: CatmullRom 을 구현할 때 필요한 행렬
CatmullRomCoefficient: CatmullRom 을 구현할 때 필요한 행렬
controlPoints: 철판의 역할, 점 6개를 받아서 소가 움직이는 경로를 계산할 때 필요한 변수
isOnclick: 처음에 소를 줍는지 안 줍는지 확인하는 변수
currentPos: 소를 클릭하면서 소의 위치를 받아오는 변수, 이 점을 이용해서 VDrag를 할 때 평면을 계산하는데 이용할 수 있다

onMouseDrag:
    우선 이 코드를 고치고 이해함에 있어서 onMouseDrag 함수부터 이해했습니다.
    그 이유는 주석에서 명시된대로 TODO 가 있는 함수 였고, onMouseDrag 함수에서 바닥평면을 재설정 할 수 있고
    소의 정보를 입력 받아올 수 있는 함수기 때문에 이 함수부터 채워넣었습니다.
    여기서 주의해 주었던 내용은 우선 V_DRAG 에서 currentPos 의 좌표를 수정할 때
    x, z 좌표는 수정하면 안되고 오직 y 좌표만 수정해야 했기에 currentPos에서 y좌표만을 수정했습니다.
    또한 H_DRAG 에서 평면을 계산할 때 바닥평면이 변경돼야 하기 때문에, Plane class 를 이용해서 법선벡터와 지나는 점을 이용하여 평면을 수정했습니다.
    그리고 animation이 진행되는 동안 cow가 mouse 방향으로 방향이 계속 수정되기에
    animState == True 일 때 이 함수가 실행되지 않게 했습니다.

onMouseDrag 코드
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

onMouseButton:
    처음에 onMouseButton 함수를 구현할 때에 모든 point 를 찍을 때마다 클릭을 다시 하도록 했었는데
    영상에서 클릭 한번으로 점을 찍은걸로 보여서 isOnclick 변수를 이용해서 처음에 클릭할 때에는 소를 찍는 클릭으로 인식하게 하고
    두번째 찍을 때부터는 controlPoints에 append 하고 찍은 점의 위치에 소를 출력할 수 있도록 했습니다.

onMouseButton 코드 
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
                controlPoints.append(cow2wld.copy())
            print( "Left mouse up\n")
            # start horizontal dragging using mouse-move events.
    elif button == glfw.MOUSE_BUTTON_RIGHT:
        if state == GLFW_DOWN:
            print( "Right mouse click at (%d, %d)\n"%(x,y) )    

display:
    우선 display 함수에서 생각했던 요구사항으로는 glfw.get_time() 함수를 이용해서
    controlPoints의 index에 접근할 수 있도록 하는것과 CatmullRom-Spline 을 구현해서 소를 움직이게 하는 것 이었습니다.
    그래서 glfw.get_time() 을 이용해서 인덱스에 접근하려면
    0~1 / 1~2 / 2~3 ... 이런식으로 구간을 분리하는 것이 중요했는데
    이를 이용하기 위에 animStartTime 을 따로 설정해서 animTime 을 만들어줬습니다.
    또한 list 에서 time 을 index 로 사용하기 위해서는 실수를 정수로 변환하는 과정이 필요했기 때문에
    animTime 을 정수형으로 변환했고, CatmullRom-Spline 을 이용하기위해 점 4개를 받아왔습니다.
    그런다음 animTime 과 HermiteConversion, CatmullRomCoefficient 그리고 점 4개를 이용한 행렬들을 곱해주었고
    이를 translation 함수를 이용해서 적용해 주었습니다.
    여기까지 했을 때 소가 이동은 하지만 rotate를 만족하지 못해서 rotate 를 하기 위해서
    소의 local 축을 변경했습니다. 4*4 행렬에서 3*3 행렬 부분이 회전행렬을 만족하므로
    이동방향을  local의 x축으로 설정하고 global의 y축과 local의 x축을 외적하여 local의 z축을 구하고
    local의 x축과 local의 z축을 외적하여 local의 y축을 계산해주었습니다.
    이 축들을 animCow의 3*3 부분에 적용을 해주어서 rotate가 되도록 해주었습니다.

display 코드
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