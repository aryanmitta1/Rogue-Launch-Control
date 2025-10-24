#include <SoftwareSerial.h>

int potentiometerPin = A0;
int potentiometerVal = 0;

SoftwareSerial XBee(10, 11);         // Define SoftwareSerial pins: RX = 10, TX = 11
 
void setup() {
  Serial.begin(9600);                // Start communication with the PC for debugging
  XBee.begin(9600);                  // Start communication with the XBee module
 
  randomSeed(analogRead(0));         // Seed the random number generator for varied results
}
 
void loop() {
  potentiometerVal = analogRead(potentiometerPin);

      // Generate a random number between 0 and 255
  
  XBee.print('<');                   // Start of transmission marker
  XBee.print(potentiometerVal);          // Send the randomly generated number
  XBee.println('>');                 // End of transmission marker
 
  Serial.print("Sent number: ");     // Debugging output to Serial Monitor
  Serial.println(potentiometerVal);
 
  delay(1000);                       // Delay between sends to avoid flooding
}