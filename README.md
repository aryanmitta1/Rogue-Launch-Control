# Rogue Launch Control

A comprehensive GUI application for rocket launch control with real-time monitoring and smart display.

## Features

GUI can monitor pressure in real time with a live graph . There is a display for apogee, height, velocity, and data collection runtime. There is a color-coded status for system readiness. 10Hz update frequency (100ms intervals). Currently, Pressure, Altitude, and Temperature are implemented to be read from a serial stream (which would be a receiver arduino device). GPS display potentially may be implemented at a later point. 

This python app works very closely with an arduino receiver and transmitter (which both use XBees) and their sketches are located in this repo as well. 

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
