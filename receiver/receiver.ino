#include <SoftwareSerial.h>         // Include SoftwareSerial library for communication

SoftwareSerial XBee(10, 11);        // Define SoftwareSerial pins: RX = 10, TX = 11

bool started = false;               // True when start marker is detected
bool ended = false;                 // True when end marker is detected
char incomingByte;                  // Storage for each byte read
char msg[4];                        // Array to assemble the incoming message
byte index = 0;                     // Current position in the array

void setup() {
  Serial.begin(9600);               // Start communication with the PC for debugging
  XBee.begin(9600);                 // Start communication with the XBee module
}

void loop() {
  while (XBee.available() > 0) {    // Check if there is data available from the XBee
    incomingByte = XBee.read();     // Read the incoming byte

    if (incomingByte == '<') {      // Detect start of the message
      started = true;
      index = 0;
      msg[index] = '\0';            // Clear the buffer
    }
    else if (incomingByte == '>') { // Detect end of the message
      ended = true;   
      break;                            // Stop reading, process the message
    }
    else if (started && index < 3) {    // Store the byte in msg array if message has started
      msg[index] = incomingByte;
      index++;
      msg[index] = '\0';                      // Null terminate the string
    }
  }

  if (started && ended) {                // If a complete message was received, process it
    int value = atoi(msg);               // Convert the buffer to an integer
    // Debugging output to Serial Monitor
    Serial.println(value);

    started = false;                     // Reset for the next message
    ended = false;
  }
}