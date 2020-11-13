
# coding: utf-8

# In[1]:

import numpy as np
import imutils
import time
import timeit
import dlib
import cv2
import matplotlib.pyplot as plt
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
from threading import Timer
from drow.check_cam_fps import check_fps
import drow.make_train_data as mtd
import drow.light_remover as lr
import drow.ringing_alarm as alarm

class Drowsiness:

    def __init__(self, thema):

        self.thema = thema

        self.OPEN_EAR = 0 #For init_open_ear()
        self.EAR_THRESH = 0 #Threashold value #경계 값

        #2.
        #It doesn't matter what you use instead of a consecutive frame to check out drowsiness state. (ex. timer)
        self.EAR_CONSEC_FRAMES = 20 
        self.COUNTER = 0 #Frames counter.

        #3.
        self.closed_eyes_time = [] #The time eyes were being offed. # 눈을 뜬 시간
        self.TIMER_FLAG = False #Flag to activate 'start_closing' variable, which measures the eyes closing time. 눈을 감는 중인 시간을 측정한다.'start_closing' 변수를 활성화하는 플래그
        self.ALARM_FLAG = False #Flag to check if alarm has ever been triggered. 알람이 작동 되었던 적이 있으면 체크하는 플래그

        #4. 
        self.ALARM_COUNT = 0 #Number of times the total alarm rang. # 총 알람이 울린 횟수
        self.RUNNING_TIME = 0 #Variable to prevent alarm going off continuously. # 지속적으로 알람이 울리지 않도록 하는 변수

        #5.    
        self.PREV_TERM = 0 #Variable to measure the time eyes were being opened until the alarm rang. # 알람이 울릴 때까지 눈이 뜨는 시간을 측정한 변수

        self.CLOSE_EAR = 0

        self.both_ear = 0

        self.trigger = True

        self.th_open = None
        self.th_close = None

        self.frame = None
        self.check = False

        self.camera = None

        self.thread = Thread(target=self.main_run, args=())
        self.thread.daemon = True
        self.thread.start()
        

    def eye_aspect_ratio(self,eye) : #본래 눈의 좌표 값들은 각각 6개씩 존재한다. 37~42, 43~48
        A = dist.euclidean(eye[1], eye[5]) # (38,42), (44,48)
        B = dist.euclidean(eye[2], eye[4]) # (45,47), (39,41)
        # 윗 눈꺼플과 아랫 눈꺼풀 사이의 거리
        C = dist.euclidean(eye[0], eye[3]) #(43,46),(37,40) 눈 끝끼리의 거리
        # 각 눈좌표들 사이의 거리를 구한다. 이를 통해서 눈을 감았는지 감지 않았는지 판단하는 듯 하다.
        ear = (A + B) / (2.0 * C)
        return ear
        
    def init_open_ear(self) :
        time.sleep(3)
        print("open init time sleep")
        ear_list = []
        th_message1 = Thread(target = self.open_message)
        th_message1.deamon = True
        th_message1.start()
        for i in range(7) :
            ear_list.append(self.both_ear)
            time.sleep(1)
        # global OPEN_EAR
        self.OPEN_EAR = sum(ear_list) / len(ear_list)
        print("open list =", ear_list, "\nOPEN_EAR =", self.OPEN_EAR, "\n")

    def init_close_ear(self) : 
        time.sleep(2)
        (self.th_open).join()
        time.sleep(3)
        print("close init time sleep")
        ear_list = []
        th_message2 = Thread(target = self.close_message)
        th_message2.deamon = True
        th_message2.start()
        time.sleep(1)
        for i in range(7) :
            ear_list.append(self.both_ear)
            time.sleep(1)
        self.CLOSE_EAR = sum(ear_list) / len(ear_list)
        # global EAR_THRESH
        self.EAR_THRESH = (((self.OPEN_EAR - self.CLOSE_EAR) / 2) + self.CLOSE_EAR) #EAR_THRESH means 50% of the being opened eyes state
        print("close list =", ear_list, "\nCLOSE_EAR =", self.CLOSE_EAR, "\n")
        print("The last EAR_THRESH's value :",self.EAR_THRESH, "\n")

    # def init_message(self, name) :
    #     print("init_message")
    #     alarm.sound_alarm("drow/"+name)

    def open_message(self):
        print("open_message")
        alarm.sound_alarm("drow/open.mp3")

    def close_message(self):
        print('close_message')
        alarm.sound_alarm('drow/close.mp3')

    def wake_up(self):
        print('wake up')
        if self.thema != None:
            alarm.sound_alarm(self.thema)

    #####################################################################################################################
    #1. Variables for checking EAR.
    #2. Variables for detecting if user is asleep.
    #3. When the alarm rings, measure the time eyes are being closed.
    #4. When the alarm is rang, count the number of times it is rang, and prevent the alarm from ringing continuously.
    #5. We should count the time eyes are being opened for data labeling.
    #6. Variables for trained data generation and calculation fps.
    #7. Detect face & eyes.
    #8. Run the cam.
    #9. Threads to run the functions in which determine the EAR_THRESH. 


    def main_run(self):
    #1.
        #6. make trained data 
        np.random.seed(9)
        power, nomal, short = mtd.start(25) #actually this three values aren't used now. (if you use this, you can do the plotting)
        #The array the actual test data is placed.
        test_data = [] #테스트 데이터
        #The array the actual labeld data of test data is placed.
        result_data = [] # 테스트 데이터의 실제 라벨 데이터가 배치 된 배열
        #For calculate fps
        prev_time = 0

        #7. 
        print("loading facial landmark predictor...")
        detector = dlib.get_frontal_face_detector() #얼굴을 감지하는 감지기
        predictor = dlib.shape_predictor("drow/shape_predictor_68_face_landmarks.dat") # 이 프로젝트에서 얼굴에 각 점을 표시하는 모델. rio 얼굴에 대한 68개의 점의 좌표 값을 가지고 있다.

        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"] # 얼굴에 관한 랜드마크 중에서 왼쪽 눈을 선택. 각 shape 내에서 어디서부터 시작해서 어디까지가 눈인지 위치 값들이 들어있다.
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"] # 얼굴에 관한 랜드마크 중에서 오른쪽 눈을 선택
        # 키값을 이용해서 얼굴중 키에 해당하는 값의 좌표를 가지고 온다.

        #8.
        print("starting video stream thread...")

        vs = cv2.VideoCapture(0)

        self.camera = vs
        time.sleep(1.0)

        #9.
        self.th_open = Thread(target = self.init_open_ear)
        self.th_open.deamon = True
        self.th_open.start()
        self.th_close = Thread(target = self.init_close_ear)
        self.th_close.deamon = True
        self.th_close.start()

        FPS = 60 # 현재 원하는  프레임 수
        prev_time = 0
        #####################################################################################################################
        try:
            while self.trigger is not None:

                ret, frame = vs.read()
                current_time = time.time() - prev_time

                if (ret is not True) or (current_time <= 1./ FPS):
                    continue

                prev_time = time.time()

                frame = cv2.flip(frame,1)
                
                L, gray = lr.light_removing(frame)
                
                rects = detector(gray,0)
                
                for rect in rects: #인식된 얼굴 갯 수 만큼
                    shape = predictor(gray, rect) # 인식된 얼굴의 68개의 좌표값들을 얻는다.
                    shape = face_utils.shape_to_np(shape) # 68개의 좌표 값을 넘파이 배열로 받아온다.

                    leftEye = shape[lStart:lEnd] # 68개의 좌표 중에서 왼쪽 눈에 해당하는 좌표 값들만 모은다.
                    rightEye = shape[rStart:rEnd] # 68개의 좌표 값 중에서 오른쪽 눈에 해당하는 좌표 값들만 모은다.
                    # 눈을 감았는지 확인하기 위한 자료
                    leftEAR = self.eye_aspect_ratio(leftEye)
                    rightEAR = self.eye_aspect_ratio(rightEye)

                    #(leftEAR + rightEAR) / 2 => both_ear. 
                    self.both_ear = (leftEAR + rightEAR) * 500  #I multiplied by 1000 to enlarge the scope.
                    # 눈을 감았는지 떴는지에 대한 확실한 근거

                    leftEyeHull = cv2.convexHull(leftEye)
                    rightEyeHull = cv2.convexHull(rightEye)
                    cv2.drawContours(frame, [leftEyeHull], -1, (0,255,0), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0,255,0), 1) #블록 껍질을 계삲하고 오버레이에 껍질을 그린다. 눈주위에.
                    

                    if self.both_ear < self.EAR_THRESH : #경계값과 비교해서 눈을 감았는지 떴는지 판단, 경계 값보다 작을 때, 즉 눈을 감았을 때
                        if not self.TIMER_FLAG: #처음으로 눈을 감았다고 인식 했을 때만
                            start_closing = timeit.default_timer()
                            self.TIMER_FLAG = True
                        self.COUNTER += 1 #눈을 감은 횟수를 증가 시킨다.

                        if self.COUNTER >= self.EAR_CONSEC_FRAMES: # 눈을 감은 횟수가 20번 보다 많으면.

                            mid_closing = timeit.default_timer() # mid 라는 단어가 들어간거 보면 중간 단계의 눈을 감고 있는 시간을 체크해 주는 건가.
                            closing_time = round((mid_closing-start_closing),3) # 카메라를 통해서 지켜 보았을 때 존다고 판단한 횟수가 20번이 넘으면 얼마나 눈을 감고 있었는지 시간을 구한다.
                            #정확히 존다고 판단이 되기까지의 시간

                            #졸고 있다고 판단했고 아직 눈을 감은 채이다.
                            if closing_time >= self.RUNNING_TIME: #졸았다는 가정하에, 졸았다고 판단하기까지의 시간이 러닝 타임보다 클때, 애초에 눈을 계속 감고 있으면 러닝 타임 보다 커질 것이다. 그러면 계속 알람은 울리게 된다.
                                if self.RUNNING_TIME == 0 : # 맨 처음 졸았을 때인가. #처음 으로 알람이 울릴때
                                    CUR_TERM = timeit.default_timer() # 처음 부터 해서 졸기까지의 텀을 아래에서 계산한다.
                                    OPENED_EYES_TIME = round((CUR_TERM - self.PREV_TERM),3) #졸아서 알람이 울리고 완전히 꺼진 뒤로 부터 얼마나 걸렸는지
                                    self.PREV_TERM = CUR_TERM #졸았던 시간 기록, 정확히는 처음 알람을 울리기로 정한 시간을 기록
                                    self.RUNNING_TIME = 1.75 #알람이 울리는 시간 설정

                                self.RUNNING_TIME += 2
                                self.ALARM_FLAG = True #알람을 킬수 있게 플래그를 참으로 변경
                                self.ALARM_COUNT += 1 #알람 횟수를 1 늘린다.

                                print("{0}st ALARM".format(self.ALARM_COUNT)) # 알람이 몇번째 인지
                                print("The time eyes is being opened before the alarm went off :", OPENED_EYES_TIME) #알람이 울리기 전에 눈이 뜨는 시간
                                print("closing time :", closing_time) # 눈을 감고 있는 시간
                                t = Thread(target = self.wake_up, args = ()) #알람을 울리는 쓰레드를 작동 시킨다.
                                t.deamon = True
                                t.start()
                            cv2.rectangle(frame, (rect.left(), rect.top()), (rect.right(), rect.bottom()),(0, 0, 255), 3)
                            cv2.putText(frame, "You are Drowsy", (300,130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                        

                    else : #졸지 않았을때, 경계값보다 클 때
                        self.COUNTER = 0 #눈을 감았을때의 세는 카운터 리셋. 눈을 계속 감고 있어야 졸았다고 판단한다. 눈이 떠져서 경계값이 넘어가면 카운터가 리셋된다. 이 카운터가 20이 넘어가야 졸았다고 판단한다.
                        self.TIMER_FLAG = False #타이머 플래그를 리셋한다.
                        self.RUNNING_TIME = 0    # 러닝 타임 역시 리셋

                        if self.ALARM_FLAG : #알람 플래그가 참일때만, 즉 알람이 울고있다라는 건가
                            end_closing = timeit.default_timer()
                            (self.closed_eyes_time).append(round((end_closing-start_closing),3)) #즉 눈을 뜬 시간이다. 알람이 울리고 눈을 뜬 시간. 좀더 정확히는 전체 적으로 눈을 감고있던 시간이다.
                            print("The time eyes were being offed :", (self.closed_eyes_time))

                        self.ALARM_FLAG = False #알람이 울리지 않게 알람 플래그 값을 거짓으로 변경. 좀더 정확히는 자고 있던중 눈을 감고 있는 시간을 계산하는 등의 계산에 영향을 주지 않게 false로 변경한다.

                        cv2.putText(frame, "EAR : {:.2f}".format(self.both_ear), (300,130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,30,20), 2)
                    #인식된 얼굴에 한해서 눈을 감고 있나 뜨고 있나에 대한 눈꺼풀 사이의 거리를 표시해 준다.

                ret, jpeg = cv2.imencode('.jpg', frame)
                self.frame = jpeg
                self.check = True
            
        except Exception as ex:
            print('let out',ex)



    def get_frame(self):
        return (self.frame).tobytes()
    
    # def start_main_thread(self):
        
    def stop(self):
        self.trigger = None
        self.camera.release()
        self.thema = None