# from ultralytics import YOLO
# import cv2
# from matplotlib import pyplot as plt
# import random
# from pathlib import Path

# # Load your trained model
# model = YOLO("best.pt")
# # 0 = default webcam

# model.predict(source=0, conf=0.5, show=True)

# Load test images
# targ_dir = "/content/trash_data/test/images"
# img_paths = list(Path(targ_dir).glob("*.jpg"))
# sample_imgs = random.sample(img_paths, 9)

# for img_path in sample_imgs:
#     # Run inference
#     results = model.predict(img_path, conf=0.6)

#     # Plot results
#     img_with_boxes = results[0].plot()
#     plt.imshow(cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB))
#     plt.axis('off')
#     plt.show()

#     # Print detected classes and bounding boxes
#     for box in results[0].boxes.data:
#         x1, y1, x2, y2, conf, cls = box
#         print(f"Class: {int(cls)}, Confidence: {conf:.2f}, Box: [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")






# from ultralytics import YOLO
# import cv2
# from collections import deque
# import time

# # ----------------- CONFIG -----------------
# MODEL_PATH = "best.pt"
# CAM_INDEX = 0        # iVCam / webcam index
# CONF_THRESH = 0.5    # detection confidence
# CONSEC_FRAMES = 5    # number of consecutive frames to confirm class
# # -----------------------------------------

# # Initialize YOLO model
# model = YOLO(MODEL_PATH)

# # Initialize webcam
# cap = cv2.VideoCapture(CAM_INDEX)

# # Queue to store last N detected classes
# last_classes = deque(maxlen=CONSEC_FRAMES)

# print("Starting live detection... Press 'q' to quit.")

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to grab frame")
#         break

#     # YOLO inference on frame
#     results = model.predict(frame, conf=CONF_THRESH, verbose=False)

#     # Check if any object detected
#     if results[0].boxes:
#         # Get class with highest confidence
#         boxes = results[0].boxes.data  # [x1, y1, x2, y2, conf, cls]
#         cls_ids = [int(b[5]) for b in boxes]
#         confs = [b[4] for b in boxes]
#         # Pick class with max confidence
#         max_conf_idx = confs.index(max(confs))
#         detected_class = cls_ids[max_conf_idx]
#         last_classes.append(detected_class)
#     else:
#         last_classes.append(None)

#     # Check if same class detected for CONSEC_FRAMES
#     if len(last_classes) == CONSEC_FRAMES:
#         # all elements same and not None
#         if last_classes.count(last_classes[0]) == CONSEC_FRAMES and last_classes[0] is not None:
#             final_class_id = last_classes[0]
#             print(f"Final detected class ID: {final_class_id}")
#             last_classes.clear()  # reset queue after confirming

#     # Show frame
#     cv2.imshow("YOLO Live", results[0].plot())
    
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release resources
# cap.release()
# cv2.destroyAllWindows()



from ultralytics import YOLO
import cv2
from collections import deque
import serial
import time

# ----------------- CONFIG -----------------
MODEL_PATH = "best.pt"
CAM_INDEX = 0        # iVCam / webcam index
CONF_THRESH = 0.5    # detection confidence
CONSEC_FRAMES = 5    # number of consecutive frames to confirm class

SERIAL_PORT = 'COM3'  # change to your Arduino port
BAUD_RATE = 9600

BIN_COOLDOWN = 5      # seconds to ignore new signals
BIN_OPEN_TIME = 3     # seconds to keep bin open

# Map class IDs to Arduino signals
# we are sending paper and cardboard to same bin here, we only have 3 bins so we only send signals to arduino for plastic,paper and cardbaord, biodegradable
CLASS_SIGNAL = {
    0: "metal",   
    1: "paper",   # Cardboard
    2: "g",   # Glass
    3: "m",   # Metal
    4: "paper",   # Paper
    5: "plastic"    # Plastic
}
# -----------------------------------------

# Initialize YOLO model
model = YOLO(MODEL_PATH)

# Initialize webcam
cap = cv2.VideoCapture(CAM_INDEX)

# Initialize serial connection
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # allow Arduino to initialize
    print(f"Connected to Arduino on {SERIAL_PORT}")
except Exception as e:
    print(f"Could not connect to Arduino: {e}")
    arduino = None

# Queue to store last N detected classes
last_classes = deque(maxlen=CONSEC_FRAMES)

# Track last signal time
last_signal_time = 0

print("Starting live detection... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # YOLO inference on frame
    results = model.predict(frame, conf=CONF_THRESH, verbose=False)

    # Check if any object detected
    if results[0].boxes:
        boxes = results[0].boxes.data  # [x1, y1, x2, y2, conf, cls]
        cls_ids = [int(b[5]) for b in boxes]
        confs = [b[4] for b in boxes]
        max_conf_idx = confs.index(max(confs))
        detected_class = cls_ids[max_conf_idx]
        last_classes.append(detected_class)
    else:
        last_classes.append(None)

    # Check if same class detected for CONSEC_FRAMES
    if len(last_classes) == CONSEC_FRAMES:
        if last_classes.count(last_classes[0]) == CONSEC_FRAMES and last_classes[0] is not None:
            final_class_id = last_classes[0]
            # Only send signal if BIN_COOLDOWN passed
            if time.time() - last_signal_time >= BIN_COOLDOWN:
                signal = CLASS_SIGNAL.get(final_class_id)
                if signal and arduino:
                    arduino.write(signal.encode())
                    print(f"Sent '{signal}' to Arduino (bin will stay open {BIN_OPEN_TIME}s)")
                    last_signal_time = time.time()
                last_classes.clear()  # reset after sending

    # Show frame
    cv2.imshow("YOLO Live", results[0].plot())

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
if arduino and arduino.is_open:
    arduino.close()
    print("🔌 Arduino connection closed.")
