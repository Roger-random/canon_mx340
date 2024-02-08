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

// Record-keeping structure for tracking activity across multiple encoder
// read operations
typedef struct EncoderPosition 
{
  unsigned long timeStamp;
           long position;
           long count;
           long timePerPosition;
} EncoderPosition;

// How much hisory to keep?
const int historyLength = 10;

// Current position in history
int historyIndex = 0;

// The historical record itself
EncoderPosition history[historyLength];

void setup() {
  Serial.begin(250000);

  pinMode(paperPin, INPUT);
  pinMode(gearPin, INPUT);

  historyIndex = 0;

  history[historyIndex].timeStamp = micros();
  history[historyIndex].position = myEnc.read();
  history[historyIndex].count = 1;

  Serial.println("timestamp,position,count,us_per_position");
}

void loop() {
  unsigned long timeStamp = micros();

  long newPosition = myEnc.read();
  bool newPaper = digitalRead(paperPin);
  bool newGear = digitalRead(gearPin);

  if ( newPosition == history[historyIndex].position ) {
    history[historyIndex].count++;
  } else {
    history[historyIndex].timePerPosition = 0;
    // Limiting timePerPosition for positions held briefly. Otherwise output
    // values are skewed with large numbers that are not interesting.
    if (history[historyIndex].count < 10000) {
      history[historyIndex].timePerPosition = 
        (long)(timeStamp - history[historyIndex].timeStamp) / 
        (newPosition - history[historyIndex].position);
    }

    Serial.print(history[historyIndex].timeStamp);
    Serial.print(",");
    Serial.print(history[historyIndex].position);
    Serial.print(",");
    Serial.print(history[historyIndex].count);
    Serial.print(",");
    Serial.println(history[historyIndex].timePerPosition);

    // Single entry test doesn't change historyIndex yet
    history[historyIndex].timeStamp = timeStamp;
    history[historyIndex].position = newPosition;
    history[historyIndex].count = 1;
  }
}
