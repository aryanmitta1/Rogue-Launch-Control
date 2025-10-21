# Rogue Launch Control

A comprehensive GUI application for rocket launch control with real-time monitoring and simulation capabilities.

## Features

- **Real-time Pressure Monitoring**: Live pressure graph and analog gauge display
- **Flight Data Tracking**: Monitor apogee, height, velocity, and flight time
- **Launch Control System**: Arm, launch, and abort functionality with safety checks
- **Visual Status Indicators**: Color-coded status lights for system readiness
- **Simulation Mode**: Random data generation for testing and demonstration
- **Modern Dark Theme**: Professional aerospace-style interface with sleek design

## Design

The application features a modern, professional interface inspired by GitHub's dark theme:

- **Dark Color Scheme**: Deep backgrounds with cyan, blue, and orange accents
- **SF Pro Display Typography**: Clean, modern font throughout
- **Card-based Layout**: Organized sections with subtle borders
- **Flat Design Elements**: Professional buttons and components
- **Consistent Visual Hierarchy**: Clear information architecture

## Screenshots

The application features:
- Pressure vs Time graph (left panel)
- Analog pressure gauge with color-coded needle
- Height vs Time graph (right panel)
- Real-time flight data displays
- System status indicators
- Launch control buttons

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python launch_control.py
   ```

2. **System Operation**:
   - The system starts in simulation mode with random pressure data
   - Click "ARM SYSTEM" to prepare for launch
   - Click "LAUNCH" to initiate the rocket launch sequence
   - Click "ABORT" to cancel the launch if needed

3. **Monitoring**:
   - Watch the pressure gauge and graphs for real-time data
   - Monitor status lights for system readiness
   - Track flight data including apogee and velocity

## Launch Simulation

The application includes a realistic launch simulation with three phases:

1. **Boost Phase** (0-5 seconds): Pressure builds up, rocket ascends
2. **Coast Phase** (5-15 seconds): Pressure decreases, rocket reaches apogee
3. **Descent Phase** (15+ seconds): Rocket falls back to ground

## Technical Details

- **Framework**: Tkinter for GUI, Matplotlib for graphs
- **Threading**: Separate simulation thread for real-time updates
- **Data Rate**: 10Hz update frequency (100ms intervals)
- **Memory Management**: Keeps last 100 data points for performance
- **Safety Features**: Pressure limits and status monitoring
- **Color Scheme**: Professional dark theme with cyan/blue/orange accents

## Customization

You can modify the following parameters in the code:
- `max_pressure`: Maximum pressure limit (default: 1000 PSI)
- Update frequency in `simulate_data()` method
- Launch simulation parameters in the launch phases
- Color scheme and styling in the `colors` dictionary

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- matplotlib >= 3.5.0
- numpy >= 1.21.0
- pillow >= 9.0.0

## License

This project is for educational and demonstration purposes.