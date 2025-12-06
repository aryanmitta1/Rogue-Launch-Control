#!/usr/bin/env python3
"""
Rogue Launch Control - GUI Application
Optimized for 720p, Manual Connection Control, and High Performance.
"""

import sys
import os
import threading
import time
from datetime import datetime
import random

# serial imports
try:
    import serial
    import serial.tools.list_ports
except ImportError as e:
    print(f"Error importing pyserial: {e}")
    print("Please install pyserial: pip install pyserial")
    sys.exit(1)

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

# Default Baud Rate, if arduinos are operating at a different one, must update this. 
DEFAULT_BAUD_RATE = 9600

class LaunchControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rogue Launch Control")
        #Resolution: 720p
        self.root.geometry("1280x720")
        self.root.configure(bg='#0a0e1a')
        
        # Modern color scheme
        self.colors = {
            'bg_primary': '#0a0e1a',
            'bg_secondary': '#141822',
            'bg_tertiary': '#1e2330',
            'card_highlight': '#252b3a',
            'accent_blue': '#4A9EFF',
            'accent_cyan': '#1fc991',
            'accent_orange': '#ff6b6b',
            'accent_purple': '#9b7ede',
            'text_primary': '#ffffff',
            'text_secondary': '#a1a8b5',
            'text_muted': '#6b7280',
            'border': '#2d3440',
            'border_light': '#3d4450',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444'
        }
        
        self.fonts = {
            'title': ('Segoe UI', 24, 'bold'),
            'subtitle': ('Segoe UI', 12, 'bold'),
            'heading': ('Segoe UI', 11, 'bold'),
            'body': ('Segoe UI', 10, 'normal'),
            'data_value': ('Segoe UI', 16, 'bold'),
            'button': ('Segoe UI', 11, 'bold')
        }
        
        # Serial port management
        self.current_port = None
        self.serial_connection = None
        self.is_connected = False
        self.serial_thread = None
        self.simulation_thread = None
        
        # Thread control events
        self.stop_threads = threading.Event()
        
        # Data variables
        self.pressure_data = []
        self.time_data = []
        self.height_data = []
        self.max_pressure = 1000
        self.current_pressure = 0
        self.current_altitude = 0
        self.temperature = 0.0
        self.apogee = 0
        self.gps_latitude = 0.0
        self.gps_longitude = 0.0
        self.gps_valid = False
        self.serial_error = None
        
        # Output Log
        self.output_log = None
        
        # Create GUI elements
        self.setup_gui()
        
    def get_com_ports(self):
        """Scans for available serial ports and returns a list of names."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def setup_gui(self):
        """Set up the main GUI layout"""
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(header_frame, text="▐ LAUNCH CONTROL ▐", font=self.fonts['title'], 
                              fg=self.colors['accent_blue'], bg=self.colors['bg_primary'])
        title_label.pack(side=tk.LEFT, pady=10)
        
        self.status_badge = tk.Label(header_frame, text="● DISCONNECTED", font=self.fonts['subtitle'], 
                              fg=self.colors['text_muted'], bg=self.colors['bg_primary'])
        self.status_badge.pack(side=tk.RIGHT, pady=10, padx=10)
        
        # Main content
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left column (graphs)
        left_column = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.setup_graphs_and_gauges(left_column)
        
        # Right column (controls/data)
        right_column = tk.Frame(content_frame, bg=self.colors['bg_secondary'], width=300)
        right_column.pack(side=tk.RIGHT, fill=tk.Y)
        right_column.pack_propagate(False)
        
        # Connection Settings
        connection_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=1, relief=tk.FLAT)
        connection_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        self.setup_connection_settings(connection_frame)
        
        # Status
        status_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=1, relief=tk.FLAT)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        self.setup_status_indicators(status_frame)

        # Real-time data
        data_frame = tk.Frame(right_column, bg=self.colors['bg_tertiary'], bd=1, relief=tk.FLAT)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.setup_data_displays(data_frame)

    def setup_connection_settings(self, parent):
        tk.Label(parent, text="CONNECTION", font=self.fonts['subtitle'],
                 fg=self.colors['text_primary'], bg=self.colors['bg_tertiary']).pack(pady=(10, 5), anchor='w', padx=10)
        
        conn_grid = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        conn_grid.pack(pady=5, padx=10, fill=tk.X)

        # Port Dropdown
        self.port_options = self.get_com_ports()
        self.selected_port = tk.StringVar()
        
        if self.port_options:
            self.selected_port.set(self.port_options[0])
        else:
            self.selected_port.set("No Ports")

        # Refresh Button
        refresh_btn = tk.Button(conn_grid, text="⟳", command=self.refresh_ports,
                                font=('Segoe UI', 10), bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                                relief=tk.FLAT, width=3)
        refresh_btn.grid(row=0, column=2, padx=2)

        self.port_dropdown = ttk.Combobox(conn_grid, textvariable=self.selected_port, 
                                          values=self.port_options, state='readonly')
        self.port_dropdown.grid(row=0, column=0, columnspan=2, sticky='ew', padx=2)
        
        # Connect Button
        self.connect_btn = tk.Button(parent, text="CONNECT", 
                                   command=self.toggle_connection, 
                                   font=self.fonts['button'], 
                                   bg=self.colors['accent_cyan'], fg=self.colors['bg_primary'],
                                   relief=tk.FLAT, pady=5)
        self.connect_btn.pack(fill=tk.X, padx=10, pady=10)
        
        conn_grid.columnconfigure(0, weight=1)

    def refresh_ports(self):
        """Refreshes the list of available COM ports"""
        self.port_options = self.get_com_ports()
        self.port_dropdown['values'] = self.port_options
        if self.port_options:
            self.port_dropdown.current(0)
        else:
            self.selected_port.set("No Ports")

    def toggle_connection(self):
        """Handles connecting and disconnecting"""
        if not self.is_connected:
            # Connect
            port = self.selected_port.get()
            if port == "No Ports" or not port:
                messagebox.showerror("Error", "No serial port selected.")
                return
            
            self.current_port = port
            self.stop_threads.clear() #resets flag
            self.is_connected = True
            
            #Clear old data when toggling connection (makes sure graphs dont panic)
            self.time_data = []
            self.pressure_data = []
            self.height_data = []
            self.apogee = 0
            
            #Creating Log File Again
            try:
                self.output_log = open(f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "a")
            except Exception:
                pass

            # Start Threads
            self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.simulation_thread = threading.Thread(target=self.process_data, daemon=True)
            
            self.serial_thread.start()
            self.simulation_thread.start()
            
            # UI Updates
            self.connect_btn.config(text="DISCONNECT", bg=self.colors['danger'], fg='white')
            self.status_badge.config(text=f"● LIVE ({port})", fg=self.colors['success'])
            
        else:
            # Disconnect
            self.is_connected = False
            self.stop_threads.set() # Signal threads to stop
            
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                
            if self.output_log:
                self.output_log.close()
            
            # UI Updates
            self.connect_btn.config(text="CONNECT", bg=self.colors['accent_cyan'], fg=self.colors['bg_primary'])
            self.status_badge.config(text="● DISCONNECTED", fg=self.colors['text_muted'])

    def setup_status_indicators(self, parent):
        indicators = ["SYSTEM", "GPS", "PRESSURE", "ALTITUDE"]
        self.status_lights = {}
        
        grid = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        grid.pack(fill=tk.X, pady=5)

        for i, name in enumerate(indicators):
            frame = tk.Frame(grid, bg=self.colors['bg_tertiary'])
            frame.grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)
            
            canvas = tk.Canvas(frame, width=12, height=12, bg=self.colors['bg_tertiary'], highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=(0, 5))
            light = canvas.create_oval(2, 2, 10, 10, fill=self.colors['text_muted'], outline='')
            self.status_lights[name] = canvas, light
            
            tk.Label(frame, text=name, font=('Segoe UI', 9), fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_tertiary']).pack(side=tk.LEFT)
            
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    def setup_data_displays(self, parent):
        # Using a simpler grid for data
        self.data_labels = {}
        fields = [
            ("PRESSURE", "PSI", 'accent_cyan'),
            ("ALTITUDE", "FT", 'accent_purple'),
            ("TEMP", "°C", 'accent_orange'),
            ("APOGEE", "FT", 'text_primary'),
            ("VELOCITY", "FT/S", 'text_secondary')
        ]
        
        for name, unit, color in fields:
            f = tk.Frame(parent, bg=self.colors['bg_tertiary'])
            f.pack(fill=tk.X, pady=4, padx=5)
            
            tk.Label(f, text=name, font=('Segoe UI', 8), fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_tertiary']).pack(anchor='w')
            
            lbl = tk.Label(f, text=f"0.0 {unit}", font=self.fonts['data_value'], 
                         fg=self.colors[color], bg=self.colors['bg_tertiary'])
            lbl.pack(anchor='w')
            self.data_labels[name] = lbl

        # Small GPS Text area
        tk.Label(parent, text="LAT / LON", font=('Segoe UI', 8), fg=self.colors['text_secondary'],
                bg=self.colors['bg_tertiary']).pack(anchor='w', padx=5, pady=(10,0))
        self.gps_text = tk.Label(parent, text="--.--- / --.---", font=('Segoe UI', 10), 
                               fg=self.colors['text_primary'], bg=self.colors['bg_tertiary'])
        self.gps_text.pack(anchor='w', padx=5)

    def setup_graphs_and_gauges(self, parent):
        graph_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # 3. Figures Setup
        # Pressure Graph
        self.pressure_fig = Figure(figsize=(4, 3), dpi=100, facecolor=self.colors['bg_tertiary'])
        self.ax_pressure = self.pressure_fig.add_subplot(111)
        self.ax_pressure.set_facecolor(self.colors['bg_secondary'])
        self.setup_axis_style(self.ax_pressure, "Pressure (PSI)")
        
        # Initialize an empty line
        self.line_pressure, = self.ax_pressure.plot([], [], color=self.colors['accent_cyan'], lw=2)
        
        # Set INITIAL scales
        self.ax_pressure.set_ylim(0, 150)

        canvas_p = FigureCanvasTkAgg(self.pressure_fig, master=graph_frame)
        canvas_p.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
        self.pressure_canvas = canvas_p

        # Altitude Graph
        self.height_fig = Figure(figsize=(4, 3), dpi=100, facecolor=self.colors['bg_tertiary'])
        self.ax_height = self.height_fig.add_subplot(111)
        self.ax_height.set_facecolor(self.colors['bg_secondary'])
        self.setup_axis_style(self.ax_height, "Altitude (Ft)")
        
        # Initialize empty line
        self.line_height, = self.ax_height.plot([], [], color=self.colors['accent_purple'], lw=2)
        
        # Set INITIAL scales
        self.ax_height.set_ylim(0, 1000)

        canvas_h = FigureCanvasTkAgg(self.height_fig, master=graph_frame)
        canvas_h.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))
        self.height_canvas = canvas_h

    def setup_axis_style(self, ax, title):
        ax.set_title(title, color=self.colors['text_primary'], fontsize=10)
        ax.tick_params(colors=self.colors['text_secondary'], labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(self.colors['border'])
        ax.grid(True, alpha=0.1, color=self.colors['border'])

    def read_serial_data(self):
        """Worker thread for serial input"""
        print(f"Opening Serial: {self.current_port}")
        
        try:
            self.serial_connection = serial.Serial(self.current_port, DEFAULT_BAUD_RATE, timeout=1)
            self.serial_error = None
            
            while not self.stop_threads.is_set():
                if self.serial_connection.in_waiting:
                    try:
                        line = self.serial_connection.readline().decode('utf-8').strip()
                        if ',' in line:
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 3:
                                self.current_pressure = float(parts[0])
                                self.current_altitude = float(parts[1])
                                self.temperature = float(parts[2])
                                
                                # Log to file
                                if self.output_log:
                                    self.output_log.write(f"{datetime.now()},{line}\n")
                                    
                                self.serial_error = None
                    except Exception as e:
                        print(f"Read Error: {e}")
                else:
                    time.sleep(0.01)
                    
        except Exception as e:
            self.serial_error = str(e)
            print(f"Connection Error: {e}")

    def process_data(self):
        """Worker thread for data processing and UI updates"""
        start_time = time.time()
        
        while not self.stop_threads.is_set():
            current_time = time.time() - start_time
            
            # Store Data
            self.time_data.append(current_time)
            self.pressure_data.append(self.current_pressure)
            self.height_data.append(self.current_altitude)
            
            if self.current_altitude > self.apogee:
                self.apogee = self.current_altitude
            
            # Keep 600 points (Approx 30 seconds)
            if len(self.time_data) > 600:
                self.time_data.pop(0)
                self.pressure_data.pop(0)
                self.height_data.pop(0)

            # Schedule UI Update on main thread
            self.root.after_idle(self.update_display)
            
            # Sleep slightly longer to prevent UI flooding
            time.sleep(0.05)

    def update_display(self):
        """Updates UI elements. Uses optimized methods."""
        if not self.is_connected: return

        #label updates
        if self.serial_error:
            self.status_badge.config(text="● ERROR", fg=self.colors['danger'])
        else:
            self.data_labels["PRESSURE"].config(text=f"{self.current_pressure:.1f} PSI")
            self.data_labels["ALTITUDE"].config(text=f"{self.current_altitude:.0f} FT")
            self.data_labels["TEMP"].config(text=f"{self.temperature:.1f} °C")
            self.data_labels["APOGEE"].config(text=f"{self.apogee:.0f} FT")
            
            #Velocity estimate based on altitude
            vel = 0
            if len(self.height_data) > 5:
                vel = (self.height_data[-1] - self.height_data[-5]) / (self.time_data[-1] - self.time_data[-5])
            self.data_labels["VELOCITY"].config(text=f"{vel:.0f} FT/S")

        #Graphs are optimized by not clearing all the time
        if len(self.time_data) > 1:
            #Update data inside the existing line object
            self.line_pressure.set_data(self.time_data, self.pressure_data)
            self.line_height.set_data(self.time_data, self.height_data)
            
            #autoscaling
            max_p = max(self.pressure_data) if self.pressure_data else 0
            max_h = max(self.height_data) if self.height_data else 0
            
            limit_p = max(max_p * 1.2, 150)
            limit_h = max(max_h * 1.2, 1000)

            min_x = self.time_data[0]
            max_x = self.time_data[-1] + 1
            
            self.ax_pressure.set_xlim(min_x, max_x)
            self.ax_pressure.set_ylim(0, limit_p)
            
            self.ax_height.set_xlim(min_x, max_x)
            self.ax_height.set_ylim(0, limit_h)
            
            # Efficient redraw
            self.pressure_canvas.draw()
            self.height_canvas.draw()
        
        # blink lights
        tick = int(time.time() * 2) % 2 == 0
        sys_col = self.colors['success'] if self.is_connected else self.colors['text_muted']
        self.status_lights["SYSTEM"][0].itemconfig(self.status_lights["SYSTEM"][1], fill=sys_col)
        
        rx_col = self.colors['accent_cyan'] if not self.serial_error and tick else self.colors['text_muted']
        if self.serial_error: rx_col = self.colors['danger']
        self.status_lights["PRESSURE"][0].itemconfig(self.status_lights["PRESSURE"][1], fill=rx_col)

    def on_closing(self):
        self.stop_threads.set()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        if self.output_log:
            self.output_log.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = LaunchControlGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
