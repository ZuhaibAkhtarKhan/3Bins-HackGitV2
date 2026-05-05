3bins ♻️🤖
An AI Smart Bin aimed at solving recycling contamination.


https://github.com/user-attachments/assets/1182e42d-5c4d-4108-94bc-22e89d2f365d


This project uses computer vision to automatically detect and sort waste items into six distinct categories: cardboards, paper (tho carboard and plastic will go to the same bin), Plastic and Biodegradable. This system integrates a custom-trained vision model with a physical control system to ensure only the correct bin opens.

🚀 Key Features
Custom Vision Brain: Powered by a fine-tuned YOLOv8 model (trained specifically on local waste datasets) for high-speed, offline detection.

Physical Automation: Arduino Mega controller managing 3x Servo motors with "blocking" logic to prevent cross-contamination.

Real-Time Response: Instant classification and actuation (< 3-second cycle).

Link to canva slide: https://www.canva.com/design/DAHBUyTU5Ag/a9snx7nCTYFi_zxcMvhosA/edit?utm_content=DAHBUyTU5Ag&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
