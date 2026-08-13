import cv2
from ultralytics import YOLO
from PIL import Image
import RPi.GPIO as GPIO
import time

# YOLO 모델 로드
model = YOLO('/home/pi/yolo_project/best.pt')  # 경로는 자신의 모델 경로로 수정

# ------------------- 모터 설정 ------------------- #
GPIO.setmode(GPIO.BCM)

# 모터 제어 핀 설정
IN1, IN2 = 17, 27  # 모터1
IN3, IN4 = 22, 23  # 모터2
ENA, ENB = 18, 13  # PWM 핀 (속도 제어)

# GPIO 핀 출력 설정
for pin in [IN1, IN2, IN3, IN4, ENA, ENB]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# PWM 설정 (1000Hz)
pwmA = GPIO.PWM(ENA, 1000)
pwmB = GPIO.PWM(ENB, 1000)
pwmA.start(0)
pwmB.start(0)

def motor_forward(speed=50):
    # 전진
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)

def motor_stop():
    # 정지
    for pin in [IN1, IN2, IN3, IN4]:
        GPIO.output(pin, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

# ------------------- 객체 탐지 ------------------- #
def detect_objects(frame):
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    results = model(img)

    detected = False
    for det in results[0].boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f'{label} {conf:.2f}', (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # ✅ 99% 이상일 때만 감지된 것으로 처리
        if conf >= 0.90:
            detected = True

    return frame, detected

# ------------------- 메인 루프 ------------------- #
cap = cv2.VideoCapture(0)  # 카메라 번호 조정 필요 시 변경
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, found = detect_objects(frame)

        if found:
            motor_stop()
        else:
            motor_forward(60)  # 감지 안되면 전진

        cv2.imshow('YOLOv8 Object Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    pwmA.stop()
    pwmB.stop()
    GPIO.cleanup()
