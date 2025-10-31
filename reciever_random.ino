#include <SoftwareSerial.h>
#include <Servo.h>

SoftwareSerial XBee(10, 11); // RX, TX

void setup() {
  Serial.begin(9600);
  XBee.begin(9600);
}

void loop() {
  // Check if there’s data available from the XBee
  if (XBee.available()) {
    // Read a full message between '<' and '>'
    String message = XBee.readStringUntil('>'); // Read until end marker
    int startIdx = message.indexOf('<');
    
    // Extract only the part inside < >
    if (startIdx != -1) {
      message = message.substring(startIdx + 1);
      message.trim();
      
      // Print the clean message (e.g. 6,6,8,8,7)
      Serial.print('<');
      Serial.print(message);
      Serial.println('>');
    }
  }
}
