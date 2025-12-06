#include <Adafruit_BMP3XX.h>
#include <SoftwareSerial.h>
#define BMP390_I2C_ADDRESS 0x77 


Adafruit_BMP3XX bmp;

SoftwareSerial XBee(10, 11); // Define SoftwareSerial pins: RX = 10, TX = 11

void setup() {
  Serial.begin(9600); // pc connection for debugging
  XBee.begin(9600);   // communication with the XBee module
  
  if (!bmp.begin_I2C(BMP390_I2C_ADDRESS)) {
    Serial.println("Error: BMP390 not detected. Check wiring!");
    while (1); 
  }
  Serial.println("BMP390 Initialized with Adafruit Library.");

}

void loop() {
  // Read the sensor
  if (!bmp.performReading()) {
    Serial.println("Failed to perform reading.");
    return;
  }
  
  float temperature = bmp.temperature; // Temperature in degrees Celsius (°C)
  float pressure = bmp.pressure / 6894.757; // Pressure in PSI
  float altitude = bmp.readAltitude(1013.25); //Altitude inferred based on pressure and sea level pressure (hPa)
  
  // Seding data in order Altitude, Pressure, Temperature
  XBee.print('<'); // Start of transmission marker
  XBee.print(altitude);    // Altitude (Meters)
  XBee.print(','); 
  XBee.print(pressure);    // Pressure (PSI)
  XBee.print(','); 
  XBee.print(temperature); // Temperature (°C)
  XBee.print('>'); 

  
  //Debugging output to Serial Monitor (matching XBee order)
  Serial.print("Sent numbers: "); 
  Serial.print(altitude);
  Serial.print(','); 
  Serial.print(pressure);
  Serial.print(','); 
  Serial.println(temperature);
  
  delay(1000); // Delay between sends
}