from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

def test_yolo_model(model_path, image_path):
    
    model = YOLO(model_path)
    
    
    img = cv2.imread(image_path)
    results = model(img)
    
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    
    for result in results:
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            
            cls_id = int(box.cls[0])
            conf = box.conf[0]
            label = f"{model.names[cls_id]} {conf:.2f}"
            
            
            cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(img_rgb, (x1, y1 - text_h - 5), (x1 + text_w, y1), (0, 0, 0), -1)
            
            
            cv2.putText(img_rgb, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    
    plt.figure(figsize=(12, 8))
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.title("Object Detection Results")
    plt.show()
    

    print("\n[ Detected Objects ]")
    for i, box in enumerate(boxes):
        cls_id = int(box.cls[0])
        conf = box.conf[0]
        print(f"{i+1}. {model.names[cls_id]} (Confidence: {conf:.2f})")

if __name__ == "__main__":
    
    model_path = r'C:\Arm\best.pt'
    image_path = r"C:\Arm\2400019200008_b2.jpg".replace("\\", "/")
    
    
    test_yolo_model(model_path, image_path)
