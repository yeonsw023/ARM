import cv2
from ultralytics import YOLO
import numpy as np
from PIL import Image
import RPi.GPIO as GPIO  # 라즈베리파이의 GPIO 핀 제어

# 사용자 지정 YOLO 모델 로드
model_path = '/home/yeonsw/Arm/best.pt'  # 라즈베리파이 경로는 슬래시(/) 사용
model = YOLO(model_path)

# GPIO 설정
GPIO.setmode(GPIO.BCM)

# L298N 모터 제어 핀 설정 (모터 1과 모터 2에 각각 2개의 핀 사용)
motor1_in1 = 17  # 모터 1 IN1 핀
motor1_in2 = 27  # 모터 1 IN2 핀
motor2_in1 = 22  # 모터 2 IN1 핀
motor2_in2 = 23  # 모터 2 IN2 핀
ena = 24  # 모터 1 속도 제어 (ENA)
enb = 25  # 모터 2 속도 제어 (ENB)

# 모터 핀 출력 설정
GPIO.setup(motor1_in1, GPIO.OUT)
GPIO.setup(motor1_in2, GPIO.OUT)
GPIO.setup(motor2_in1, GPIO.OUT)
GPIO.setup(motor2_in2, GPIO.OUT)
GPIO.setup(ena, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)

# PWM 초기화
pwm_ena = GPIO.PWM(ena, 1000)  # PWM 주파수 1kHz
pwm_enb = GPIO.PWM(enb, 1000)  # PWM 주파수 1kHz
pwm_ena.start(0)  # 모터 속도 0%로 초기화
pwm_enb.start(0)  # 모터 속도 0%로 초기화

def stop_motors():
    GPIO.output(motor1_in1, GPIO.LOW)
    GPIO.output(motor1_in2, GPIO.LOW)
    GPIO.output(motor2_in1, GPIO.LOW)
    GPIO.output(motor2_in2, GPIO.LOW)

def start_motors():
    GPIO.output(motor1_in1, GPIO.HIGH)  # 모터 1 전방 회전
    GPIO.output(motor1_in2, GPIO.LOW)
    GPIO.output(motor2_in1, GPIO.HIGH)  # 모터 2 전방 회전
    GPIO.output(motor2_in2, GPIO.LOW)

def detect_objects(frame):
    # OpenCV 프레임을 PIL 이미지로 변환
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # 객체 검출 수행
    results = model(img)

    # 감지된 객체가 있으면 모터를 멈추고, 없으면 모터를 작동시킴
    if len(results[0].boxes.data) > 30:  # 감지된 객체가 있을 때
        stop_motors()  # 물체가 감지되면 모터 멈춤
        for det in results[0].boxes.data:
            x1, y1, x2, y2, conf, cls = det.tolist()
            label = model.names[int(cls)]

            # 감지된 객체 주위에 박스 및 레이블 표시
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f'{label} {conf:.2f}', (int(x1), int(y1) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    else:
        start_motors()  # 물체가 없으면 모터 작동

    return frame

# 웹캠 스트리밍
cap = cv2.VideoCapture(0)  # 보통 라즈베리파이에서는 0번 장치

if not cap.isOpened():
    print("Error: Camera not accessible")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame")
        break
    
    frame = detect_objects(frame)
    
    cv2.imshow('Real-time Object Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# GPIO 정리
GPIO.cleanup()
