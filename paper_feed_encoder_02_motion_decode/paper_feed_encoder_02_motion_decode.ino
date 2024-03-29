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

// Time per position threshold. Values above this threshold are slow enough
// to be treated as if stopped.
const long timePerPositionThreshold = 10000;

// How much hisory to keep?
const int historyLength = 2;

// The historical record itself
EncoderPosition history[historyLength];

// Current position in history
int historyCurrent = 0;

// Previous history entry position
int historyPrevious = 0;

// Previous position report
EncoderPosition prevReport;

// Timestamp of previous loop() poll
unsigned long prevTimeStamp;

// Previous state of photo interrupter sensors
bool prevPaper;
bool prevGear;

// Smallest microseconds per encoder value seen recently
long min_us_enc;

void setup() {
  Serial.begin(250000);

  pinMode(paperPin, INPUT);
  pinMode(gearPin, INPUT);

  historyCurrent = 0;
  historyPrevious = 0;

  prevTimeStamp = micros();

  history[historyCurrent].timeStamp = prevTimeStamp;
  history[historyCurrent].position = myEnc.read();
  history[historyCurrent].count = 1;

  Serial.println("timestamp,count,min_us_enc");

  prevReport = history[historyCurrent];
  prevPaper = digitalRead(paperPin);
  prevGear = digitalRead(gearPin);

  min_us_enc = timePerPositionThreshold;
}

// Advance pointers
void advanceHistoryPointers() {
  // Were we tracking a previous history entry separate from current
  // history entry? If so, update separately.
  if (historyPrevious != historyCurrent) {
    historyPrevious = historyCurrent;
  }

  if (historyCurrent == 0) {
    historyCurrent = 1;
  } else {
    historyCurrent = 0;
  }
}

// Encoder+sensor polling loop
void loop() {
  unsigned long timeStamp = micros();

  long newPosition = myEnc.read();
  bool newPaper = digitalRead(paperPin);
  bool newGear = digitalRead(gearPin);

  if ( newPosition == history[historyCurrent].position ) {
    // Encoder position has not changed
    history[historyCurrent].count++;

    if (prevReport.timeStamp < history[historyCurrent].timeStamp &&
        abs(prevReport.position - history[historyCurrent].position) > 10 &&
        (timeStamp - history[historyCurrent].timeStamp) > timePerPositionThreshold) {
      // Encoder position has held for longer than threshold, interpreting as
      // end of movement. Time to print a line of report.
      Serial.print(prevReport.timeStamp);
      Serial.print(",");
      Serial.print(history[historyCurrent].position - prevReport.position);
      Serial.print(",");
      Serial.print(min_us_enc);
      Serial.println("");

      prevReport = history[historyCurrent];
      min_us_enc = timePerPositionThreshold;
    }
  }
  else if ( historyPrevious != historyCurrent &&
            newPosition == history[historyPrevious].position ) {
    // If we have a previous position on record, and we've merely bounced back
    // to that position, collapse 'current' and 'previous' entries together.
    history[historyPrevious].count += history[historyCurrent].count;

    // And continue as if 'historyCurrent' never happened.
    historyCurrent = historyPrevious;
  } else {
    // Calculate microseconds per encoder count. Negative values reflect
    // decrementing encoder count. It does not mean time reversal.
    long us_enc = 
      (long)(timeStamp - history[historyCurrent].timeStamp) /
      (newPosition - history[historyCurrent].position);

    history[historyCurrent].timePerPosition = us_enc;

    if ( abs(us_enc) < abs(min_us_enc)) {
      min_us_enc = us_enc;
    }

    advanceHistoryPointers();

    history[historyCurrent].timeStamp = timeStamp;
    history[historyCurrent].position = newPosition;
    history[historyCurrent].count = 1;
  }

  if (prevPaper != newPaper) {
    Serial.print(timeStamp);
    Serial.print(",paper,");
    Serial.println(newPaper);
  }

  if (prevGear != newGear) {
    Serial.print(timeStamp);
    Serial.print(",gear,");
    Serial.println(newGear);
  }

  prevPaper = newPaper;
  prevGear = newGear;
  prevTimeStamp = timeStamp;
}
