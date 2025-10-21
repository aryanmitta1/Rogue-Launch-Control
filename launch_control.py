#!/usr/bin/env python3
"""
Rogue Launch Control - GUI Application
A comprehensive launch control software with real-time monitoring and simulation.
"""

import sys
import os

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

class LaunchControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rogue Launch Control")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0d1117')
        
        # Modern color scheme
        self.colors = {
            'bg_primary': '#0d1117',      # Dark background
            'bg_secondary': '#161b22',    # Slightly lighter background
            'bg_tertiary': '#21262d',      # Card backgrounds
            'accent_blue': '#58a6ff',     # Primary accent
            'accent_cyan': '#39d353',     # Success/positive
            'accent_orange': '#f85149',   # Warning/danger
            'accent_purple': '#a5a5ff',   # Secondary accent
            'text_primary': '#f0f6fc',    # Primary text
            'text_secondary': '#8b949e',  # Secondary text
            'border': '#30363d',          # Borders
            'success': '#238636',         # Success green
            'warning': '#9a6700',         # Warning yellow
            'danger': '#da3633'           # Danger red
        }
        
        # Data variables
        self.pressure_data = []
        self.time_data = []
        self.height_data = []
        self.max_pressure = 1000  # PSI
        self.current_pressure = 0
        self.apogee = 0
        self.launch_time = None
        self.is_launching = False
        self.simulation_running = False
        
        # Create GUI elements
        self.setup_gui()
        self.setup_data_simulation()
        
    def setup_gui(self):
        """Set up the main GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title with modern styling
        title_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 25))
        
        title_label = tk.Label(title_frame, text="ROGUE LAUNCH CONTROL", 
                              font=('SF Pro Display', 28, 'bold'), 
                              fg=self.colors['accent_blue'], bg=self.colors['bg_primary'])
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(title_frame, text="Advanced Rocket Launch Management System", 
                                 font=('SF Pro Display', 12), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        subtitle_label.pack(pady=(5, 0))
        
        # Top row - Status and controls
        top_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        top_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status indicators
        self.setup_status_indicators(top_frame)
        
        # Control buttons
        self.setup_control_buttons(top_frame)
        
        # Middle row - Data displays
        middle_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        middle_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.setup_data_displays(middle_frame)
        
        # Bottom row - Graphs and gauges
        bottom_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_graphs_and_gauges(bottom_frame)
        
    def setup_status_indicators(self, parent):
        """Set up status indicator lights"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'], 
                               relief=tk.FLAT, bd=0)
        status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        # Add subtle border effect
        border_frame = tk.Frame(status_frame, bg=self.colors['border'], height=2)
        border_frame.pack(fill=tk.X)
        
        # Header
        header_frame = tk.Frame(status_frame, bg=self.colors['bg_tertiary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header_frame, text="SYSTEM STATUS", 
                font=('SF Pro Display', 11, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack()
        
        # Status lights
        lights_frame = tk.Frame(status_frame, bg=self.colors['bg_tertiary'])
        lights_frame.pack(pady=(0, 20), padx=20)
        
        # System Ready
        ready_frame = tk.Frame(lights_frame, bg=self.colors['bg_tertiary'])
        ready_frame.pack(side=tk.LEFT, padx=15)
        self.ready_light = tk.Label(ready_frame, text="●", font=('SF Pro Display', 16), 
                                  fg=self.colors['danger'], bg=self.colors['bg_tertiary'])
        self.ready_light.pack(side=tk.LEFT)
        tk.Label(ready_frame, text="System Ready", 
                font=('SF Pro Display', 10),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).pack(side=tk.LEFT, padx=(8, 0))
        
        # Pressure OK
        pressure_frame = tk.Frame(lights_frame, bg=self.colors['bg_tertiary'])
        pressure_frame.pack(side=tk.LEFT, padx=15)
        self.pressure_light = tk.Label(pressure_frame, text="●", font=('SF Pro Display', 16), 
                                     fg=self.colors['danger'], bg=self.colors['bg_tertiary'])
        self.pressure_light.pack(side=tk.LEFT)
        tk.Label(pressure_frame, text="Pressure OK", 
                font=('SF Pro Display', 10),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).pack(side=tk.LEFT, padx=(8, 0))
        
        # Launch Status
        launch_frame = tk.Frame(lights_frame, bg=self.colors['bg_tertiary'])
        launch_frame.pack(side=tk.LEFT, padx=15)
        self.launch_light = tk.Label(launch_frame, text="●", font=('SF Pro Display', 16), 
                                   fg=self.colors['danger'], bg=self.colors['bg_tertiary'])
        self.launch_light.pack(side=tk.LEFT)
        tk.Label(launch_frame, text="Launch Ready", 
                font=('SF Pro Display', 10),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).pack(side=tk.LEFT, padx=(8, 0))
        
    def setup_control_buttons(self, parent):
        """Set up control buttons"""
        control_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'], 
                                relief=tk.FLAT, bd=0)
        control_frame.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Add subtle border effect
        border_frame = tk.Frame(control_frame, bg=self.colors['border'], height=2)
        border_frame.pack(fill=tk.X)
        
        # Header
        header_frame = tk.Frame(control_frame, bg=self.colors['bg_tertiary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header_frame, text="LAUNCH CONTROLS", 
                font=('SF Pro Display', 11, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack()
        
        buttons_frame = tk.Frame(control_frame, bg=self.colors['bg_tertiary'])
        buttons_frame.pack(pady=(0, 20), padx=20)
        
        # Modern button styling
        button_style = {
            'font': ('SF Pro Display', 10, 'bold'),
            'relief': tk.FLAT,
            'bd': 0,
            'width': 14,
            'height': 2,
            'cursor': 'hand2'
        }
        
        # Arm button
        self.arm_button = tk.Button(buttons_frame, text="ARM SYSTEM", 
                                  bg=self.colors['warning'], fg=self.colors['text_primary'],
                                  command=self.arm_system, **button_style)
        self.arm_button.pack(side=tk.LEFT, padx=8)
        
        # Launch button
        self.launch_button = tk.Button(buttons_frame, text="LAUNCH", 
                                     bg=self.colors['danger'], fg=self.colors['text_primary'],
                                     command=self.launch_rocket,
                                     state=tk.DISABLED, **button_style)
        self.launch_button.pack(side=tk.LEFT, padx=8)
        
        # Abort button
        self.abort_button = tk.Button(buttons_frame, text="ABORT", 
                                    bg=self.colors['text_secondary'], fg=self.colors['text_primary'],
                                    command=self.abort_launch, **button_style)
        self.abort_button.pack(side=tk.LEFT, padx=8)
        
    def setup_data_displays(self, parent):
        """Set up real-time data displays"""
        data_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'], 
                             relief=tk.FLAT, bd=0)
        data_frame.pack(fill=tk.X, pady=10)
        
        # Add subtle border effect
        border_frame = tk.Frame(data_frame, bg=self.colors['border'], height=2)
        border_frame.pack(fill=tk.X)
        
        # Header
        header_frame = tk.Frame(data_frame, bg=self.colors['bg_tertiary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header_frame, text="FLIGHT DATA", 
                font=('SF Pro Display', 11, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack()
        
        # Data display grid
        data_grid = tk.Frame(data_frame, bg=self.colors['bg_tertiary'])
        data_grid.pack(pady=(0, 20), padx=20)
        
        # Current Pressure
        tk.Label(data_grid, text="Current Pressure:", 
                font=('SF Pro Display', 9),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).grid(row=0, column=0, sticky='w', padx=15, pady=8)
        self.pressure_label = tk.Label(data_grid, text="0 PSI", 
                                     font=('SF Pro Display', 13, 'bold'),
                                     fg=self.colors['accent_cyan'], bg=self.colors['bg_tertiary'])
        self.pressure_label.grid(row=0, column=1, padx=15, pady=8)
        
        # Max Pressure
        tk.Label(data_grid, text="Max Pressure:", 
                font=('SF Pro Display', 9),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).grid(row=0, column=2, sticky='w', padx=15, pady=8)
        self.max_pressure_label = tk.Label(data_grid, text=f"{self.max_pressure} PSI", 
                                         font=('SF Pro Display', 13, 'bold'),
                                         fg=self.colors['accent_orange'], bg=self.colors['bg_tertiary'])
        self.max_pressure_label.grid(row=0, column=3, padx=15, pady=8)
        
        # Apogee
        tk.Label(data_grid, text="Apogee:", 
                font=('SF Pro Display', 9),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).grid(row=1, column=0, sticky='w', padx=15, pady=8)
        self.apogee_label = tk.Label(data_grid, text="0 ft", 
                                   font=('SF Pro Display', 13, 'bold'),
                                   fg=self.colors['accent_cyan'], bg=self.colors['bg_tertiary'])
        self.apogee_label.grid(row=1, column=1, padx=15, pady=8)
        
        # Flight Time
        tk.Label(data_grid, text="Flight Time:", 
                font=('SF Pro Display', 9),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).grid(row=1, column=2, sticky='w', padx=15, pady=8)
        self.time_label = tk.Label(data_grid, text="0.0s", 
                                 font=('SF Pro Display', 13, 'bold'),
                                 fg=self.colors['accent_cyan'], bg=self.colors['bg_tertiary'])
        self.time_label.grid(row=1, column=3, padx=15, pady=8)
        
        # Current Height
        tk.Label(data_grid, text="Current Height:", 
                font=('SF Pro Display', 9),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).grid(row=2, column=0, sticky='w', padx=15, pady=8)
        self.height_label = tk.Label(data_grid, text="0 ft", 
                                   font=('SF Pro Display', 13, 'bold'),
                                   fg=self.colors['accent_cyan'], bg=self.colors['bg_tertiary'])
        self.height_label.grid(row=2, column=1, padx=15, pady=8)
        
        # Velocity
        tk.Label(data_grid, text="Velocity:", 
                font=('SF Pro Display', 9),
                fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary']).grid(row=2, column=2, sticky='w', padx=15, pady=8)
        self.velocity_label = tk.Label(data_grid, text="0 ft/s", 
                                     font=('SF Pro Display', 13, 'bold'),
                                     fg=self.colors['accent_cyan'], bg=self.colors['bg_tertiary'])
        self.velocity_label.grid(row=2, column=3, padx=15, pady=8)
        
    def setup_graphs_and_gauges(self, parent):
        """Set up graphs and pressure gauge"""
        # Left side - Pressure graph
        graph_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'], 
                              relief=tk.FLAT, bd=0)
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Add subtle border effect
        border_frame = tk.Frame(graph_frame, bg=self.colors['border'], height=2)
        border_frame.pack(fill=tk.X)
        
        # Header
        header_frame = tk.Frame(graph_frame, bg=self.colors['bg_tertiary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header_frame, text="PRESSURE vs TIME", 
                font=('SF Pro Display', 11, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack()
        
        # Create matplotlib figure with modern styling
        self.fig = Figure(figsize=(8, 6), facecolor=self.colors['bg_tertiary'])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.colors['bg_secondary'])
        self.ax.set_xlabel('Time (s)', color=self.colors['text_primary'], fontsize=10)
        self.ax.set_ylabel('Pressure (PSI)', color=self.colors['text_primary'], fontsize=10)
        self.ax.tick_params(colors=self.colors['text_secondary'], labelsize=9)
        self.ax.grid(True, alpha=0.2, color=self.colors['border'])
        
        # Embed matplotlib in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Right side - Pressure gauge and height graph
        right_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        # Pressure gauge
        gauge_frame = tk.Frame(right_frame, bg=self.colors['bg_tertiary'], 
                              relief=tk.FLAT, bd=0)
        gauge_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Add subtle border effect
        border_frame = tk.Frame(gauge_frame, bg=self.colors['border'], height=2)
        border_frame.pack(fill=tk.X)
        
        # Header
        header_frame = tk.Frame(gauge_frame, bg=self.colors['bg_tertiary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header_frame, text="PRESSURE GAUGE", 
                font=('SF Pro Display', 11, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack()
        
        self.setup_pressure_gauge(gauge_frame)
        
        # Height graph
        height_frame = tk.Frame(right_frame, bg=self.colors['bg_tertiary'], 
                               relief=tk.FLAT, bd=0)
        height_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add subtle border effect
        border_frame = tk.Frame(height_frame, bg=self.colors['border'], height=2)
        border_frame.pack(fill=tk.X)
        
        # Header
        header_frame = tk.Frame(height_frame, bg=self.colors['bg_tertiary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header_frame, text="HEIGHT vs TIME", 
                font=('SF Pro Display', 11, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack()
        
        # Create height graph
        self.height_fig = Figure(figsize=(4, 4), facecolor=self.colors['bg_tertiary'])
        self.height_ax = self.height_fig.add_subplot(111)
        self.height_ax.set_facecolor(self.colors['bg_secondary'])
        self.height_ax.set_xlabel('Time (s)', color=self.colors['text_primary'], fontsize=10)
        self.height_ax.set_ylabel('Height (ft)', color=self.colors['text_primary'], fontsize=10)
        self.height_ax.tick_params(colors=self.colors['text_secondary'], labelsize=9)
        self.height_ax.grid(True, alpha=0.2, color=self.colors['border'])
        
        self.height_canvas = FigureCanvasTkAgg(self.height_fig, height_frame)
        self.height_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
    def setup_pressure_gauge(self, parent):
        """Set up the pressure gauge visualization"""
        gauge_canvas = tk.Canvas(parent, width=200, height=200, 
                                bg=self.colors['bg_tertiary'], highlightthickness=0)
        gauge_canvas.pack(pady=20)
        
        # Draw gauge background with modern styling
        gauge_canvas.create_arc(50, 50, 150, 150, start=0, extent=180, 
                              outline=self.colors['border'], width=2, 
                              fill=self.colors['bg_secondary'])
        
        # Draw gauge markings with modern colors
        for i in range(0, 181, 30):
            angle = i * np.pi / 180
            x1 = 100 + 40 * np.cos(angle)
            y1 = 100 - 40 * np.sin(angle)
            x2 = 100 + 50 * np.cos(angle)
            y2 = 100 - 50 * np.sin(angle)
            gauge_canvas.create_line(x1, y1, x2, y2, 
                                   fill=self.colors['text_secondary'], width=2)
            
            # Add labels with modern styling
            if i % 60 == 0:
                label_x = 100 + 60 * np.cos(angle)
                label_y = 100 - 60 * np.sin(angle)
                pressure_value = int((i / 180) * self.max_pressure)
                gauge_canvas.create_text(label_x, label_y, text=str(pressure_value), 
                                       fill=self.colors['text_primary'], 
                                       font=('SF Pro Display', 8))
        
        # Pressure needle with modern styling
        self.needle = gauge_canvas.create_line(100, 100, 100, 50, 
                                             fill=self.colors['accent_orange'], width=3)
        
        # Center dot with modern styling
        gauge_canvas.create_oval(95, 95, 105, 105, 
                                fill=self.colors['accent_orange'], 
                                outline=self.colors['accent_orange'])
        
        # Store canvas reference for updates
        self.gauge_canvas = gauge_canvas
        
    def setup_data_simulation(self):
        """Set up the data simulation thread"""
        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self.simulate_data, daemon=True)
        self.simulation_thread.start()
        
    def simulate_data(self):
        """Simulate real-time data"""
        start_time = time.time()
        
        while self.simulation_running:
            current_time = time.time() - start_time
            
            if self.is_launching:
                # Launch phase simulation
                if current_time < 5:  # Boost phase
                    pressure = min(self.max_pressure, 200 + (current_time * 150))
                    height = current_time * current_time * 50
                    velocity = current_time * 100
                elif current_time < 15:  # Coast phase
                    pressure = max(0, self.max_pressure - (current_time - 5) * 100)
                    height = 1250 + (current_time - 5) * 200 - (current_time - 5) ** 2 * 10
                    velocity = max(0, 500 - (current_time - 5) * 50)
                else:  # Descent phase
                    pressure = 0
                    height = max(0, self.apogee - (current_time - 15) * 100)
                    velocity = -(current_time - 15) * 50
            else:
                # Pre-launch simulation
                pressure = random.uniform(0, 50)
                height = 0
                velocity = 0
            
            # Update data
            self.current_pressure = pressure
            if height > self.apogee:
                self.apogee = height
            
            # Store data for graphs
            self.time_data.append(current_time)
            self.pressure_data.append(pressure)
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
        # Update data labels
        self.pressure_label.config(text=f"{self.current_pressure:.0f} PSI")
        self.apogee_label.config(text=f"{self.apogee:.0f} ft")
        self.time_label.config(text=f"{self.time_data[-1] if self.time_data else 0:.1f}s")
        self.height_label.config(text=f"{self.height_data[-1] if self.height_data else 0:.0f} ft")
        
        velocity = 0
        if len(self.height_data) > 1:
            velocity = (self.height_data[-1] - self.height_data[-2]) * 10  # Approximate velocity
        self.velocity_label.config(text=f"{velocity:.0f} ft/s")
        
        # Update pressure gauge
        if hasattr(self, 'gauge_canvas'):
            pressure_ratio = self.current_pressure / self.max_pressure
            angle = pressure_ratio * 180  # Convert to degrees
            angle_rad = angle * np.pi / 180
            
            # Calculate needle position
            needle_x = 100 + 45 * np.cos(angle_rad)
            needle_y = 100 - 45 * np.sin(angle_rad)
            
            # Update needle
            self.gauge_canvas.coords(self.needle, 100, 100, needle_x, needle_y)
            
            # Change needle color based on pressure
            if pressure_ratio > 0.8:
                color = self.colors['danger']  # Red for high pressure
            elif pressure_ratio > 0.5:
                color = self.colors['warning']  # Orange for medium pressure
            else:
                color = self.colors['accent_cyan']  # Cyan for low pressure
                
            self.gauge_canvas.itemconfig(self.needle, fill=color)
        
        # Update graphs
        self.update_graphs()
        
        # Update status lights
        self.update_status_lights()
        
    def update_graphs(self):
        """Update the pressure and height graphs"""
        if len(self.time_data) > 1:
            # Update pressure graph
            self.ax.clear()
            self.ax.set_facecolor(self.colors['bg_secondary'])
            self.ax.plot(self.time_data, self.pressure_data, 
                        color=self.colors['accent_cyan'], linewidth=2.5)
            self.ax.set_xlabel('Time (s)', color=self.colors['text_primary'], fontsize=10)
            self.ax.set_ylabel('Pressure (PSI)', color=self.colors['text_primary'], fontsize=10)
            self.ax.tick_params(colors=self.colors['text_secondary'], labelsize=9)
            self.ax.grid(True, alpha=0.2, color=self.colors['border'])
            self.ax.set_title('Pressure vs Time', color=self.colors['text_primary'], 
                            fontsize=12, fontweight='bold')
            
            # Update height graph
            self.height_ax.clear()
            self.height_ax.set_facecolor(self.colors['bg_secondary'])
            self.height_ax.plot(self.time_data, self.height_data, 
                               color=self.colors['accent_blue'], linewidth=2.5)
            self.height_ax.set_xlabel('Time (s)', color=self.colors['text_primary'], fontsize=10)
            self.height_ax.set_ylabel('Height (ft)', color=self.colors['text_primary'], fontsize=10)
            self.height_ax.tick_params(colors=self.colors['text_secondary'], labelsize=9)
            self.height_ax.grid(True, alpha=0.2, color=self.colors['border'])
            self.height_ax.set_title('Height vs Time', color=self.colors['text_primary'], 
                                   fontsize=12, fontweight='bold')
            
            # Refresh canvases
            self.canvas.draw()
            self.height_canvas.draw()
            
    def update_status_lights(self):
        """Update status indicator lights"""
        # System ready (always cyan when not launching)
        if not self.is_launching:
            self.ready_light.config(fg=self.colors['accent_cyan'])
        else:
            self.ready_light.config(fg=self.colors['danger'])
            
        # Pressure OK
        if self.current_pressure < self.max_pressure * 0.8:
            self.pressure_light.config(fg=self.colors['accent_cyan'])
        else:
            self.pressure_light.config(fg=self.colors['danger'])
            
        # Launch ready
        if not self.is_launching and self.current_pressure < self.max_pressure * 0.1:
            self.launch_light.config(fg=self.colors['accent_cyan'])
        else:
            self.launch_light.config(fg=self.colors['danger'])
            
    def arm_system(self):
        """Arm the launch system"""
        if not self.is_launching:
            self.arm_button.config(state=tk.DISABLED, bg=self.colors['text_secondary'])
            self.launch_button.config(state=tk.NORMAL, bg=self.colors['danger'])
            messagebox.showinfo("System Armed", "Launch system is now armed and ready!")
            
    def launch_rocket(self):
        """Launch the rocket"""
        if not self.is_launching:
            self.is_launching = True
            self.launch_time = time.time()
            self.launch_button.config(state=tk.DISABLED, bg=self.colors['text_secondary'])
            self.abort_button.config(state=tk.NORMAL, bg=self.colors['warning'])
            messagebox.showinfo("Launch Initiated", "Rocket launch sequence initiated!")
            
    def abort_launch(self):
        """Abort the launch"""
        if self.is_launching:
            self.is_launching = False
            self.abort_button.config(state=tk.DISABLED, bg=self.colors['text_secondary'])
            self.arm_button.config(state=tk.NORMAL, bg=self.colors['warning'])
            messagebox.showwarning("Launch Aborted", "Launch sequence has been aborted!")
            
    def on_closing(self):
        """Handle application closing"""
        self.simulation_running = False
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
