import cv2

# 여러 개의 카메라 장치 확인
for i in range(10):  # 0~9까지 가능한 카메라 인덱스 확인
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"카메라 {i} 사용 가능")
        cap.release()