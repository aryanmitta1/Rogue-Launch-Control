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

# --- ADDED: Missing constants from test_launch_control_software.py ---
PORT = 'COM14'
BAUD_RATE = 9600
# --- END ADDED ---

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
        self.serial_error = None # <<<<<<< ADDED: Missing variable
        
        # Create GUI elements
        self.setup_gui()
        self.setup_serial_reader() # <<<<<<< ADDED: Start serial thread
        self.setup_data_simulation()
        
    def setup_gui(self):
        """Set up the main GUI layout"""
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(header_frame, text="ROGUE LAUNCH CONTROL", font=("Arial", 32, "bold"), fg=self.colors['text_primary'], bg=self.colors['bg_primary'])
        title_label.pack(side=tk.LEFT, pady=10)
        
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
        status_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground=self.colors['border'])
        status_frame.pack(fill=tk.X, padx=20, pady=20)
        tk.Label(status_frame, text="SYSTEM STATUS", font=("Arial", 16, "bold"), fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(10, 5))
        self.setup_status_indicators(status_frame)
        
        # Control buttons
        control_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground=self.colors['border'])
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        tk.Label(control_frame, text="LAUNCH CONTROLS", font=("Arial", 16, "bold"), fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(10, 5))
        self.setup_control_buttons(control_frame)
        
        # Real-time data
        data_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground=self.colors['border'])
        data_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        tk.Label(data_frame, text="LIVE TELEMETRY", font=("Arial", 16, "bold"), fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(10, 5))
        self.setup_data_displays(data_frame)

    def setup_status_indicators(self, parent):
        """Set up status indicator lights"""
        indicator_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        indicator_frame.pack(pady=10, padx=20, fill=tk.X)
        
        indicators = [("SYSTEM_POWER", "System Power"), ("TELEMETRY", "Telemetry"), ("ARMED", "Armed")]
        self.status_lights = {}

        for name, text in indicators:
            frame = tk.Frame(indicator_frame, bg=self.colors['bg_tertiary'])
            frame.pack(fill=tk.X, pady=5)
            
            canvas = tk.Canvas(frame, width=20, height=20, bg=self.colors['bg_tertiary'], highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=(0, 10))
            light = canvas.create_oval(2, 2, 18, 18, fill=self.colors['text_secondary'], outline=self.colors['border'])
            self.status_lights[name] = canvas, light
            
            label = tk.Label(frame, text=text, font=("Arial", 12), fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary'])
            label.pack(side=tk.LEFT)
            
        # Initial status
        self.status_lights["SYSTEM_POWER"][0].itemconfig(self.status_lights["SYSTEM_POWER"][1], fill=self.colors['success'])
        self.status_lights["TELEMETRY"][0].itemconfig(self.status_lights["TELEMETRY"][1], fill=self.colors['accent_cyan'])

    def setup_control_buttons(self, parent):
        """Set up control buttons"""
        button_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        button_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.arm_button = tk.Button(button_frame, text="ARM SYSTEM", font=("Arial", 14, "bold"), 
                                    bg=self.colors['warning'], fg=self.colors['bg_primary'], 
                                    relief=tk.FLAT, width=20, command=self.arm_system)
        self.arm_button.pack(pady=5, fill=tk.X)
        
        self.launch_button = tk.Button(button_frame, text="LAUNCH", font=("Arial", 14, "bold"), 
                                       bg=self.colors['text_secondary'], fg=self.colors['bg_primary'], 
                                       relief=tk.FLAT, width=20, state=tk.DISABLED, command=self.launch_rocket)
        self.launch_button.pack(pady=5, fill=tk.X)
        
        self.abort_button = tk.Button(button_frame, text="ABORT", font=("Arial", 14, "bold"), 
                                      bg=self.colors['text_secondary'], fg=self.colors['bg_primary'], 
                                      relief=tk.FLAT, width=20, state=tk.DISABLED, command=self.abort_launch)
        self.abort_button.pack(pady=5, fill=tk.X)

    def setup_data_displays(self, parent):
        """Set up real-time data displays"""
        data_grid = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        data_grid.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)
        
        data_points = [
            ("PRESSURE", "PSI"),
            ("APOGEE", "ft"),
            ("TIME", "s"),
            ("HEIGHT", "ft"),
            ("VELOCITY", "ft/s")
        ]
        
        for i, (name, unit) in enumerate(data_points):
            data_grid.rowconfigure(i, weight=1)
            
            # Label
            label = tk.Label(data_grid, text=name, font=("Arial", 12), fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary'], anchor='w')
            label.grid(row=i, column=0, sticky='w')
            
            # Value
            value_label = tk.Label(data_grid, text="0 " + unit, font=("Arial", 20, "bold"), fg=self.colors['text_primary'], bg=self.colors['bg_tertiary'], anchor='e')
            value_label.grid(row=i, column=1, sticky='e')
            
            # Store references to labels we need to update
            if name == "PRESSURE":
                self.pressure_label = value_label
                value_label.config(fg=self.colors['accent_cyan'])
            elif name == "APOGEE":
                self.apogee_label = value_label
            elif name == "TIME":
                self.time_label = value_label
            elif name == "HEIGHT":
                self.height_label = value_label
            elif name == "VELOCITY":
                self.velocity_label = value_label
                
        data_grid.columnconfigure(1, weight=1)

    def setup_graphs_and_gauges(self, parent):
        """Set up graphs and pressure gauge"""
        
        # Top row for graphs
        graph_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pressure Graph
        pressure_graph_frame = tk.Frame(graph_frame, bg=self.colors['bg_tertiary'], bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground=self.colors['border'])
        pressure_graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        self.pressure_fig = Figure(figsize=(5, 4), dpi=100, facecolor=self.colors['bg_tertiary'])
        self.ax_pressure = self.pressure_fig.add_subplot(111)
        self.pressure_canvas = FigureCanvasTkAgg(self.pressure_fig, master=pressure_graph_frame)
        self.pressure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Height Graph
        height_graph_frame = tk.Frame(graph_frame, bg=self.colors['bg_tertiary'], bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground=self.colors['border'])
        height_graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        
        self.height_fig = Figure(figsize=(5, 4), dpi=100, facecolor=self.colors['bg_tertiary'])
        self.ax_height = self.height_fig.add_subplot(111)
        self.height_canvas = FigureCanvasTkAgg(self.height_fig, master=height_graph_frame)
        self.height_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bottom row for gauge
        gauge_frame_outer = tk.Frame(parent, bg=self.colors['bg_tertiary'], bd=1, relief=tk.SOLID, borderwidth=1, highlightbackground=self.colors['border'])
        gauge_frame_outer.pack(fill=tk.X, pady=(10, 0))
        tk.Label(gauge_frame_outer, text="LIVE PRESSURE GAUGE", font=("Arial", 16, "bold"), fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(10, 5))
        
        gauge_frame_inner = tk.Frame(gauge_frame_outer, bg=self.colors['bg_tertiary'])
        gauge_frame_inner.pack(pady=20)
        
        self.setup_pressure_gauge(gauge_frame_inner)

    def setup_pressure_gauge(self, parent):
        """Set up the pressure gauge visualization"""
        self.gauge_canvas = tk.Canvas(parent, width=200, height=100, bg=self.colors['bg_tertiary'], highlightthickness=0)
        self.gauge_canvas.pack()
        
        # Draw gauge background
        self.gauge_canvas.create_arc(10, 10, 190, 190, start=0, extent=180, style=tk.ARC, 
                                     outline=self.colors['border'], width=10)
        
        # Draw color zones
        self.gauge_canvas.create_arc(10, 10, 190, 190, start=0, extent=90, style=tk.ARC, 
                                     outline=self.colors['danger'], width=10) # 80-100%
        self.gauge_canvas.create_arc(10, 10, 190, 190, start=36, extent=54, style=tk.ARC, 
                                     outline=self.colors['warning'], width=10) # 50-80%
        self.gauge_canvas.create_arc(10, 10, 190, 190, start=90, extent=90, style=tk.ARC, 
                                     outline=self.colors['success'], width=10) # 0-50%
        
        # Add labels
        self.gauge_canvas.create_text(20, 100, text="0", fill=self.colors['text_secondary'], font=("Arial", 10))
        self.gauge_canvas.create_text(100, 20, text=f"{self.max_pressure // 2}", fill=self.colors['text_secondary'], font=("Arial", 10))
        self.gauge_canvas.create_text(180, 100, text=f"{self.max_pressure}", fill=self.colors['text_secondary'], font=("Arial", 10))
        
        # Draw needle
        self.needle = self.gauge_canvas.create_line(100, 100, 20, 100, width=3, fill=self.colors['accent_cyan'])
    
    def setup_serial_reader(self):
        """Set up the serial data reading thread"""
        self.simulation_running = True 
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()
        print("Serial reader thread started.")
        
    def read_serial_data(self):
        """
        Read data from the serial port in a separate thread
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
                            # Update the shared current_pressure variable
                            # The other thread (simulate_data) will read this
                            self.current_pressure = float(line) 
                            if self.serial_error: # Clear error if we get good data
                                self.serial_error = None
                    except (UnicodeDecodeError, ValueError) as e:
                        print(f"Serial data error: {e} - Received: '{line}'")
                else:
                    # Don't busy-wait
                    time.sleep(0.01)
        except serial.SerialException as e:
            print(f"Serial Error: {e}")
            self.serial_error = f"Error: Port {PORT} not found."
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
        Pressure is now read from self.current_pressure (set by serial thread).
        """
        start_time = time.time()
        
        while self.simulation_running:
            current_time = time.time() - start_time
            
            # --- PRESSURE LOGIC REMOVED ---
            if self.is_launching:
                # Launch phase simulation (HEIGHT AND VELOCITY ONLY)
                if current_time < 5:  # Boost phase
                    # pressure = min(self.max_pressure, 200 + (current_time * 150)) # REMOVED
                    height = current_time * current_time * 50
                    velocity = current_time * 100
                elif current_time < 15:  # Coast phase
                    # pressure = max(0, self.max_pressure - (current_time - 5) * 100) # REMOVED
                    height = 1250 + (current_time - 5) * 200 - (current_time - 5) ** 2 * 10
                    velocity = max(0, 500 - (current_time - 5) * 50)
                else:  # Descent phase
                    # pressure = 0 # REMOVED
                    height = max(0, self.apogee - (current_time - 15) * 100)
                    velocity = -(current_time - 15) * 50
            else:
                # Pre-launch simulation
                # pressure = random.uniform(0, 50) # REMOVED
                height = 0
                velocity = 0
            
            # Update data
            # self.current_pressure = pressure # REMOVED (set by serial thread)
            if height > self.apogee:
                self.apogee = height
            
            # Store data for graphs
            self.time_data.append(current_time)
            # --- KEY CHANGE: Use pressure from serial thread ---
            self.pressure_data.append(self.current_pressure)
            # --- END KEY CHANGE ---
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
            self.pressure_label.config(text=self.serial_error, fg=self.colors['danger'])
        else:
            self.pressure_label.config(text=f"{self.current_pressure:.0f} PSI", fg=self.colors['accent_cyan'])
            
        # Update data labels
        # self.pressure_label.config(text=f"{self.current_pressure:.0f} PSI") # Replaced by above
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
            # Clamp ratio between 0 and 1
            pressure_ratio = max(0, min(1, pressure_ratio)) 
            
            angle = pressure_ratio * 180  # Convert to degrees
            angle_rad = (180 - angle) * np.pi / 180 # Corrected angle for gauge
            
            # Calculate needle position
            needle_x = 100 - 45 * np.cos(angle_rad)
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
        
        # Update pressure graph
        self.ax_pressure.clear()
        self.ax_pressure.plot(self.time_data, self.pressure_data, color=self.colors['accent_cyan'], linewidth=2)
        self.ax_pressure.set_title("Pressure (PSI)", color=self.colors['text_primary'], fontsize=12)
        self.ax_pressure.set_xlabel("Time (s)", color=self.colors['text_secondary'], fontsize=10)
        self.ax_pressure.set_ylabel("Pressure", color=self.colors['text_secondary'], fontsize=10)
        self.ax_pressure.set_facecolor(self.colors['bg_secondary'])
        self.ax_pressure.tick_params(axis='x', colors=self.colors['text_secondary'])
        self.ax_pressure.tick_params(axis='y', colors=self.colors['text_secondary'])
        for spine in self.ax_pressure.spines.values():
            spine.set_edgecolor(self.colors['border'])
        self.pressure_fig.tight_layout()
        self.pressure_canvas.draw_idle()
        
        # Update height graph
        self.ax_height.clear()
        self.ax_height.plot(self.time_data, self.height_data, color=self.colors['accent_purple'], linewidth=2)
        self.ax_height.set_title("Height (ft)", color=self.colors['text_primary'], fontsize=12)
        self.ax_height.set_xlabel("Time (s)", color=self.colors['text_secondary'], fontsize=10)
        self.ax_height.set_ylabel("Height", color=self.colors['text_secondary'], fontsize=10)
        self.ax_height.set_facecolor(self.colors['bg_secondary'])
        self.ax_height.tick_params(axis='x', colors=self.colors['text_secondary'])
        self.ax_height.tick_params(axis='y', colors=self.colors['text_secondary'])
        for spine in self.ax_height.spines.values():
            spine.set_edgecolor(self.colors['border'])
        self.height_fig.tight_layout()
        self.height_canvas.draw_idle()

    def update_status_lights(self):
        """Update status indicator lights"""
        
        # Telemetry light (flashes if error, solid if OK)
        if self.serial_error:
            # Flash red
            color = self.colors['danger'] if int(time.time() * 2) % 2 == 0 else self.colors['bg_tertiary']
        else:
            # Solid cyan
            color = self.colors['accent_cyan']
        self.status_lights["TELEMETRY"][0].itemconfig(self.status_lights["TELEMETRY"][1], fill=color)

        # Armed light
        armed_color = self.colors['success'] if self.arm_button['state'] == tk.DISABLED else self.colors['text_secondary']
        self.status_lights["ARMED"][0].itemconfig(self.status_lights["ARMED"][1], fill=armed_color)
            
    def arm_system(self):
        """Arm the launch system"""
        if messagebox.askyesno("Arm System", "Are you sure you want to arm the launch system?"):
            self.arm_button.config(state=tk.DISABLED, bg=self.colors['text_secondary'])
            self.launch_button.config(state=tk.NORMAL, bg=self.colors['danger'])
            self.abort_button.config(state=tk.NORMAL, bg=self.colors['warning'])
            print("System ARMED.")
            
    def launch_rocket(self):
        """Launch the rocket"""
        if self.arm_button['state'] == tk.DISABLED:
            self.is_launching = True
            self.launch_time = datetime.now()
            self.apogee = 0
            self.launch_button.config(state=tk.DISABLED, bg=self.colors['text_secondary'])
            self.abort_button.config(state=tk.NORMAL, bg=self.colors['warning'])
            messagebox.showinfo("Launch Initiated", "Rocket launch sequence initiated!")
            
    def abort_launch(self):
        """Abort the launch"""
        if self.is_launching or self.arm_button['state'] == tk.DISABLED:
            self.is_launching = False
            self.launch_button.config(state=tk.DISABLED, bg=self.colors['text_secondary'])
            self.abort_button.config(state=tk.DISABLED, bg=self.colors['text_secondary'])
            self.arm_button.config(state=tk.NORMAL, bg=self.colors['warning'])
            messagebox.showwarning("System Disarmed", "System has been disarmed.")
            
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
