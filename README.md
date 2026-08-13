# ARM
YOLO 로봇팔
이 작품은 실시간 객체검출을 통하여 객체를 분류하는 로봇팔의 코드 설명이다.
1. test_yolo_image.py : YOLO 모델을 불러와 지정된 정지된 이미지 파일에서 객체를 탐지하는 코드.
2. test_yolo_webcam.py : 1번 외장 웹캠(인덱스 1)을 연결하여 실시간 비디오 스트리밍 환경에서 객체를 탐지하는 코드.
3. test_yolo_webcam_640x480.py : 2번의 코드에 해상도를 추가.
4. yolo_dc_motor_count_stop.py : '신뢰도(Confidence)'가 아닌 '감지된 객체의 수량'을 기준으로 모터 정지 유무를 결정하는 방식의 코드.
5. yolo_dc_motor_conf_stop.py : 인식 정확도(확률)를 기준으로 자율주행(전진/정지)을 수행하는 코드.
6. yolo_servo_arm_single_test.py : I2C 통신 기반의 PCA9685 모듈을 사용하여 5개의 서보모터(로봇 팔)를 제어하는 코드가 추가, 실시간 스트리밍 방식이 아니라, 카메라를 열어 단 1장의 사진(frame.jpg)만 캡처하여 저장한 뒤 카메라를 즉시 닫고 분석을 진행, 분석 결과 신뢰도가 90% 이상이면 미리 지정된 각도와 시간(time.sleep) 순서대로 로봇 팔을 움직이는 코드.
7. main_integrated_robot_control.py : 실시간 웹캠 탐지 + DC 모터(주행) + 서보모터(로봇 팔)가 모두 통합된 코드
8. yolov5_shape_sorting_arm.py : 루프 내에서 탐지 신뢰도가 90% 이상일 때, 감지된 객체의 클래스가 0번(원형)인지 1번(사각형)인지 구분하는 논리(class_label == 0, class_label == 1)가 포함되어 있고 분류하여 로봇 팔의 동작을 제어한 코드 (프로젝트 시현)
