import cv2
import time
from ultralytics import YOLO
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# I2C 버스 설정 (SCL: GPIO3, SDA: GPIO2)
i2c = busio.I2C(SCL, SDA)

# PCA9685 PWM 드라이버 초기화
robot_handle = PCA9685(i2c)

# 서보 제어용 PWM 주파수 설정 (서보는 일반적으로 50Hz 사용)
robot_handle.frequency = 50

# 서보 모터용 PWM 펄스 최소/최대 값 (PCA9685에서 0~4095 범위의 단위)
servoMin = 150   # 0도에 해당하는 펄스 길이
servoMax = 550   # 180도에 해당하는 펄스 길이

# 각도를 서보에 맞는 PWM 펄스 폭으로 변환하는 함수
def map(value, min_angle, max_angle, min_pulse, max_pulse):
    angle_range = max_angle - min_angle
    pulse_range = max_pulse - min_pulse
    scale_factor = float(angle_range) / float(pulse_range)
    return min_pulse + (value / scale_factor)

# 서보 모터의 채널에 특정 각도를 설정하는 함수
def set_angle(channel, angle):
    pulse = int(map(angle, 0, 180, servoMin, servoMax))
    robot_handle.channels[channel].duty_cycle = int(pulse / 4096 * 65535)

# 초기 위치 설정
set_angle(0, 100)
set_angle(1, 120)
set_angle(2, 160)
set_angle(3, 20)
set_angle(4, 150)

# YOLOv8 모델 로드
model = YOLO('/home/yeon/file/Arm/best.pt')

# 카메라에서 이미지 캡처
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ret, frame = cap.read()
cv2.imwrite("frame.jpg", frame)
cap.release()
cv2.destroyAllWindows()

# 이미지에서 객체 탐지
img = cv2.imread("frame.jpg")
results = model(img)

confidence = 0.0
class_label = -1

# YOLOv8의 결과에서 클래스와 신뢰도 추출
if results and results[0].boxes:
    for box in results[0].boxes:
        class_label = int(box.cls[0])
        confidence = float(box.conf[0])

# 조건 충족 시 모터 제어 실행
if confidence >= 0.9:
    print(f"객체가 인식되었습니다. 클래스: {class_label}, 신뢰도: {confidence}")

    set_angle(1, 160)
    time.sleep(1)
    set_angle(4, 90)
    time.sleep(1)
    set_angle(1, 80)
    time.sleep(1)
    set_angle(0, 40)
    time.sleep(1)
    set_angle(1, 140)
    time.sleep(1)
    set_angle(4, 150)
    time.sleep(1)
    set_angle(1, 120)
    time.sleep(1)

# 원래 초기 상태로 복귀
set_angle(0, 100)
set_angle(1, 120)
set_angle(2, 160)
set_angle(3, 20)
set_angle(4, 150)
