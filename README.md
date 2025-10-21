# Rogue Launch Control

A comprehensive GUI application for rocket launch control with real-time monitoring and simulation capabilities.

## Features

GUI can monitor pressure in real time with a live graph (currently, it's random numbers). There is a display for apogee, height, velocity, and flight time as well (let me know if I should add more). There is a color-coded status for system readiness. 10Hz update frequency (100ms intervals).

Features:
- Pressure vs Time graph
- Analog pressure gauge with color-coded needle
- Height vs Time graph
- Real-time data displays
- Status indicators
- Launch control buttons (not sure if will need)

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
