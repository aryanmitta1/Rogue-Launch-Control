# Rogue Launch Control

A comprehensive GUI application for rocket launch control with real-time monitoring and simulation capabilities.

## Features

GUI can monitor pressure in real time with a live graph . There is a display for apogee, height, velocity, and flight time as well (let me know if I should add more). There is a color-coded status for system readiness. 10Hz update frequency (100ms intervals). Currently, Pressure, Altitude, and Temperature are implemented to be read from a serial stream (which would be a receiver arduino device). GPS display potentially may be implemented at a later point. 

This python program expects a specific format of Serial input from a receiver microcontroller which actually sends and receives data from the rocket.
(ex: OUTPUT: 100,200,300 where the first value gets taken as pressure, second and third as coordinates). This program is reponsible for parsing the receiver's serial output and displaying the telemtry data nicely.

Features:
- Pressure vs Time graph
- Height vs Time graph
- Real-time data displays (Including Tank Pressure, Temperature, Altitude)
- Status indicators

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- matplotlib >= 3.5.0
- numpy >= 1.21.0
- pillow >= 9.0.0
