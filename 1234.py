import cv2
from ultralytics import YOLO
import numpy as np
from PIL import Image
import RPi.GPIO as GPIO
import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# YOLOv8 모델 로드
model_path = r'/home/yeon/file/Arm/best.pt'
model = YOLO(model_path)

# L298N DC모터 핀 설정
in1, in2 = 17, 27
in3, in4 = 22, 23
enA, enB = 18, 24

GPIO.setmode(GPIO.BCM)
GPIO.setup([in1, in2, in3, in4, enA, enB], GPIO.OUT)

pwmA = GPIO.PWM(enA, 1000)
pwmB = GPIO.PWM(enB, 1000)
pwmA.start(100)
pwmB.start(100)

def stop_dc_motors():
    GPIO.output([in1, in2, in3, in4], GPIO.LOW)

def run_dc_motors():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)

# PCA9685 설정
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50

def set_angle(channel, angle):
    # angle 0~180 → pulse 500~2500us → duty cycle 계산
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 50       # 50 Hz
    pulse_length //= 4096     # 12-bit resolution
    pulse = int((angle * 11 + 500) / pulse_length)
    pca.channels[channel].duty_cycle = pulse * 16  # 12-bit scaling

# 객체 감지 후 서보모터 동작
def stop_and_move_servos():
    print("▶ 객체 감지됨 - 모터 정지 및 서보모터 순차 동작")
    stop_dc_motors()
    time.sleep(2)

    set_angle(1, 100)  # MG996R - 채널 1
    time.sleep(2)

    set_angle(2, 120)  # MG996R - 채널 2
    time.sleep(2)

    set_angle(3, 90)   # SG90    - 채널 3
    time.sleep(2)

    set_angle(4, 30)   # SG90    - 채널 4 (역방향)
    time.sleep(2)

    set_angle(0, 160)  # MG996R - 채널 0
    time.sleep(2)

    set_angle(4, 90)   # SG90    - 채널 4 (정방향 복귀)
    time.sleep(2)

# 객체 감지
def detect_objects(frame):
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    results = model(img)

    detected = False
    for det in results[0].boxes.data:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]
        confidence = float(conf)

        if confidence >= 0.99:
            detected = True

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f'{label} {confidence:.2f}', (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame, detected

# 웹캠 실행
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, detected = detect_objects(frame)

        if detected:
            stop_and_move_servos()
        else:
            run_dc_motors()

        cv2.imshow('Object Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
    pca.deinit()