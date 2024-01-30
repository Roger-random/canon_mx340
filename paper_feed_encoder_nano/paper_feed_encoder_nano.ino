/* Encoder Library - Basic Example
 * http://www.pjrc.com/teensy/td_libs_Encoder.html
 *
 * This example code is in the public domain.
 */

#include <Encoder.h>

// Change these two numbers to the pins connected to your encoder.
//   Best Performance: both pins have interrupt capability
//   Good Performance: only the first pin has interrupt capability
//   Low Performance:  neither pin has interrupt capability
Encoder myEnc(2, 3);
//   avoid using pins with LEDs attached

const int paperPin = 6;
const int gearPin = 8;

unsigned long millisNextPrint;
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
