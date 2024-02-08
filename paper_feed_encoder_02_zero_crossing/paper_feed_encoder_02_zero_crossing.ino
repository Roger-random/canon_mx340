/* 
 * Quick tool for exploring Canon Pixma MX340
 * 
 * Continuously reads the quadrature encoder reporting rotation of
 * paper feed shaft, plus two photo interrupter sensors associated
 * with paper operations. Reports when the shaft starts or stops
 * rotating, and when sensors change status.
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

void setup() {
  Serial.begin(250000);
  Serial.println("milliseconds,paper,gear,position_change,changed_time,status");

  pinMode(paperPin, INPUT);
  pinMode(gearPin, INPUT);
}

void loop() {
  unsigned long timeStamp = millis();

  long newPosition = myEnc.read();
  bool newPaper = digitalRead(paperPin);
  bool newGear = digitalRead(gearPin);
}
