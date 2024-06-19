// This file is to be uploaded to arduino and controlled with test.py
#include <AFMotor.h>

// Constants for motor configuration
const int MOTOR_STEPS_PER_REV = 96;
int MOTOR_SPEED = 10; // Initial speed, can be modified dynamically
const int MOTOR_SPEED_DELTA = 30;

// Motor identifiers
const int MOTOR_1 = 1;
const int MOTOR_2 = 2;

// Stepper motor objects
AF_Stepper motorBlack(MOTOR_STEPS_PER_REV, MOTOR_1);
AF_Stepper motorWhite(MOTOR_STEPS_PER_REV, MOTOR_2);

// Motor state variables
bool motor1Running = false;
bool motor1Forward = true;
bool motor2Running = false;
bool motor2Forward = true;

unsigned long previousMillis = 0;
const long interval = 10; // Interval in milliseconds

void send_motor_info() {
  // Send motor speed information back to Python
  Serial.print("MOTOR_SPEED="); // Start of message indicator
  Serial.println(MOTOR_SPEED);  // Motor speed
}

void initializeMotor(AF_Stepper &motor) {
  motor.setSpeed(MOTOR_SPEED);
  motor.release();
}

void handleSerial() {
  if (Serial.available() > 0) {
    // Read the incoming string
    String command = Serial.readStringUntil('\n');
    command.trim();

    // Process the command
    if (command == "INCREASE_SPEED") {
      MOTOR_SPEED += MOTOR_SPEED_DELTA;
      motorBlack.setSpeed(MOTOR_SPEED);
      motorWhite.setSpeed(MOTOR_SPEED);
      send_motor_info();
    } else if (command == "DECREASE_SPEED") {
      MOTOR_SPEED -= MOTOR_SPEED_DELTA;
      motorBlack.setSpeed(MOTOR_SPEED);
      motorWhite.setSpeed(MOTOR_SPEED);
      send_motor_info();
    } else if (command == "M1F") {
      motor1Forward = true;
      motor1Running = true;
      send_motor_info();
    } else if (command == "M1S") {
      motor1Running = false;
      motorBlack.release();
    } else if (command == "M1R") {
      motor1Forward = false;
      motor1Running = true;
    } else if (command == "M2F") {
      motor2Forward = true;
      motor2Running = true;
    } else if (command == "M2S") {
      motor2Running = false;
      motorWhite.release();
    } else if (command == "M2R") {
      motor2Forward = false;
      motor2Running = true;
    }
  }
}

void motorStep() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    // Step motors based on state variables
    if (motor1Running) {
      motorBlack.onestep(motor1Forward ? FORWARD : BACKWARD, SINGLE);
    }
    if (motor2Running) {
      motorWhite.onestep(motor2Forward ? FORWARD : BACKWARD, SINGLE);
    }
  }
}

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Initialize both motors
  initializeMotor(motorBlack);
  initializeMotor(motorWhite);
}

void loop() {
  handleSerial();
  motorStep();
}
