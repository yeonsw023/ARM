import torch
import numpy as np
import cv2
import Adafruit_PCA9685
import time

model = torch.hub.load('ultralytics/yolov5', 'custom', path='학습시킨 pt파일 경로')

robot_handle=Adafruit_PCA9685.PCA9685()
servoMin=150 #servo motor는 mg996을 사용
servoMax=550

def map(value,min_angle,max_angle,min_pulse,max_pulse):
    angle_range=max_angle-min_angle
    pulse_range=max_pulse-min_pulse
    scale_factor=float(angle_range)/float(pulse_range)
    return min_pulse+(value/scale_factor)

def set_angle(channel,angle):
    pulse=int(map(angle,0,180,servoMin,servoMax))
    robot_handle.set_pwm(channel,0,pulse)
    
robot_handle.set_pwm_freq(50)

set_angle(0,100)
set_angle(5,160)
set_angle(1,135)
set_angle(2,45)
set_angle(4,140)

while True:
    cap = cv2.VideoCapture(0) # 외장 카메라의 경우는 1, 보통은 0을 사
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    ret, frame = cap.read()
    cv2.imwrite('frame.jpg', frame)

    cap.release()
    cv2.destroyAllWindows()

    img = cv2.imread('frame.jpg')
    results = model(img)

    confidence = 0.0
    class_label = -1

    for detection in results.xyxy[0]:
        class_label = int(detection[5])
        confidence = detection[4]

        if confidence >= 0.9:
            print("Class Label:", class_label)
            print("Confidence:", confidence)
            print("객체가 인식되었습니다.")
        
            if class_label == 0:  # circle의 클래스 레이블
                    object_circle_detected = True
            elif class_label == 1:  # square의 클래스 레이블
                    object_square_detected = True
        elif confidence < 0.9:
             print("객체가 인식되지 않았습니다.")

    if class_label == -1:
        print("객체가 인식되지 않았습니다.")

    set_angle(0,100)
    time.sleep(2)
    set_angle(5,160)
    time.sleep(2)
    set_angle(1,150)
    time.sleep(2)
    set_angle(2,45)
    set_angle(4,140)
    time.sleep(2)
    set_angle(5,100)
    time.sleep(2)
    set_angle(1,90)
    time.sleep(2)

    if confidence >= 0.9:
        set_angle(0,10)
        time.sleep(2)

    elif class_label == -1 or confidence < 0.9:
        set_angle(0,170)
        time.sleep(2)

    set_angle(1,135)
    time.sleep(2)
    set_angle(5,160)
    time.sleep(2)
    set_angle(1,80)
    time.sleep(2)
    set_angle(4,90)
    time.sleep(2)
