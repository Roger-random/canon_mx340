/* 
 * Quick tool for exploring Canon Pixma MX340
 * 
 * Continuously reads the quadrature encoder reporting rotation of
 * paper feed shaft, plus two photo interrupter sensors associated
 * with paper operations. Reports when the shaft starts or stops
 * rotating, and when sensors change status.
 *
 * At the moment this doesn't work, due to a time threshold problem
 * with making decisions based on a polling time period. (millisPerCheck)
 *
 * If this time is set too short, the program will mistakenly decide
 * the shaft is stopped when it's actually just polling too fast to see
 * motion.
 *
 * If this time is set too long, the program will miss certain quick
 * transitions such as when the shaft stops and immediately reverses
 * direction.
 *
 * In theory there is a range of polling rates between "too short"
 * and "too long". Experimentally, I failed to find such a value.
 *
 * Derived from Encoder Library - Basic Example
 * http://www.pjrc.com/teensy/td_libs_Encoder.html
 *
 * This example code is in the public domain.
 */

#include <Encoder.h>

// For best performance, select two interrupt capable pins on the
// microcontroller. For the ATmega328 on board an Arduino Nano,
// they are pins 2 and 3.
Encoder myEnc(2, 3);

// Pins to read status of photo interrupter sensors. Any digital
// input pin will suffice.
const int paperPin = 6; // Probably reports paper presence
const int gearPin = 8; // Something in a gearbox of yet-unknown purpose

// Time between status checks
unsigned long millisPerCheck = 15;

// When to perform next status check
unsigned long millisNextCheck;

// Variables to track shaft rotating/stopped status.
bool wasStopped;
long stoppedChangePosition;
unsigned long stoppedChangeTime;

// Track previous state so we know when things have changed
long prevPosition;
bool prevPaper;
bool prevGear;

// Flags for detected status
uint8_t changed_rotation_started = 0x01;
uint8_t changed_rotation_stopped = 0x02;
uint8_t changed_paper_sensor     = 0x04;
uint8_t changed_gear_sensor      = 0x08;

void setup() {
  Serial.begin(250000);
  Serial.println("milliseconds,paper,gear,position_change,changed_time,status");

  pinMode(paperPin, INPUT);
  pinMode(gearPin, INPUT);

  prevPosition = myEnc.read();

  millisNextCheck = millis();

  wasStopped = true;
  stoppedChangePosition = prevPosition;
  stoppedChangeTime = millis();

  prevPaper = digitalRead(paperPin);
  prevGear = digitalRead(gearPin);
}

void loop() {
  unsigned long timeStamp = millis();

  if (timeStamp > millisNextCheck) {
    long newPosition = myEnc.read();
    bool newPaper = digitalRead(paperPin);
    bool newGear = digitalRead(gearPin);

    uint8_t changeStatus = 0;

    if (wasStopped) {
      if (0 != (newPosition-prevPosition)) {
        changeStatus |= changed_rotation_started;
      }
    } else {
      if (0 == (newPosition-prevPosition)) {
        changeStatus |= changed_rotation_stopped;
      }
    }

    if (newPaper != prevPaper) {
      changeStatus |= changed_paper_sensor;
    }

    if (newGear != prevGear) {
      changeStatus |= changed_gear_sensor;
    }

    if (0 != changeStatus) {
      Serial.print(timeStamp);
      Serial.print(",");
      Serial.print(newPaper);
      Serial.print(",");
      Serial.print(newGear);
      Serial.print(",");
      Serial.print(newPosition-stoppedChangePosition);
      Serial.print(",");
      Serial.print(timeStamp-stoppedChangeTime);
      Serial.print(",");
      Serial.println(changeStatus);

      if (0 != (changeStatus & (changed_rotation_started | changed_rotation_stopped))) {
        wasStopped = !wasStopped;
        stoppedChangeTime = timeStamp;
        stoppedChangePosition = newPosition;
      }
    }

    prevPaper = newPaper;
    prevGear = newGear;
    prevPosition = newPosition;

    millisNextCheck = timeStamp + millisPerCheck;
  }
}
