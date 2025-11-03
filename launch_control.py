#!/usr/bin/env python3
"""
Rogue Launch Control - GUI Application
A comprehensive launch control software with real-time monitoring and simulation.
"""

import sys
import os
import serial #needed for arduino serial input

# Add error handling for imports
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError as e:
    print(f"Error importing tkinter: {e}")
    print("tkinter is usually included with Python. Please check your Python installation.")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install the required packages:")
    print("pip install matplotlib numpy pillow")
    sys.exit(1)

import threading
import time
from datetime import datetime
import random

#REPLACE WITH COM PORT OF RECEIVER ARDUINO
PORT = '/dev/cu.usbmodem14101'
BAUD_RATE = 9600
#ADJUST BAUD RATE TO MATCH ARDUINO SERIAL OUT BAUD RATE

class LaunchControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rogue Launch Control")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0e1a')
        
        # Modern color scheme - Sleek and professional
        self.colors = {
            'bg_primary': '#0a0e1a',      # Dark background - deeper black
            'bg_secondary': '#141822',    # Slightly lighter background
            'bg_tertiary': '#1e2330',      # Card backgrounds
            'card_highlight': '#252b3a',  # Card hover/shadow effect
            'accent_blue': '#4A9EFF',     # Primary accent - brighter blue
            'accent_cyan': '#1fc991',     # Success/positive - emerald
            'accent_orange': '#ff6b6b',   # Warning/danger - coral
            'accent_purple': '#9b7ede',   # Secondary accent - lavender
            'text_primary': '#ffffff',    # Primary text - pure white
            'text_secondary': '#a1a8b5',  # Secondary text - lighter gray
            'text_muted': '#6b7280',      # Muted text
            'border': '#2d3440',          # Borders - lighter
            'border_light': '#3d4450',    # Light borders
            'success': '#10b981',         # Success green - emerald
            'warning': '#f59e0b',         # Warning yellow - amber
            'danger': '#ef4444'           # Danger red - ruby
        }
        
        # Font family - using system fonts that look modern
        self.fonts = {
            'title': ('Segoe UI', 28, 'bold'),
            'subtitle': ('Segoe UI', 14, 'bold'),
            'heading': ('Segoe UI', 12, 'bold'),
            'body': ('Segoe UI', 11, 'normal'),
            'data_value': ('Segoe UI', 18, 'bold'),
            'button': ('Segoe UI', 13, 'bold')
        }
        
        # Data variables
        self.pressure_data = []
        self.time_data = []
        self.height_data = []
        self.max_pressure = 1000  # PSI
        self.current_pressure = 0
        self.current_altitude = 0  # Current altitude from serial
        self.temperature = 25.0  # degrees Celsius
        self.apogee = 0
        self.launch_time = None
        self.is_launching = False
        self.simulation_running = False
        self.serial_error = None
        
        # GPS data
        self.gps_latitude = 0.0
        self.gps_longitude = 0.0
        self.gps_valid = False
        
        # Create GUI elements
        self.setup_gui()
        self.setup_serial_reader()
        self.setup_data_simulation()
        
    def setup_gui(self):
        """Set up the main GUI layout"""
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(header_frame, text="▐ LAUNCH CONTROL ▐", font=self.fonts['title'], 
                              fg=self.colors['accent_blue'], bg=self.colors['bg_primary'])
        title_label.pack(side=tk.LEFT, pady=15)
        
        # Status badge
        status_badge = tk.Label(header_frame, text="● LIVE", font=self.fonts['subtitle'], 
                              fg=self.colors['success'], bg=self.colors['bg_primary'])
        status_badge.pack(side=tk.RIGHT, pady=15, padx=10)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left column (graphs and gauges)
        left_column = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.setup_graphs_and_gauges(left_column)
        
        # Right column (data and controls)
        right_column = tk.Frame(content_frame, bg=self.colors['bg_secondary'], width=350)
        right_column.pack(side=tk.RIGHT, fill=tk.Y)
        right_column.pack_propagate(False)
        
        # Status indicators
        status_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=2, relief=tk.FLAT, 
                               highlightbackground=self.colors['border_light'], highlightthickness=1)
        status_frame.pack(fill=tk.X, padx=15, pady=15)
        tk.Label(status_frame, text="System Status", font=self.fonts['subtitle'], 
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(12, 8))
        self.setup_status_indicators(status_frame)
        
        # Control buttons
        """
        control_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=2, relief=tk.FLAT,
                                 highlightbackground=self.colors['border_light'], highlightthickness=1)
        control_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        tk.Label(control_frame, text="Launch Controls", font=self.fonts['subtitle'],
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(12, 8))
        self.setup_control_buttons(control_frame)
        """
        # Real-time data
        data_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=2, relief=tk.FLAT,
                             highlightbackground=self.colors['border_light'], highlightthickness=1)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        tk.Label(data_frame, text="Live Telemetry", font=self.fonts['subtitle'],
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(12, 8))
        self.setup_data_displays(data_frame)

    def setup_status_indicators(self, parent):
        """Set up status indicator lights"""
        indicator_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        indicator_frame.pack(pady=8, padx=15, fill=tk.X)
        
        indicators = [
            ("SYSTEM_POWER", "System Power"),
            ("TELEMETRY", "Telemetry"),
            ("GPS", "GPS"),
            ("PRESSURE", "Pressure Sensor"),
            ("TEMPERATURE", "Temperature Sensor"),
            ("ALTITUDE", "Altitude Sensor"),
            ("ARMED", "Armed")
        ]
        self.status_lights = {}

        for name, text in indicators:
            frame = tk.Frame(indicator_frame, bg=self.colors['bg_tertiary'])
            frame.pack(fill=tk.X, pady=4)
            
            # Modern glow effect for status lights
            canvas = tk.Canvas(frame, width=22, height=22, bg=self.colors['bg_tertiary'], highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=(0, 12))
            
            # Outer glow
            light = canvas.create_oval(1, 1, 21, 21, fill=self.colors['text_muted'], outline='', width=2)
            # Inner core
            inner = canvas.create_oval(5, 5, 17, 17, fill='', outline='')
            self.status_lights[name] = canvas, light, inner
            
            label = tk.Label(frame, text=text, font=self.fonts['body'], 
                           fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary'])
            label.pack(side=tk.LEFT)
            
        # Initial status
        self.status_lights["SYSTEM_POWER"][0].itemconfig(self.status_lights["SYSTEM_POWER"][1], fill=self.colors['success'])
        self.status_lights["TELEMETRY"][0].itemconfig(self.status_lights["TELEMETRY"][1], fill=self.colors['accent_cyan'])
        self.status_lights["GPS"][0].itemconfig(self.status_lights["GPS"][1], fill=self.colors['success'])
        self.status_lights["PRESSURE"][0].itemconfig(self.status_lights["PRESSURE"][1], fill=self.colors['success'])
        self.status_lights["TEMPERATURE"][0].itemconfig(self.status_lights["TEMPERATURE"][1], fill=self.colors['success'])
        self.status_lights["ALTITUDE"][0].itemconfig(self.status_lights["ALTITUDE"][1], fill=self.colors['success'])

    def setup_control_buttons(self, parent):
        """Set up control buttons"""
        """
        button_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        button_frame.pack(pady=8, padx=15, fill=tk.X)
        
        # ARM button - amber/warning
        self.arm_button = tk.Button(button_frame, text="◉ ARM SYSTEM", font=self.fonts['button'], 
                                    bg=self.colors['warning'], fg='#000000',
                                    activebackground='#fbbf24', activeforeground='#000000',
                                    relief=tk.FLAT, bd=0, cursor='hand2',
                                    padx=10, pady=12, command=self.arm_system)
        self.arm_button.pack(pady=6, fill=tk.X)
        
        # LAUNCH button - red/danger
        self.launch_button = tk.Button(button_frame, text="▲ LAUNCH", font=self.fonts['button'], 
                                      bg='#404040', fg=self.colors['text_secondary'],
                                      activebackground='#505050', activeforeground=self.colors['text_secondary'],
                                      relief=tk.FLAT, bd=0, cursor='hand2',
                                      padx=10, pady=12, state=tk.DISABLED, command=self.launch_rocket)
        self.launch_button.pack(pady=6, fill=tk.X)
        
        # ABORT button - gray/disabled
        self.abort_button = tk.Button(button_frame, text="⨯ ABORT", font=self.fonts['button'], 
                                     bg='#404040', fg=self.colors['text_secondary'],
                                     activebackground='#505050', activeforeground=self.colors['text_secondary'],
                                     relief=tk.FLAT, bd=0, cursor='hand2',
                                     padx=10, pady=12, state=tk.DISABLED, command=self.abort_launch)
        self.abort_button.pack(pady=6, fill=tk.X)
    """
    def setup_data_displays(self, parent):
        """Set up real-time data displays"""
        data_grid = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        data_grid.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        
        data_points = [
            ("temperature", 'accent_orange'),
            ("pressure", 'accent_cyan'),
            ("altitude", 'text_primary'),
            ("apogee", 'accent_blue'),
            ("time", 'text_secondary'),
            ("velocity", 'text_secondary'),
            ("latitude", 'accent_purple'),
            ("longitude", 'accent_purple')
        ]
        
        for i, (name, color_key) in enumerate(data_points):
            data_grid.rowconfigure(i, weight=1)
            
            # Single label showing "name: value" in plain format
            label_text = name.lower() + ": "
            value_label = tk.Label(data_grid, text=label_text + "0", 
                                  font=self.fonts['body'], fg=self.colors['text_primary'], 
                                  bg=self.colors['bg_tertiary'], anchor='w')
            value_label.grid(row=i, column=0, sticky='w', pady=4, padx=(5, 10))
            
            # Store references and set colors
            if name == "temperature":
                self.temperature_label = value_label
                value_label.config(fg=self.colors['accent_orange'])
            elif name == "pressure":
                self.pressure_label = value_label
                value_label.config(fg=self.colors['accent_cyan'])
            elif name == "altitude":
                self.height_label = value_label
                value_label.config(fg=self.colors['accent_blue'])
            elif name == "apogee":
                self.apogee_label = value_label
                value_label.config(fg=self.colors['text_primary'])
            elif name == "time":
                self.time_label = value_label
            elif name == "velocity":
                self.velocity_label = value_label
            elif name == "latitude":
                self.gps_lat_label = value_label
                value_label.config(fg=self.colors['accent_purple'])
            elif name == "longitude":
                self.gps_lon_label = value_label
                value_label.config(fg=self.colors['accent_purple'])
                
        data_grid.columnconfigure(0, weight=1)

    def setup_graphs_and_gauges(self, parent):
        """Set up graphs and GPS map"""
        
        # Top row for graphs
        graph_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pressure Graph
        pressure_graph_frame = tk.Frame(graph_frame, bg=self.colors['bg_tertiary'], bd=2, relief=tk.FLAT,
                                         highlightbackground=self.colors['border_light'], highlightthickness=1)
        pressure_graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=8)
        
        self.pressure_fig = Figure(figsize=(5, 4), dpi=100, facecolor=self.colors['bg_tertiary'])
        self.ax_pressure = self.pressure_fig.add_subplot(111)
        self.pressure_canvas = FigureCanvasTkAgg(self.pressure_fig, master=pressure_graph_frame)
        self.pressure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Altitude Graph
        altitude_graph_frame = tk.Frame(graph_frame, bg=self.colors['bg_tertiary'], bd=2, relief=tk.FLAT,
                                        highlightbackground=self.colors['border_light'], highlightthickness=1)
        altitude_graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)
        
        self.height_fig = Figure(figsize=(5, 4), dpi=100, facecolor=self.colors['bg_tertiary'])
        self.ax_height = self.height_fig.add_subplot(111)
        self.height_canvas = FigureCanvasTkAgg(self.height_fig, master=altitude_graph_frame)
        self.height_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bottom row for GPS map
        gps_frame_outer = tk.Frame(parent, bg=self.colors['bg_tertiary'], bd=2, relief=tk.FLAT,
                                    highlightbackground=self.colors['border_light'], highlightthickness=1)
        gps_frame_outer.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        tk.Label(gps_frame_outer, text="TANK STATUS", font=self.fonts['subtitle'],
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(12, 5))
        
        self.setup_gps_map(gps_frame_outer)

    def setup_gps_map(self, parent):
        """Set up the GPS map visualization"""
        self.gps_fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.colors['bg_tertiary'])
        self.ax_gps = self.gps_fig.add_subplot(111)
        self.ax_gps.set_facecolor(self.colors['bg_secondary'])
        
        # Initialize with default map (0, 0)
        self.ax_gps.plot(0, 0, 'o', color=self.colors['accent_purple'], markersize=15, label='Current Position')
        self.ax_gps.set_xlim(-1, 1)
        self.ax_gps.set_ylim(-1, 1)
        self.ax_gps.set_title("GPS Location", color=self.colors['text_primary'], fontsize=14)
        self.ax_gps.set_xlabel("Longitude (°)", color=self.colors['text_secondary'], fontsize=10)
        self.ax_gps.set_ylabel("Latitude (°)", color=self.colors['text_secondary'], fontsize=10)
        self.ax_gps.tick_params(axis='x', colors=self.colors['text_secondary'])
        self.ax_gps.tick_params(axis='y', colors=self.colors['text_secondary'])
        for spine in self.ax_gps.spines.values():
            spine.set_edgecolor(self.colors['border'])
        self.ax_gps.grid(True, alpha=0.2, color=self.colors['border'])
        self.gps_fig.tight_layout()
        
        self.gps_canvas = FigureCanvasTkAgg(self.gps_fig, master=parent)
        self.gps_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_serial_reader(self):
        """Set up the serial data reading thread"""
        self.simulation_running = True 
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()
        print("Serial reader thread started.")
        
    def read_serial_data(self):
        """
        Read data from the serial port in a separate thread
        Expected format: pressure,altitude,temperature,latitude,longitude
        Example: 6,6,8,8,7
        """
        print("--SERIAL WORKER ON--")
        try:
            ser = serial.Serial(PORT, BAUD_RATE, timeout=1) # Uses constants defined above
            while self.simulation_running:
                if ser.in_waiting > 0:
                    try:
                        # Read a line from the Arduino
                        line = ser.readline().decode('utf-8').strip()
                        if line:
                            # UPDATED Parse format: pressure,altitude,temperature,latitude,longitude
                            # Data is expected to come like the above as a string 
                            # Split by Comma
                    
                                values = data_str.split(',')
                                
                                if len(values) == 3:
                                    # Extract and update all variables
                                    self.current_pressure = float(values[0])
                                    self.current_altitude = float(values[1])
                                    self.temperature = float(values[2])
                                    #self.gps_latitude = float(values[3]) #Covered by other component (not lcs)
                                    #self.gps_longitude = float(values[4]) #Covered by other componenet (not lcs)
                                    self.gps_valid = True
                                    
                                    if self.serial_error: # Clear error if we get good data
                                        self.serial_error = None
                                    else:
                                        print(f"Serial data format error: Expected 3 values, got {len(values)} - Received: '{line}'")
                                else:
                                # Report Errors to all 
                                    try:
                                        self.current_pressure = None
                                        self.current_altitude = None
                                        self.temperature = None
                                        if self.serial_error:
                                            self.serial_error = None
                                    except ValueError:
                                        print(f"Serial data format error: Invalid format - Received: '{line}'")
                    except (UnicodeDecodeError, ValueError) as e:
                        print(f"Serial data error: {e} - Received: '{line}'")
                else:
                    # Don't busy-wait
                    time.sleep(0.01)
        except serial.SerialException as e:
            print(f"Serial Error: {e}")
            self.serial_error = f"Receiver Device Not Found!"
            #Display -1 (unexpected value!) with the error
            self.current_pressure = -1
            self.current_altitude = -1
            self.temperature = -1
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()
            print("Serial worker finished.")
            
    def setup_data_simulation(self):
        """Set up the data simulation thread"""
        # self.simulation_running is already set to True by setup_serial_reader
        self.simulation_thread = threading.Thread(target=self.simulate_data, daemon=True)
        self.simulation_thread.start()
        print("Data processing/simulation thread started.")
        

    def simulate_data(self):
        """
        Processes real-time data and simulates height/velocity.
        Pressure, altitude, temperature, and GPS are now read from serial (set by serial thread).
        Only velocity is calculated from altitude changes.
        """
        start_time = time.time()
        
        while self.simulation_running:
            current_time = time.time() - start_time
            
            # Use altitude from serial data (self.current_altitude set by serial thread)
            # LCS not responsible for sending signals, so self.is_launching check removed
            """
            if self.is_launching:
                # During launch, use serial altitude if available, otherwise simulate
                if self.current_altitude > 0:
                    height = self.current_altitude
                else:
                    # Fallback simulation during launch
                    if current_time < 5:  # Boost phase
                        height = current_time * current_time * 50
                    elif current_time < 15:  # Coast phase
                        height = 1250 + (current_time - 5) * 200 - (current_time - 5) ** 2 * 10
                    else:  # Descent phase
                        height = max(0, self.apogee - (current_time - 15) * 100)
            else:
            """
            #Always using Serial Altitude
            height = self.current_altitude
            
            # Temperature and GPS are now set by serial thread
            # No simulation needed - they're updated directly in read_serial_data()
            # Calculate velocity from altitude changes
            # Update data
           
            if height > self.apogee:
                self.apogee = height
            
            # Store data for graphs
            self.time_data.append(current_time)
            self.pressure_data.append(self.current_pressure)
            self.height_data.append(height)
            
            # Keep only last 100 data points
            if len(self.time_data) > 100:
                self.time_data = self.time_data[-100:]
                self.pressure_data = self.pressure_data[-100:]
                self.height_data = self.height_data[-100:]
            
            # Update GUI
            self.root.after(0, self.update_display)
            
            time.sleep(0.1)  # Update every 100ms
            
    def update_display(self):
        """Update all display elements"""
        #Serial Port Error handle
        if self.serial_error:
            #Pressure Altitude and Temperature (The Data Readings) all get error text
            error_text = "NULL - Check Receiver Connection"
            self.pressure_label.config(text=f"pressure: {error_text}", fg=self.colors['danger'])
            self.temperature_label.config(text=f"temperature: {error_text}", fg=self.colors['danger'])
            self.height_label.config(text=f"altitude: {error_text}", fg=self.colors['danger'])

        else:
        
            # Update temperature
            self.temperature_label.config(text=f"temperature: {self.temperature:.1f}", fg=self.colors['accent_orange'])
            
            # Update data labels
            self.apogee_label.config(text=f"apogee: {self.apogee:.0f}")
            self.time_label.config(text=f"time: {self.time_data[-1] if self.time_data else 0:.1f}")
            self.height_label.config(text=f"altitude: {self.height_data[-1] if self.height_data else 0:.0f}")
        
            velocity = 0
            if len(self.height_data) > 1:
                velocity = (self.height_data[-1] - self.height_data[-2]) * 10  # Approximate velocity
            self.velocity_label.config(text=f"velocity: {velocity:.0f}")
        
        # Update GPS labels
        if self.gps_valid:
            self.gps_lat_label.config(text=f"latitude: {self.gps_latitude:.6f}", fg=self.colors['accent_purple'])
            self.gps_lon_label.config(text=f"longitude: {self.gps_longitude:.6f}", fg=self.colors['accent_purple'])
        else:
            self.gps_lat_label.config(text="latitude: No Signal", fg=self.colors['text_secondary'])
            self.gps_lon_label.config(text="longitude: No Signal", fg=self.colors['text_secondary'])
        
        # Update graphs
        self.update_graphs()
        
        # Update GPS map
        self.update_gps_map()
        
        # Update status lights
        self.update_status_lights()
        
    def update_graphs(self):
        """Update the pressure and altitude graphs"""
        
        # Update pressure graph with gradient effect
        self.ax_pressure.clear()
        self.ax_pressure.set_facecolor(self.colors['bg_secondary'])
        
        if len(self.time_data) > 0:
            self.ax_pressure.plot(self.time_data, self.pressure_data, color=self.colors['accent_cyan'], linewidth=2.5, label='Pressure')
            # Fill area under curve for modern look
            self.ax_pressure.fill_between(self.time_data, self.pressure_data, alpha=0.3, color=self.colors['accent_cyan'])
        
        self.ax_pressure.set_title("Pressure", color=self.colors['text_primary'], fontsize=13, fontweight='bold')
        self.ax_pressure.set_xlabel("Time (s)", color=self.colors['text_secondary'], fontsize=10)
        self.ax_pressure.set_ylabel("PSI", color=self.colors['text_secondary'], fontsize=10)
        self.ax_pressure.tick_params(axis='x', colors=self.colors['text_secondary'], labelsize=9)
        self.ax_pressure.tick_params(axis='y', colors=self.colors['text_secondary'], labelsize=9)
        for spine in self.ax_pressure.spines.values():
            spine.set_edgecolor(self.colors['border'])
            spine.set_linewidth(1)
        self.ax_pressure.grid(True, alpha=0.15, color=self.colors['border'], linestyle='-', linewidth=0.5)
        self.pressure_fig.tight_layout()
        self.pressure_canvas.draw_idle()
        
        # Update altitude graph with gradient effect
        self.ax_height.clear()
        self.ax_height.set_facecolor(self.colors['bg_secondary'])
        
        if len(self.time_data) > 0:
            self.ax_height.plot(self.time_data, self.height_data, color=self.colors['accent_purple'], linewidth=2.5, label='Altitude')
            # Fill area under curve
            self.ax_height.fill_between(self.time_data, self.height_data, alpha=0.3, color=self.colors['accent_purple'])
        
        self.ax_height.set_title("Altitude", color=self.colors['text_primary'], fontsize=13, fontweight='bold')
        self.ax_height.set_xlabel("Time (s)", color=self.colors['text_secondary'], fontsize=10)
        self.ax_height.set_ylabel("Feet", color=self.colors['text_secondary'], fontsize=10)
        self.ax_height.tick_params(axis='x', colors=self.colors['text_secondary'], labelsize=9)
        self.ax_height.tick_params(axis='y', colors=self.colors['text_secondary'], labelsize=9)
        for spine in self.ax_height.spines.values():
            spine.set_edgecolor(self.colors['border'])
            spine.set_linewidth(1)
        self.ax_height.grid(True, alpha=0.15, color=self.colors['border'], linestyle='-', linewidth=0.5)
        self.height_fig.tight_layout()
        self.height_canvas.draw_idle()

    def update_gps_map(self):
        """Update the GPS map with current location"""
        self.ax_gps.clear()
        self.ax_gps.set_facecolor(self.colors['bg_secondary'])
        
        if self.gps_valid:
            # Plot current position with modern styling
            self.ax_gps.plot(self.gps_longitude, self.gps_latitude, 'o', 
                           color=self.colors['accent_purple'], markersize=18, 
                           markeredgecolor=self.colors['text_primary'], markeredgewidth=2,
                           label='Current Position', zorder=5)
            
            # Add subtle background circle
            circle = plt.Circle((self.gps_longitude, self.gps_latitude), 0.002, 
                              color=self.colors['accent_purple'], alpha=0.1, zorder=1)
            self.ax_gps.add_patch(circle)
            
            # Set reasonable limits around the position
            margin = 0.005
            self.ax_gps.set_xlim(self.gps_longitude - margin, self.gps_longitude + margin)
            self.ax_gps.set_ylim(self.gps_latitude - margin, self.gps_latitude + margin)
        else:
            # Show "No Signal" message
            self.ax_gps.text(0.5, 0.5, 'NO GPS SIGNAL', 
                           ha='center', va='center', 
                           fontsize=14, color=self.colors['text_muted'], weight='bold',
                           transform=self.ax_gps.transAxes)
            self.ax_gps.set_xlim(-0.001, 0.001)
            self.ax_gps.set_ylim(-0.001, 0.001)
        
        self.ax_gps.set_title("GPS Location", color=self.colors['text_primary'], fontsize=13, fontweight='bold')
        self.ax_gps.set_xlabel("Longitude", color=self.colors['text_secondary'], fontsize=10)
        self.ax_gps.set_ylabel("Latitude", color=self.colors['text_secondary'], fontsize=10)
        self.ax_gps.tick_params(axis='x', colors=self.colors['text_secondary'], labelsize=9)
        self.ax_gps.tick_params(axis='y', colors=self.colors['text_secondary'], labelsize=9)
        for spine in self.ax_gps.spines.values():
            spine.set_edgecolor(self.colors['border'])
            spine.set_linewidth(1)
        self.ax_gps.grid(True, alpha=0.2, color=self.colors['border'], linestyle='-', linewidth=0.5)
        self.gps_fig.tight_layout()
        self.gps_canvas.draw_idle()
    
    def update_status_lights(self):
        """Update status indicator lights"""
        # Structure: status_lights[name] = (canvas, light_outer, light_inner)
        
        # Telemetry light (flashes if error, solid if OK)
        if self.serial_error:
            color = self.colors['danger'] if int(time.time() * 2) % 2 == 0 else self.colors['text_muted']
        else:
            color = self.colors['accent_cyan']
        self.status_lights["TELEMETRY"][0].itemconfig(self.status_lights["TELEMETRY"][1], fill=color)

        # GPS light
        if self.gps_valid:
            gps_color = self.colors['success']
        else:
            gps_color = self.colors['danger'] if int(time.time() * 2) % 2 == 0 else self.colors['text_muted']
        self.status_lights["GPS"][0].itemconfig(self.status_lights["GPS"][1], fill=gps_color)
        
        # Pressure sensor light
        if self.serial_error:
            pressure_color = self.colors['danger'] if int(time.time() * 2) % 2 == 0 else self.colors['text_muted']
        else:
            pressure_color = self.colors['success']
        self.status_lights["PRESSURE"][0].itemconfig(self.status_lights["PRESSURE"][1], fill=pressure_color)
        
        # Temperature sensor light
        temp_color = self.colors['success']
        self.status_lights["TEMPERATURE"][0].itemconfig(self.status_lights["TEMPERATURE"][1], fill=temp_color)
        
        # Altitude sensor light
        alt_color = self.colors['success']
        self.status_lights["ALTITUDE"][0].itemconfig(self.status_lights["ALTITUDE"][1], fill=alt_color)

        # Armed light || COMMENTED OUT FOR REMOVAL OF BUTTONS
        #armed_color = self.colors['success'] if self.arm_button['state'] == tk.DISABLED else self.colors['text_muted']
        #self.status_lights["ARMED"][0].itemconfig(self.status_lights["ARMED"][1], fill=armed_color)

    """
    def arm_system(self):
        "Arm the System" 
        if messagebox.askyesno("Arm System", "Are you sure you want to arm the launch system?"):
            self.arm_button.config(state=tk.DISABLED, bg='#3d3d3d', fg=self.colors['text_secondary'])
            self.launch_button.config(state=tk.NORMAL, bg=self.colors['danger'], fg='#ffffff',
                                     activebackground='#ea4949')
            self.abort_button.config(state=tk.NORMAL, bg='#505050', fg=self.colors['text_secondary'],
                                    activebackground='#606060')
            print("System ARMED.")
    """
    """
    def launch_rocket(self):
        "Launch the rocket"
        if self.arm_button['state'] == tk.DISABLED:
            self.is_launching = True
            self.launch_time = datetime.now()
            self.apogee = 0
            self.launch_button.config(state=tk.DISABLED, bg='#3d3d3d', fg=self.colors['text_secondary'])
            self.abort_button.config(state=tk.NORMAL, bg=self.colors['warning'], fg='#000000',
                                    activebackground='#fbbf24')
            messagebox.showinfo("Launch Initiated", "Rocket launch sequence initiated!")
     """
    """
    def abort_launch(self):
        "Abort the Launch"
        if self.is_launching or self.arm_button['state'] == tk.DISABLED:
            self.is_launching = False
            self.launch_button.config(state=tk.DISABLED, bg='#404040', fg=self.colors['text_secondary'])
            self.abort_button.config(state=tk.DISABLED, bg='#404040', fg=self.colors['text_secondary'])
            self.arm_button.config(state=tk.NORMAL, bg=self.colors['warning'], fg='#000000',
                                  activebackground='#fbbf24')
            messagebox.showwarning("System Disarmed", "System has been disarmed.")
     """       
    def on_closing(self):
        """Handle application closing"""
        self.simulation_running = False # This flag stops both threads
        # Wait for threads to finish
        if hasattr(self, 'serial_thread'):
            self.serial_thread.join(timeout=1)
        if hasattr(self, 'simulation_thread'):
            self.simulation_thread.join(timeout=1)
        self.root.destroy()

def main():
    """Main application entry point"""
    try:
        print("Starting Rogue Launch Control...")
        root = tk.Tk()
        app = LaunchControlGUI(root)
        
        # Handle window closing
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("Launch Control GUI initialized successfully!")
        print("Use the ARM SYSTEM button to prepare for launch, then LAUNCH to start the simulation.")
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Please check that all dependencies are installed correctly.")
        sys.exit(1)

if __name__ == "__main__":
    main()
