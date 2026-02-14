#include <Servo.h>

// 1. Create Servo Objects
Servo servoPlastic; // Pin 2
Servo servoPaper;   // Pin 3
Servo servoMetal;   // Pin 4

// 2. Define Pins
const int pinPlastic = 2;
const int pinPaper   = 3;
const int pinMetal   = 4;

void setup() {
  Serial.begin(9600);
  servoPlastic.attach(pinPlastic);
  servoPaper.attach(pinPaper);
  servoMetal.attach(pinMetal);

  // Close all bins initially
  servoPlastic.write(0);
  servoPaper.write(0);
  servoMetal.write(0);

  Serial.println("System Ready. Waiting for 'plastic', 'paper', or 'metal'.");
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming data until a newline character
    String command = Serial.readStringUntil('\n');
    
    // CRITICAL: Remove hidden whitespace (like "\r" or " ")
    command.trim(); 

    if (command == "plastic") {
      activateBin(servoPlastic, "Plastic");
    } 
    else if (command == "paper") {
      activateBin(servoPaper, "Paper");
    } 
    else if (command == "metal") {
      activateBin(servoMetal, "Metal");
    }
  }
}

void activateBin(Servo &activeServo, String binName) {
  Serial.print("Opening ");
  Serial.println(binName);

  // 1. Open Lid
  activeServo.write(90);

  // 2. Wait 3 Seconds (Block other commands)
  delay(3000); 

  // 3. Close Lid
  activeServo.write(0);
  Serial.println("Closing...");
  
  delay(500); // Allow physical closing time

  // 4. Clear the buffer 
  // (Prevents queued commands from firing immediately after)
  while(Serial.available() > 0) {
    char junk = Serial.read(); 
  }
}