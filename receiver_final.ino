#include <SoftwareSerial.h>

// software srial rx tx for xbee
SoftwareSerial XBee(10, 11);

//buffers for receiving data
const byte numChars = 64;
char receivedChars[numChars];
boolean newData = false;

void setup() {
  Serial.begin(9600); 
  XBee.begin(9600);
  
}

void loop() {
  recvWithStartEndMarkers();
  if (newData == true) {
    processAndSendToPython();
    newData = false;
  }
}

//parses data in <> format
void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (XBee.available() > 0 && newData == false) {
    rc = XBee.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      } else {
        receivedChars[ndx] = '\0'; // Terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

//function to parse the data, REORDER IT, and send to Python
void processAndSendToPython() {
  char * strtokIndx; // used by strtok() as an index

  //Altitude (First item sent by Transmitter)
  strtokIndx = strtok(receivedChars, ",");
  if (strtokIndx == NULL) return; // Error check
  float altitude = atof(strtokIndx);

  //Pressure(Second item sent by Transmitter)
  strtokIndx = strtok(NULL, ",");
  if (strtokIndx == NULL) return;
  float pressure = atof(strtokIndx);

  //Temp (Third item sent by Transmitter)
  strtokIndx = strtok(NULL, ",");
  if (strtokIndx == NULL) return;
  float temperature = atof(strtokIndx);

  // -----------------------------------------------------
  // Python app expects: Pressure, Altitude, Temperature
  // -----------------------------------------------------
  
  Serial.print(pressure, 2);
  Serial.print(",");
  Serial.print(altitude, 2);
  Serial.print(",");
  Serial.println(temperature, 2); //needs the newline 
}