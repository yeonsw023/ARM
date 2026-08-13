import cv2
from ultralytics import YOLO
import numpy as np
from PIL import Image

# 사용자 지정 YOLO 모델 로드 (YOLOv8 사용)
model_path = r'C:\\Arm\\best.pt'
model = YOLO(model_path)  # YOLOv8 모델 로드

def detect_objects(frame):
    # OpenCV 프레임을 PIL 이미지로 변환
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # 객체 검출 수행
    results = model(img)

    # 결과에서 필요한 정보 추출
    for det in results[0].boxes.data:  # YOLOv8에서의 방식
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]

        # 감지된 객체 주위에 박스 및 레이블 표시
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f'{label} {conf:.2f}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame

# 웹캠 스트리밍
cap = cv2.VideoCapture(1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 객체 감지 수행
    frame = detect_objects(frame)
    
    # 화면에 출력
    cv2.imshow('Real-time Object Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()