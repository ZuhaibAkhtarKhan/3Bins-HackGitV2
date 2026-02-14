3bins ♻️🤖
An Agentic AI Smart Bin aimed at solving recycling contamination.

This project uses computer vision to automatically detect and sort waste items into three distinct categories: Trash, Plastic, and Bio/Battery. Unlike standard classifiers, this system integrates a custom-trained vision model with a physical control system to ensure only the correct bin opens.

🚀 Key Features
Custom Vision Brain: Powered by a fine-tuned YOLOv8 model (trained specifically on local waste datasets) for high-speed, offline detection.

Physical Automation: Arduino Mega controller managing 3x Servo motors with "blocking" logic to prevent cross-contamination.

Real-Time Response: Instant classification and actuation (< 3-second cycle).
