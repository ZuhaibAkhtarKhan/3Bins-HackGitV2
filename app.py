from flask import Flask, render_template, jsonify
from ultralytics import YOLO
import cv2
from collections import deque
import serial
import time
import os
import threading

app = Flask(__name__)

# ---------------- CONFIG ----------------
MODEL_PATH = "best.pt"
CONF_THRESH = 0.5
CONSEC_FRAMES = 2

SERIAL_PORT = "COM3"
BAUD_RATE = 9600

BIN_COOLDOWN = 5
LOG_FILE = "signals.txt"

# we are sending paper and cardboard to same bin here, we only have 3 bins so we only send signals to arduino
CLASS_SIGNAL = {
    5: "plastic",
    1: "paper",
    4: "paper",
    0: "metal"
}
# ----------------------------------------

model = YOLO(MODEL_PATH)
last_classes = deque(maxlen=CONSEC_FRAMES)
last_signal_time = 0
current_bin = None
running = False

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Arduino Connected")
except:
    arduino = None
    print("Arduino NOT connected")


def log_signal(bin_name):
    with open(LOG_FILE, "a") as f:
        f.write(bin_name + "\n")


def run_detection():
    global last_signal_time, current_bin, running

    cap = cv2.VideoCapture(0)
    cap.set(3, 480)
    cap.set(4, 360)

    print("Detection started")

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, conf=CONF_THRESH, verbose=False)

        if results[0].boxes:
            boxes = results[0].boxes.data
            cls_ids = [int(b[5]) for b in boxes]
            confs = [b[4] for b in boxes]
            detected_class = cls_ids[confs.index(max(confs))]
            last_classes.append(detected_class)
        else:
            last_classes.append(None)

        if len(last_classes) == CONSEC_FRAMES:
            if last_classes.count(last_classes[0]) == CONSEC_FRAMES and last_classes[0] is not None:
                if time.time() - last_signal_time >= BIN_COOLDOWN:

                    bin_name = CLASS_SIGNAL.get(last_classes[0])
                    if bin_name:
                        current_bin = bin_name
                        log_signal(bin_name)

                        if arduino:
                            arduino.write(bin_name.encode())

                        last_signal_time = time.time()

                last_classes.clear()

        annotated_frame = results[0].plot()
        cv2.imshow("YOLO Detection", annotated_frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    running = False


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/start')
def start():
    global running
    if not running:
        running = True
        thread = threading.Thread(target=run_detection)
        thread.start()
    return "Started"


@app.route('/stats')
def stats():
    counts = {"plastic": 0, "paper": 0, "metal": 0}

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                name = line.strip()
                if name in counts:
                    counts[name] += 1

    total = sum(counts.values())

    percentages = {}
    for k in counts:
        percentages[k] = round((counts[k] / total) * 100, 2) if total > 0 else 0

    global current_bin
    temp = current_bin
    current_bin = None

    return jsonify({
        "counts": counts,
        "percentages": percentages,
        "active": temp
    })


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
