/* 
 * Quick tool for exploring Canon Pixma MX340
 * 
 * Continuously reads the quadrature encoder reporting rotation of
 * paper feed shaft, plus two photo interrupter sensors associated
 * with paper operations. Performs no processing, merely report
 * status at regular intervals (millisPerPrint) to the serial port
 * in comma-separated values (CSV) format. Intended for export to
 * some other data analysis software.
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

// When to print to serial port.
unsigned long millisNextPrint;

// Time period between prints
unsigned long millisPerPrint = 10;

void setup() {
  Serial.begin(250000);
  Serial.println("milliseconds,paper,gear,position");
  millisNextPrint = millis();

  pinMode(paperPin, INPUT);
  pinMode(gearPin, INPUT);
}

void loop() {
  long newPosition = myEnc.read();
  if (millis() > millisNextPrint) {
    millisNextPrint += millisPerPrint;
    Serial.print(millis());
    Serial.print(",");
    Serial.print(digitalRead(paperPin));
    Serial.print(",");
    Serial.print(digitalRead(gearPin));
    Serial.print(",");
    Serial.println(newPosition);
  }
}
