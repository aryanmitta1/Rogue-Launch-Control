#include <SoftwareSerial.h>

int data[5];

SoftwareSerial XBee(10, 11);  // RX = 10, TX = 11

void setup() {
  Serial.begin(9600);
  XBee.begin(9600);
}

void loop() {
  int pressure = random(1, 10);
  int altitude = random(1, 10);
  int temperature = random(1, 10);
  int latitude = random(1, 10);
  int longitude = random(1, 10);

  data[0] = pressure;
  data[1] = altitude;
  data[2] = temperature;
  data[3] = latitude;
  data[4] = longitude;

  // Construct and send message: <6,6,8,8,7>
  XBee.print('<');
  Serial.print('<');
  for (int i = 0; i < 5; i++) {
    XBee.print(data[i]);
    Serial.print(data[i]);
    if (i < 4) {
      XBee.print(',');
      Serial.print(',');
    }
  }
  XBee.print('>');
  Serial.print('>');
  XBee.println();   // newline for clarity between messages
  Serial.println(); // newline for clarity between messages

  delay(1000);
}
