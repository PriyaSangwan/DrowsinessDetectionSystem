import threading
import numpy as np
import cv2
import dlib
from imutils import face_utils
from pygame import mixer
import time
import pickle as pkl
alarm = 'alarm.wav'
mixer.init()
mixer.music.load(alarm)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("predictor\\shape_predictor_68_face_landmarks.dat")

left_model = pkl.load(open('model\\left_eye_model', 'rb'))
right_model = pkl.load(open('model\\right_eye_model', 'rb'))
left_scale = pkl.load(open('model\\left_eye_scaling_datamodel', 'rb'))
right_scale = pkl.load(open('model\\right_eye_scaling_datamodel', 'rb'))


def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist


def blinked(a, b, c, d, e, f, eye):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)
    lr = [up, down, ratio]
    if eye == 'left':
        x_data = left_scale.transform([lr])
        result = left_model.predict(x_data)
    else:
        x_data = right_scale.transform([lr])
        result = right_model.predict(x_data)
    return result[0]


class Video(threading.Thread):
    status = ''
    sleep = 0
    drowsy = 0
    active = 0
    count = 0
    sleep_count = 0

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.timer_u = time.time()
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_var(self):
        timer_v = time.time()
        time_passed = (timer_v - self.timer_u)
        if self.count != 0:
            time_slept = format((time_passed * self.sleep_count) / self.count, ".3f")
        else:
            time_slept = "Initialising app.."
        return [self.status, time_slept, 'ghor sankat']

    def get_frame(self):
        ret, frame = self.video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        face_frame = frame.copy()
        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            landmarks = predictor(gray, face)
            landmarks = face_utils.shape_to_np(landmarks)
            left_blink = blinked(landmarks[36], landmarks[37], landmarks[38], landmarks[41], landmarks[40],
                                 landmarks[39], 'left')
            right_blink = blinked(landmarks[42], landmarks[43], landmarks[44], landmarks[47], landmarks[46],
                                  landmarks[45], 'right')

            color = (0, 0, 0)
            self.count += 1
            if (left_blink == 0 or right_blink == 0):

                self.sleep += 1
                self.drowsy = 0
                self.active = 0

                if (self.sleep > 6):
                    self.status = "Sleeping !!!"
                    self.sleep_count += 1
                    self.color = (255, 0, 0)
                    if (mixer.music.get_busy() == False): mixer.music.play()
            elif (left_blink == 1 or right_blink == 1):

                self.sleep = 0
                self.active = 0
                self.drowsy += 1
                if (self.drowsy > 6):
                    if (mixer.music.get_busy() == True): mixer.music.stop()
                    self.status = "Drowsy"
                    self.color = (0, 255, 0)
            else:

                self.drowsy = 0
                self.sleep = 0
                self.active += 1
                if (self.active > 6):
                    if (mixer.music.get_busy() == True): mixer.music.stop()
                    self.status = "Active"
                    self.color = (0, 255, 0)
            cv2.putText(frame, self.status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            for n in range(0, 68):
                (x, y) = landmarks[n]
                cv2.circle(face_frame, (x, y), 1, (255, 0, 0), -1)

        ret, jpg = cv2.imencode('.jpg',frame)
        return jpg.tobytes()
