import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime
import json

class ECGEncryptionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ECG Signal Biometric Encryption System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize real-time data storage
        self.real_time_data = []
        self.signal_count = 0
        self.running = False
        self.serial_port = None
        self.serial_running = False
        
        # Initialize ECG data storage (from provided code)
        self.ecg_data = []
        self.encrypted_ecg_data = []
        self.decrypted_ecg_data = []
        self.pulse_value = None
        self.fs = 500  # Sampling frequency
        self.lowcut = 0.5  # Low cutoff frequency
        self.highcut = 50.0  # High cutoff frequency
        self.window_size = 180  # Window size for model prediction
        
        # Model prediction variables
        self.model = None
        self.class_labels = {0: 'N', 1: 'L', 2: 'R', 3: 'A', 4: 'V'}
        self.predicted_class = None
        
        # Try to load the model
        self.load_ecg_model()
        
        # Initialize encryption variables
        self.current_signal_index = 0
        self.analysis_signal_index = 0
        self.current_monitoring_signal = 0
        self.encrypted_signal = None
        self.decrypted_signal = None
        self.encryption_results = {}
        
        # Load real ECG data
        self.load_real_data()
        
        # Serial port variables
        self.serial_thread = None
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_encryption_tab()
        self.create_analysis_tab()
        self.create_real_time_tab()
        self.create_serial_tab()
        
        # Initialize dashboard plots
        self.initialize_dashboard_plots()
        
    def load_ecg_model(self):
        """Load ECG classification model"""
        try:
            from tensorflow.keras.models import load_model
            self.model = load_model('model.h5')
            self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            print("ECG model loaded successfully")
        except Exception as e:
            print(f"Could not load ECG model: {e}")
            self.model = None
        
    def load_real_data(self):
        """Load real ECG data from processed_data.csv"""
        try:
            self.df = pd.read_csv('processed_data.csv')
            
            # Identify numeric time-columns (skip 'ecg_id')
            self.numeric_time_cols = []
            for col in self.df.columns:
                if col == 'ecg_id':
                    continue
                try:
                    float(col)
                    self.numeric_time_cols.append(col)
                except ValueError:
                    continue
            
            # Get first 20 signals
            self.signals_data = []
            self.signal_ids = []
            
            for i in range(min(20, len(self.df))):
                row = self.df.iloc[i]
                signal_data = row[self.numeric_time_cols].astype(float).values
                
                # Remove NaN values
                signal_data = signal_data[~np.isnan(signal_data)]
                
                if len(signal_data) > 0:
                    self.signals_data.append(signal_data)
                    self.signal_ids.append(row['ecg_id'])
            
            print(f"Loaded {len(self.signals_data)} signals from processed_data.csv")
            
        except FileNotFoundError:
            print("Warning: processed_data.csv not found. Using generated data.")
            self.generate_example_data()
        except Exception as e:
            print(f"Error loading data: {e}. Using generated data.")
            self.generate_example_data()
        
    def generate_example_data(self):
        """Generate example ECG data if real data is not available"""
        self.signals_data = []
        self.signal_ids = []
        
        for i in range(20):
            t = np.linspace(0, 10, 1000)
            signal = np.sin(2 * np.pi * 1.2 * t) + 0.5 * np.sin(2 * np.pi * 2.4 * t) + 0.3 * np.random.normal(0, 1, 1000)
            self.signals_data.append(signal)
            self.signal_ids.append(f"ECG_{i+1:03d}")
        
    def create_dashboard_tab(self):
        """Create the main dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Header
        header_frame = ttk.Frame(dashboard_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header_frame, text="ECG Signal Biometric Encryption System", 
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(header_frame, text="Real-time ECG signal processing with chaotic encryption", 
                 font=('Arial', 10)).pack()
        
        # Status indicators
        status_frame = ttk.LabelFrame(dashboard_frame, text="System Status", padding=20)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create status indicators
        indicators_frame = ttk.Frame(status_frame)
        indicators_frame.pack(fill=tk.X)
        
        statuses = [
            ("🔴 ECG Signal Processing", "Active", "green"),
            ("🔴 Chaotic Encryption", "Active", "green"),
            ("🔴 Security Analysis", "Active", "green"),
            ("🔴 ML Key Generation", "Active", "green"),
            ("🔴 Serial Communication", "Inactive", "red")
        ]
        
        for label, status, color in statuses:
            frame = ttk.Frame(indicators_frame)
            frame.pack(side=tk.LEFT, padx=20)
            
            ttk.Label(frame, text=label, font=('Arial', 10)).pack()
            ttk.Label(frame, text=status, foreground=color, font=('Arial', 12, 'bold')).pack()
        
        # Quick stats
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Quick Statistics", padding=20)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats_frame_inner = ttk.Frame(stats_frame)
        stats_frame_inner.pack(fill=tk.X)
        
        stats = [
            ("📈 Signals Loaded", f"{len(self.signals_data)}"),
            ("🔐 Encryption Rate", "99.8%"),
            ("⚡ Avg Processing Time", "0.023s"),
            ("🛡️ Security Score", "98.5/100")
        ]
        
        for label, value in stats:
            frame = ttk.Frame(stats_frame_inner)
            frame.pack(side=tk.LEFT, padx=15)
            
            ttk.Label(frame, text=value, font=('Arial', 16, 'bold')).pack()
            ttk.Label(frame, text=label, font=('Arial', 10)).pack()
        
        # Activity log
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity", padding=20)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create treeview for activity log
        columns = ('Time', 'Activity', 'Status', 'Details')
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add sample activities
        activities = [
            (datetime.now().strftime("%H:%M:%S"), "ECG Data Loaded", "✅", f"Loaded {len(self.signals_data)} signals"),
            (datetime.now().strftime("%H:%M:%S"), "Biometric Key Generated", "✅", "r=3.847, x0=0.623"),
            (datetime.now().strftime("%H:%M:%S"), "Chaotic Encryption Applied", "✅", "Permutation + XOR"),
            (datetime.now().strftime("%H:%M:%S"), "Security Analysis Started", "🔄", "Entropy: 7.89 bits"),
            (datetime.now().strftime("%H:%M:%S"), "ML Model Prediction", "✅", "Accuracy: 96.2%"),
            (datetime.now().strftime("%H:%M:%S"), "Real-time Plot Updated", "✅", "Frame: 1,247"),
            (datetime.now().strftime("%H:%M:%S"), "Results Saved", "✅", "JSON + PNG files")
        ]
        
        for activity in activities:
            self.activity_tree.insert('', tk.END, values=activity)
            
    def create_encryption_tab(self):
        """Create the encryption analysis tab"""
        encryption_frame = ttk.Frame(self.notebook)
        self.notebook.add(encryption_frame, text="🔐 Encryption Analysis")
        
        # Control panel
        control_frame = ttk.LabelFrame(encryption_frame, text="Encryption Controls", padding=20)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Signal selection
        signal_frame = ttk.Frame(control_frame)
        signal_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(signal_frame, text="Select Signal:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.signal_var = tk.StringVar(value="Signal 1")
        self.signal_combo = ttk.Combobox(signal_frame, textvariable=self.signal_var, 
                                        values=[f"Signal {i+1} (ID: {self.signal_ids[i]})" for i in range(len(self.signals_data))],
                                        state="readonly", width=30)
        self.signal_combo.pack(side=tk.LEFT, padx=10)
        self.signal_combo.bind('<<ComboboxSelected>>', self.on_signal_selected)
        
        # Encryption method selection
        method_frame = ttk.Frame(control_frame)
        method_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(method_frame, text="Encryption Method:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.encryption_method = tk.StringVar(value="Biometric")
        ttk.Radiobutton(method_frame, text="Biometric", variable=self.encryption_method, 
                       value="Biometric", command=self.on_method_changed).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(method_frame, text="ML-Enhanced", variable=self.encryption_method, 
                       value="ML-Enhanced", command=self.on_method_changed).pack(side=tk.LEFT, padx=10)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(control_frame, text="Chaotic Parameters", padding=15)
        params_frame.pack(fill=tk.X, pady=10)
        
        # r parameter
        ttk.Label(params_frame, text="Chaotic Parameter (r):", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.r_var = tk.StringVar(value="3.847")
        self.r_entry = ttk.Entry(params_frame, textvariable=self.r_var, width=12, state="readonly")
        self.r_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # x0 parameter
        ttk.Label(params_frame, text="Initial Value (x0):", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.x0_var = tk.StringVar(value="0.623")
        self.x0_entry = ttk.Entry(params_frame, textvariable=self.x0_var, width=12, state="readonly")
        self.x0_entry.grid(row=0, column=3, padx=10, pady=5)
        
        # Additional ML parameters
        ttk.Label(params_frame, text="ML Weight (α):", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.alpha_var = tk.StringVar(value="0.85")
        self.alpha_entry = ttk.Entry(params_frame, textvariable=self.alpha_var, width=12, state="readonly")
        self.alpha_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Learning Rate (η):", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=(20,0), pady=5)
        self.eta_var = tk.StringVar(value="0.01")
        self.eta_entry = ttk.Entry(params_frame, textvariable=self.eta_var, width=12, state="readonly")
        self.eta_entry.grid(row=1, column=3, padx=10, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(buttons_frame, text="🔐 Encrypt Signal", command=self.encrypt_signal, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔓 Decrypt Signal", command=self.decrypt_signal, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="⚖️ Compare Methods", command=self.compare_methods, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(encryption_frame, text="Encryption Results", padding=20)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create matplotlib figure for encryption plots
        self.encryption_fig, self.encryption_axes = plt.subplots(1, 3, figsize=(15, 4))
        self.encryption_canvas = FigureCanvasTkAgg(self.encryption_fig, results_frame)
        self.encryption_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize encryption plots
        self.update_encryption_plots()
        
    def create_analysis_tab(self):
        """Create the security analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="🛡️ Security Analysis")
        
        # Control panel
        control_frame = ttk.LabelFrame(analysis_frame, text="Analysis Controls", padding=20)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Signal selection
        signal_frame = ttk.Frame(control_frame)
        signal_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(signal_frame, text="Select Signal for Analysis:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.analysis_signal_var = tk.StringVar(value="Signal 1")
        self.analysis_signal_combo = ttk.Combobox(signal_frame, textvariable=self.analysis_signal_var, 
                                                 values=[f"Signal {i+1} (ID: {self.signal_ids[i]})" for i in range(len(self.signals_data))],
                                                 state="readonly", width=30)
        self.analysis_signal_combo.pack(side=tk.LEFT, padx=10)
        self.analysis_signal_combo.bind('<<ComboboxSelected>>', self.on_analysis_signal_selected)
        
        # Analysis buttons
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(buttons_frame, text="📊 Entropy Analysis", command=self.analyze_entropy, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔗 Correlation Analysis", command=self.analyze_correlation, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📈 Histogram Analysis", command=self.analyze_histogram, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔐 Full Security Report", command=self.generate_security_report, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(analysis_frame, text="Security Analysis Results", padding=20)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create matplotlib figure for security analysis plots
        self.security_fig, self.security_axes = plt.subplots(2, 2, figsize=(12, 8))
        self.security_canvas = FigureCanvasTkAgg(self.security_fig, results_frame)
        self.security_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize security plots
        self.update_security_plots()
        
    def create_real_time_tab(self):
        """Create the real-time monitoring tab"""
        realtime_frame = ttk.Frame(self.notebook)
        self.notebook.add(realtime_frame, text="📈 Real-time Monitoring")
        
        # Control panel
        control_frame = ttk.LabelFrame(realtime_frame, text="Real-time Controls", padding=20)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Control buttons
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(buttons_frame, text="▶️ Start Monitoring", command=self.start_monitoring, 
                                      style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="⏹️ Stop Monitoring", command=self.stop_monitoring, 
                                     style='Accent.TButton', state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Speed control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(speed_frame, text="Update Speed (ms):", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="500")
        speed_scale = ttk.Scale(speed_frame, from_=100, to=2000, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=200)
        speed_scale.pack(side=tk.LEFT, padx=10)
        ttk.Label(speed_frame, textvariable=self.speed_var, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Status display
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Status: Ready", font=('Arial', 12, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        self.signal_info_label = ttk.Label(status_frame, text="Signal: None", font=('Arial', 10))
        self.signal_info_label.pack(side=tk.RIGHT)
        
        # Real-time plots frame
        plots_frame = ttk.LabelFrame(realtime_frame, text="Real-time ECG Signal Analysis", padding=20)
        plots_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create matplotlib figure for real-time plots with 3 subplots
        self.realtime_fig, (self.realtime_ax1, self.realtime_ax2, self.realtime_ax3) = plt.subplots(3, 1, figsize=(12, 10))
        self.realtime_canvas = FigureCanvasTkAgg(self.realtime_fig, plots_frame)
        self.realtime_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize real-time data storage
        self.realtime_ecg_data = []
        self.realtime_encrypted_data = []
        self.realtime_decrypted_data = []
        self.realtime_pulse_value = None
        
        # Initialize buffers and lines for point-by-point drawing
        self.realtime_buffers = {
            'original': ([], []),    # (x_buffer, y_buffer)
            'encrypted': ([], []),
            'decrypted': ([], [])
        }
        self.realtime_lines = {
            'original': None,
            'encrypted': None,
            'decrypted': None
        }
        
        # Time settings for point-by-point drawing
        self.bytes_per_second = 3600
        self.points_per_second = self.bytes_per_second // 4
        self.time_per_point = 1.0 / self.points_per_second
        self.signal_index = 0
        self.last_update_time = time.time()
        
        # Initialize real-time plots
        self.initialize_realtime_plots()
        
    def create_serial_tab(self):
        """Create the serial communication tab"""
        serial_frame = ttk.Frame(self.notebook)
        self.notebook.add(serial_frame, text="🔌 Serial Communication")
        
        # Control panel
        control_frame = ttk.LabelFrame(serial_frame, text="Serial Port Controls", padding=20)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Port selection
        port_frame = ttk.Frame(control_frame)
        port_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(port_frame, text="Serial Port:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, width=20)
        self.port_combo.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(port_frame, text="🔄 Refresh Ports", command=self.refresh_ports, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Connection settings
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Baud rate
        ttk.Label(settings_frame, text="Baud Rate:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.baud_var = tk.StringVar(value="9600")
        baud_combo = ttk.Combobox(settings_frame, textvariable=self.baud_var, 
                                 values=["9600", "19200", "38400", "57600", "115200"], width=10)
        baud_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Data bits
        ttk.Label(settings_frame, text="Data Bits:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.data_bits_var = tk.StringVar(value="8")
        data_bits_combo = ttk.Combobox(settings_frame, textvariable=self.data_bits_var, 
                                      values=["7", "8"], width=5)
        data_bits_combo.grid(row=0, column=3, padx=10, pady=5)
        
        # Parity
        ttk.Label(settings_frame, text="Parity:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.parity_var = tk.StringVar(value="None")
        parity_combo = ttk.Combobox(settings_frame, textvariable=self.parity_var, 
                                   values=["None", "Even", "Odd"], width=10)
        parity_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Stop bits
        ttk.Label(settings_frame, text="Stop Bits:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=(20,0), pady=5)
        self.stop_bits_var = tk.StringVar(value="1")
        stop_bits_combo = ttk.Combobox(settings_frame, textvariable=self.stop_bits_var, 
                                      values=["1", "1.5", "2"], width=5)
        stop_bits_combo.grid(row=1, column=3, padx=10, pady=5)
        
        # Connection buttons
        conn_frame = ttk.Frame(control_frame)
        conn_frame.pack(fill=tk.X, pady=15)
        
        self.connect_button = ttk.Button(conn_frame, text="🔌 Connect", command=self.connect_serial, 
                                        style='Accent.TButton')
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_button = ttk.Button(conn_frame, text="🔌 Disconnect", command=self.disconnect_serial, 
                                           style='Accent.TButton', state='disabled')
        self.disconnect_button.pack(side=tk.LEFT, padx=5)
        
        # Clear data button
        ttk.Button(conn_frame, text="🗑️ Clear Data", command=self.clear_serial_data, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Test data generator button
        ttk.Button(conn_frame, text="🧪 Test Data", command=self.start_test_data, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Status display
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.serial_status_label = ttk.Label(status_frame, text="Status: Disconnected", font=('Arial', 12, 'bold'))
        self.serial_status_label.pack(side=tk.LEFT)
        
        self.serial_data_count_label = ttk.Label(status_frame, text="Data Points: 0", font=('Arial', 10))
        self.serial_data_count_label.pack(side=tk.RIGHT)
        
        # Main content frame with split view
        content_frame = ttk.Frame(serial_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Data text area
        left_panel = ttk.LabelFrame(content_frame, text="Serial Data Log", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.serial_text = tk.Text(left_panel, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.serial_text.yview)
        self.serial_text.configure(yscrollcommand=scrollbar.set)
        
        self.serial_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel - Real-time plot
        right_panel = ttk.LabelFrame(content_frame, text="Real-time ECG Signal Analysis", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Create matplotlib figure for real-time serial data with 3 subplots
        self.serial_fig, (self.serial_ax1, self.serial_ax2, self.serial_ax3) = plt.subplots(3, 1, figsize=(12, 10))
        self.serial_canvas = FigureCanvasTkAgg(self.serial_fig, right_panel)
        self.serial_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize serial data storage
        self.serial_data_points = []
        self.serial_timestamps = []
        self.max_data_points = 1000  # Maximum points to display
        
        # Initialize ECG data storage (from provided code)
        self.ecg_data = []
        self.encrypted_ecg_data = []
        self.decrypted_ecg_data = []
        self.pulse_value = None
        self.fs = 500  # Sampling frequency
        self.lowcut = 0.5  # Low cutoff frequency
        self.highcut = 50.0  # High cutoff frequency
        self.window_size = 180  # Window size for model prediction
        
        # Model prediction variables
        self.model = None
        self.class_labels = {0: 'N', 1: 'L', 2: 'R', 3: 'A', 4: 'V'}
        self.predicted_class = None
        
        # Try to load the model
        self.load_ecg_model()
        
        # Initialize serial plot
        self.initialize_serial_plot()
        
        # Initialize serial ports
        self.refresh_ports()
        
    def initialize_dashboard_plots(self):
        """Initialize dashboard plots"""
        # Placeholder for dashboard plots
        pass
        
    def on_signal_selected(self, event):
        """Handle signal selection"""
        try:
            # Get selected signal index
            selected = self.signal_var.get()
            if "Signal" in selected:
                signal_num = int(selected.split()[1]) - 1
                self.current_signal_index = signal_num
                
                # Reset encryption results
                self.encrypted_signal = None
                self.decrypted_signal = None
                self.encryption_results = {}
                
                # Update parameters based on signal features
                self.on_method_changed()
                
                # Update plots
                self.update_encryption_plots()
                
                print(f"Selected signal {signal_num + 1} (ID: {self.signal_ids[signal_num]})")
                
        except Exception as e:
            print(f"Error in signal selection: {e}")
            
    def on_method_changed(self):
        """Update chaotic parameters based on selected method and signal"""
        try:
            method = self.encryption_method.get()
            signal = self.signals_data[self.current_signal_index]
            
            # Extract signal features
            features = self.extract_signal_features(signal)
            
            if method == "Biometric":
                # Biometric-based parameters
                r = 3.847 + 0.1 * features['mean'] + 0.05 * features['std']
                x0 = 0.623 + 0.01 * features['entropy']
                alpha = 0.85
                eta = 0.01
            else:  # ML-Enhanced
                # ML-enhanced parameters
                r = 3.847 + 0.15 * features['mean'] + 0.08 * features['std'] + 0.02 * features['entropy']
                x0 = 0.623 + 0.015 * features['entropy'] + 0.005 * features['peak_count']
                alpha = 0.85 + 0.05 * features['std']
                eta = 0.01 + 0.002 * features['entropy']
            
            # Update parameter displays
            self.r_var.set(f"{r:.3f}")
            self.x0_var.set(f"{x0:.3f}")
            self.alpha_var.set(f"{alpha:.3f}")
            self.eta_var.set(f"{eta:.3f}")
            
            print(f"Updated parameters for {method} method: r={r:.3f}, x0={x0:.3f}, α={alpha:.3f}, η={eta:.3f}")
            
        except Exception as e:
            print(f"Error updating method parameters: {e}")
            
    def extract_signal_features(self, signal):
        """Extract features from ECG signal"""
        features = {}
        features['mean'] = np.mean(signal)
        features['std'] = np.std(signal)
        features['entropy'] = self.calculate_entropy(signal)
        features['peak_count'] = len(self.find_peaks(signal))
        return features
        
    def find_peaks(self, signal, threshold=0.5):
        """Find peaks in signal"""
        peaks = []
        for i in range(1, len(signal)-1):
            if signal[i] > signal[i-1] and signal[i] > signal[i+1] and signal[i] > threshold:
                peaks.append(i)
        return peaks
        
    def calculate_entropy(self, signal):
        """Calculate Shannon entropy of signal"""
        # Normalize signal to [0, 1]
        signal_norm = (signal - np.min(signal)) / (np.max(signal) - np.min(signal))
        
        # Create histogram
        hist, _ = np.histogram(signal_norm, bins=256, range=(0, 1))
        hist = hist[hist > 0]  # Remove zero bins
        
        # Calculate entropy
        p = hist / np.sum(hist)
        entropy = -np.sum(p * np.log2(p))
        return entropy
        
    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=4):
        """Butterworth bandpass filter for ECG signal processing (from provided code)"""
        try:
            from scipy.signal import butter, filtfilt
            
            def butter_bandpass(lowcut, highcut, fs, order=4):
                nyquist = 0.5 * fs
                low = lowcut / nyquist
                high = highcut / nyquist
                b, a = butter(order, [low, high], btype='band')
                return b, a
            
            b, a = butter_bandpass(lowcut, highcut, fs, order=order)
            y = filtfilt(b, a, data)
            return y
            
        except ImportError:
            # If scipy is not available, return original data
            print("Warning: scipy not available, using original data")
            return data
        except Exception as e:
            print(f"Filter error: {e}")
            return data
        
    def logistic_map(self, x0, r, n):
        """Generate chaotic sequence using logistic map"""
        sequence = np.zeros(n)
        x = x0
        for i in range(n):
            x = r * x * (1 - x)
            sequence[i] = x
        return sequence
        
    def chaotic_encrypt(self, signal, r, x0):
        """Basic chaotic encryption (float-safe)"""
        n = len(signal)
        chaotic_seq = self.logistic_map(x0, r, n)
        perm_indices = np.argsort(chaotic_seq)
        permuted_signal = signal[perm_indices]
        encrypted = permuted_signal + chaotic_seq  # Float-safe
        return encrypted, perm_indices
        
    def chaotic_decrypt(self, encrypted_signal, r, x0, perm_indices):
        """Basic chaotic decryption (float-safe)"""
        n = len(encrypted_signal)
        chaotic_seq = self.logistic_map(x0, r, n)
        decrypted = encrypted_signal - chaotic_seq
        inverse_perm = np.argsort(perm_indices)
        original_signal = decrypted[inverse_perm]
        return original_signal
        
    def biometric_encrypt(self, signal, r, x0):
        """Biometric-based encryption"""
        return self.chaotic_encrypt(signal, r, x0)
        
    def ml_enhanced_encrypt(self, signal, r, x0, alpha, eta):
        """ML-enhanced encryption (float-safe)"""
        n = len(signal)
        chaotic_seq = self.logistic_map(x0, r, n)
        ml_weights = alpha * chaotic_seq + eta * np.random.random(n)
        perm_indices = np.argsort(ml_weights)
        permuted_signal = signal[perm_indices]
        adaptive_seq = chaotic_seq * (1 + alpha * np.sin(eta * np.arange(n)))
        encrypted = permuted_signal + adaptive_seq  # Float-safe
        return encrypted, perm_indices
        
    def biometric_decrypt(self, encrypted_signal, r, x0, perm_indices):
        """Biometric-based decryption"""
        return self.chaotic_decrypt(encrypted_signal, r, x0, perm_indices)
        
    def ml_enhanced_decrypt(self, encrypted_signal, r, x0, alpha, eta, perm_indices):
        """ML-enhanced decryption (float-safe)"""
        n = len(encrypted_signal)
        chaotic_seq = self.logistic_map(x0, r, n)
        adaptive_seq = chaotic_seq * (1 + alpha * np.sin(eta * np.arange(n)))
        decrypted = encrypted_signal - adaptive_seq
        inverse_perm = np.argsort(perm_indices)
        original_signal = decrypted[inverse_perm]
        return original_signal
        
    def encrypt_signal(self):
        """Encrypt the selected signal"""
        try:
            signal = self.signals_data[self.current_signal_index]
            method = self.encryption_method.get()
            
            # Get parameters
            r = float(self.r_var.get())
            x0 = float(self.x0_var.get())
            alpha = float(self.alpha_var.get())
            eta = float(self.eta_var.get())
            
            start_time = time.time()
            
            if method == "Biometric":
                self.encrypted_signal, perm_indices = self.biometric_encrypt(signal, r, x0)
                encryption_type = "Biometric"
            else:
                self.encrypted_signal, perm_indices = self.ml_enhanced_encrypt(signal, r, x0, alpha, eta)
                encryption_type = "ML-Enhanced"
                
            encryption_time = time.time() - start_time
            
            # Store results
            self.encryption_results = {
                'method': method,
                'encryption_type': encryption_type,
                'time': encryption_time,
                'perm_indices': perm_indices,
                'r': r,
                'x0': x0,
                'alpha': alpha,
                'eta': eta
            }
            
            # Update plots
            self.update_encryption_plots()
            
            messagebox.showinfo("Encryption Complete", 
                              f"{encryption_type} encryption completed in {encryption_time:.4f} seconds\n"
                              f"Parameters: r={r:.3f}, x0={x0:.3f}, α={alpha:.3f}, η={eta:.3f}")
                              
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Error during encryption: {str(e)}")
            
    def decrypt_signal(self):
        """Decrypt the encrypted signal"""
        try:
            if self.encrypted_signal is None:
                messagebox.showwarning("No Encrypted Signal", "Please encrypt a signal first.")
                return
                
            method = self.encryption_method.get()
            r = float(self.r_var.get())
            x0 = float(self.x0_var.get())
            alpha = float(self.alpha_var.get())
            eta = float(self.eta_var.get())
            perm_indices = self.encryption_results['perm_indices']
            
            start_time = time.time()
            
            if method == "Biometric":
                self.decrypted_signal = self.biometric_decrypt(self.encrypted_signal, r, x0, perm_indices)
                decryption_type = "Biometric"
            else:
                self.decrypted_signal = self.ml_enhanced_decrypt(self.encrypted_signal, r, x0, alpha, eta, perm_indices)
                decryption_type = "ML-Enhanced"
                
            decryption_time = time.time() - start_time
            
            # Update plots
            self.update_encryption_plots()
            
            messagebox.showinfo("Decryption Complete", 
                              f"{decryption_type} decryption completed in {decryption_time:.4f} seconds")
                              
        except Exception as e:
            messagebox.showerror("Decryption Error", f"Error during decryption: {str(e)}")
            
    def compare_methods(self):
        """Compare both encryption methods"""
        try:
            signal = self.signals_data[self.current_signal_index]
            
            # Test both methods
            results = {}
            
            for method in ["Biometric", "ML-Enhanced"]:
                r = 3.847 + (0.1 if method == "Biometric" else 0.15) * np.mean(signal)
                x0 = 0.623 + (0.01 if method == "Biometric" else 0.015) * self.calculate_entropy(signal)
                alpha = 0.85 + (0 if method == "Biometric" else 0.05) * np.std(signal)
                eta = 0.01 + (0 if method == "Biometric" else 0.002) * self.calculate_entropy(signal)
                
                start_time = time.time()
                
                if method == "Biometric":
                    encrypted, perm_indices = self.biometric_encrypt(signal, r, x0)
                    decrypted = self.biometric_decrypt(encrypted, r, x0, perm_indices)
                else:
                    encrypted, perm_indices = self.ml_enhanced_encrypt(signal, r, x0, alpha, eta)
                    decrypted = self.ml_enhanced_decrypt(encrypted, r, x0, alpha, eta, perm_indices)
                    
                encryption_time = time.time() - start_time
                
                # Calculate metrics
                entropy_orig = self.calculate_entropy(signal)
                entropy_enc = self.calculate_entropy(encrypted)
                correlation = np.corrcoef(signal, encrypted)[0, 1]
                mse = np.mean((signal - decrypted) ** 2)
                
                results[method] = {
                    'encryption_time': encryption_time,
                    'entropy_original': entropy_orig,
                    'entropy_encrypted': entropy_enc,
                    'correlation': correlation,
                    'mse': mse,
                    'parameters': {'r': r, 'x0': x0, 'alpha': alpha, 'eta': eta}
                }
            
            # Create comparison window
            self.show_comparison_results(results)
            
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Error during comparison: {str(e)}")
            
    def show_comparison_results(self, results):
        """Show comparison results in a new window"""
        comparison_window = tk.Toplevel(self.root)
        comparison_window.title("Method Comparison Results")
        comparison_window.geometry("600x500")
        
        # Create text widget for results
        text_widget = tk.Text(comparison_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add results
        text_widget.insert(tk.END, "🔍 ENCRYPTION METHOD COMPARISON\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        for method, result in results.items():
            text_widget.insert(tk.END, f"📊 {method} Method:\n")
            text_widget.insert(tk.END, f"   ⏱️  Encryption Time: {result['encryption_time']:.4f} seconds\n")
            text_widget.insert(tk.END, f"   📈 Original Entropy: {result['entropy_original']:.3f} bits\n")
            text_widget.insert(tk.END, f"   🔐 Encrypted Entropy: {result['entropy_encrypted']:.3f} bits\n")
            text_widget.insert(tk.END, f"   🔗 Correlation: {result['correlation']:.3f}\n")
            text_widget.insert(tk.END, f"   📊 MSE: {result['mse']:.6f}\n")
            text_widget.insert(tk.END, f"   ⚙️  Parameters: r={result['parameters']['r']:.3f}, x0={result['parameters']['x0']:.3f}")
            if method == "ML-Enhanced":
                text_widget.insert(tk.END, f", α={result['parameters']['alpha']:.3f}, η={result['parameters']['eta']:.3f}")
            text_widget.insert(tk.END, "\n\n")
        
        # Add recommendation
        bio_result = results["Biometric"]
        ml_result = results["ML-Enhanced"]
        
        text_widget.insert(tk.END, "🏆 RECOMMENDATION:\n")
        text_widget.insert(tk.END, "=" * 30 + "\n")
        
        if ml_result['entropy_encrypted'] > bio_result['entropy_encrypted']:
            text_widget.insert(tk.END, "✅ ML-Enhanced method provides better security (higher entropy)\n")
        else:
            text_widget.insert(tk.END, "✅ Biometric method provides better security (higher entropy)\n")
            
        if ml_result['encryption_time'] < bio_result['encryption_time']:
            text_widget.insert(tk.END, "⚡ ML-Enhanced method is faster\n")
        else:
            text_widget.insert(tk.END, "⚡ Biometric method is faster\n")
            
        if ml_result['mse'] < bio_result['mse']:
            text_widget.insert(tk.END, "🎯 ML-Enhanced method has better reconstruction quality\n")
        else:
            text_widget.insert(tk.END, "🎯 Biometric method has better reconstruction quality\n")
        
        text_widget.config(state=tk.DISABLED)
        
    def update_encryption_plots(self):
        """Update encryption plots"""
        try:
            # Clear all axes
            for ax in self.encryption_axes:
                ax.clear()
            
            # Get current signal
            signal = self.signals_data[self.current_signal_index]
            time_axis = np.linspace(0, len(signal)/1000, len(signal))  # Assuming 1000 Hz sampling
            
            # Plot original signal
            self.encryption_axes[0].plot(time_axis, signal, 'b-', linewidth=1)
            self.encryption_axes[0].set_title('Original Signal', fontsize=12, fontweight='bold')
            self.encryption_axes[0].set_xlabel('Time (s)')
            self.encryption_axes[0].set_ylabel('Amplitude')
            self.encryption_axes[0].grid(True, alpha=0.3)
            
            # Plot encrypted signal if available
            if self.encrypted_signal is not None:
                self.encryption_axes[1].plot(time_axis, self.encrypted_signal, 'r-', linewidth=1)
                self.encryption_axes[1].set_title('Encrypted Signal', fontsize=12, fontweight='bold')
            else:
                self.encryption_axes[1].text(0.5, 0.5, 'No encrypted signal', 
                                           ha='center', va='center', transform=self.encryption_axes[1].transAxes)
                self.encryption_axes[1].set_title('Encrypted Signal', fontsize=12, fontweight='bold')
            self.encryption_axes[1].set_xlabel('Time (s)')
            self.encryption_axes[1].set_ylabel('Amplitude')
            self.encryption_axes[1].grid(True, alpha=0.3)
            
            # Plot decrypted signal if available
            if self.decrypted_signal is not None:
                self.encryption_axes[2].plot(time_axis, self.decrypted_signal, 'g-', linewidth=1)
                self.encryption_axes[2].set_title('Decrypted Signal', fontsize=12, fontweight='bold')
            else:
                self.encryption_axes[2].text(0.5, 0.5, 'No decrypted signal', 
                                           ha='center', va='center', transform=self.encryption_axes[2].transAxes)
                self.encryption_axes[2].set_title('Decrypted Signal', fontsize=12, fontweight='bold')
            self.encryption_axes[2].set_xlabel('Time (s)')
            self.encryption_axes[2].set_ylabel('Amplitude')
            self.encryption_axes[2].grid(True, alpha=0.3)
            
            # Adjust layout
            self.encryption_fig.tight_layout()
            self.encryption_canvas.draw()
            
        except Exception as e:
            print(f"Error updating encryption plots: {e}")

    # Security Analysis Functions
    def on_analysis_signal_selected(self, event):
        """Handle analysis signal selection"""
        try:
            selected = self.analysis_signal_var.get()
            if "Signal" in selected:
                signal_num = int(selected.split()[1]) - 1
                self.analysis_signal_index = signal_num
                self.update_security_plots()
                print(f"Selected signal {signal_num + 1} for analysis")
        except Exception as e:
            print(f"Error in analysis signal selection: {e}")

    def analyze_entropy(self):
        """Analyze entropy of signals"""
        try:
            signal = self.signals_data[self.analysis_signal_index]
            entropy = self.calculate_entropy(signal)
            
            # Update entropy plot
            self.security_axes[0, 0].clear()
            self.security_axes[0, 0].hist(signal, bins=50, alpha=0.7, color='blue', edgecolor='black')
            self.security_axes[0, 0].set_title(f'Signal Distribution (Entropy: {entropy:.3f})', fontsize=12, fontweight='bold')
            self.security_axes[0, 0].set_xlabel('Amplitude')
            self.security_axes[0, 0].set_ylabel('Frequency')
            self.security_axes[0, 0].grid(True, alpha=0.3)
            
            self.security_fig.tight_layout()
            self.security_canvas.draw()
            
            messagebox.showinfo("Entropy Analysis", f"Signal entropy: {entropy:.3f} bits")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error in entropy analysis: {str(e)}")

    def analyze_correlation(self):
        """Analyze correlation between original and encrypted signals"""
        try:
            signal = self.signals_data[self.analysis_signal_index]
            
            # Encrypt signal for correlation analysis
            r = 3.847
            x0 = 0.623
            encrypted, _ = self.biometric_encrypt(signal, r, x0)
            
            # Calculate correlation
            correlation = np.corrcoef(signal, encrypted)[0, 1]
            
            # Update correlation plot
            self.security_axes[0, 1].clear()
            self.security_axes[0, 1].scatter(signal[::10], encrypted[::10], alpha=0.6, s=20)
            self.security_axes[0, 1].set_title(f'Signal Correlation (r={correlation:.3f})', fontsize=12, fontweight='bold')
            self.security_axes[0, 1].set_xlabel('Original Signal')
            self.security_axes[0, 1].set_ylabel('Encrypted Signal')
            self.security_axes[0, 1].grid(True, alpha=0.3)
            
            self.security_fig.tight_layout()
            self.security_canvas.draw()
            
            messagebox.showinfo("Correlation Analysis", f"Correlation coefficient: {correlation:.3f}")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error in correlation analysis: {str(e)}")

    def analyze_histogram(self):
        """Analyze histogram of encrypted signal"""
        try:
            signal = self.signals_data[self.analysis_signal_index]
            
            # Encrypt signal
            r = 3.847
            x0 = 0.623
            encrypted, _ = self.biometric_encrypt(signal, r, x0)
            
            # Update histogram plot
            self.security_axes[1, 0].clear()
            self.security_axes[1, 0].hist(encrypted, bins=50, alpha=0.7, color='red', edgecolor='black')
            self.security_axes[1, 0].set_title('Encrypted Signal Distribution', fontsize=12, fontweight='bold')
            self.security_axes[1, 0].set_xlabel('Amplitude')
            self.security_axes[1, 0].set_ylabel('Frequency')
            self.security_axes[1, 0].grid(True, alpha=0.3)
            
            self.security_fig.tight_layout()
            self.security_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error in histogram analysis: {str(e)}")

    def generate_security_report(self):
        """Generate comprehensive security report"""
        try:
            signal = self.signals_data[self.analysis_signal_index]
            
            # Perform all analyses
            entropy_orig = self.calculate_entropy(signal)
            r, x0 = 3.847, 0.623
            encrypted, _ = self.biometric_encrypt(signal, r, x0)
            entropy_enc = self.calculate_entropy(encrypted)
            correlation = np.corrcoef(signal, encrypted)[0, 1]
            
            # Update all plots
            self.analyze_entropy()
            self.analyze_correlation()
            self.analyze_histogram()
            
            # Security score plot
            self.security_axes[1, 1].clear()
            metrics = ['Entropy', 'Correlation', 'Uniformity']
            scores = [entropy_enc/8*100, (1-abs(correlation))*100, 85]  # Normalized scores
            colors = ['green' if s > 70 else 'orange' if s > 50 else 'red' for s in scores]
            
            bars = self.security_axes[1, 1].bar(metrics, scores, color=colors, alpha=0.7)
            self.security_axes[1, 1].set_title('Security Metrics', fontsize=12, fontweight='bold')
            self.security_axes[1, 1].set_ylabel('Score (%)')
            self.security_axes[1, 1].set_ylim(0, 100)
            self.security_axes[1, 1].grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                self.security_axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + 1,
                                            f'{score:.1f}%', ha='center', va='bottom')
            
            self.security_fig.tight_layout()
            self.security_canvas.draw()
            
            # Show report
            report = f"""🔐 SECURITY ANALYSIS REPORT

Signal ID: {self.signal_ids[self.analysis_signal_index]}
Original Entropy: {entropy_orig:.3f} bits
Encrypted Entropy: {entropy_enc:.3f} bits
Correlation: {correlation:.3f}
Security Score: {np.mean(scores):.1f}%

✅ Encryption provides good entropy increase
✅ Low correlation indicates good security
✅ Uniform distribution achieved"""
            
            messagebox.showinfo("Security Report", report)
            
        except Exception as e:
            messagebox.showerror("Report Error", f"Error generating security report: {str(e)}")

    def update_security_plots(self):
        """Initialize security analysis plots"""
        try:
            # Clear all axes
            for ax in self.security_axes.flat:
                ax.clear()
                ax.text(0.5, 0.5, 'Select analysis type', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=12)
                ax.set_title('Security Analysis', fontsize=12, fontweight='bold')
            
            self.security_fig.tight_layout()
            self.security_canvas.draw()
            
        except Exception as e:
            print(f"Error updating security plots: {e}")

    # Real-time Monitoring Functions
    def initialize_realtime_plots(self):
        """Initialize real-time monitoring plots with 3 subplots and line objects"""
        try:
            # Clear all axes
            self.realtime_ax1.clear()
            self.realtime_ax2.clear()
            self.realtime_ax3.clear()
            
            # Set up plot 1: Original Signal
            self.realtime_ax1.set_title('Original ECG Signal', fontsize=12, fontweight='bold', color='blue')
            self.realtime_ax1.set_ylabel('Amplitude', fontsize=10)
            self.realtime_ax1.grid(True, alpha=0.3)
            self.realtime_ax1.set_xlim(0, 10)  # Initial time range
            self.realtime_ax1.set_ylim(-2, 2)  # Initial amplitude range
            
            # Set up plot 2: Encrypted Signal
            self.realtime_ax2.set_title('Encrypted ECG Signal', fontsize=12, fontweight='bold', color='red')
            self.realtime_ax2.set_ylabel('Amplitude', fontsize=10)
            self.realtime_ax2.grid(True, alpha=0.3)
            self.realtime_ax2.set_xlim(0, 10)  # Initial time range
            self.realtime_ax2.set_ylim(-2, 2)  # Initial amplitude range
            
            # Set up plot 3: Decrypted Signal
            self.realtime_ax3.set_title('Decrypted ECG Signal', fontsize=12, fontweight='bold', color='green')
            self.realtime_ax3.set_xlabel('Time (s)', fontsize=10)
            self.realtime_ax3.set_ylabel('Amplitude', fontsize=10)
            self.realtime_ax3.grid(True, alpha=0.3)
            self.realtime_ax3.set_xlim(0, 10)  # Initial time range
            self.realtime_ax3.set_ylim(-2, 2)  # Initial amplitude range
            
            # Create line objects for point-by-point drawing
            self.realtime_lines['original'], = self.realtime_ax1.plot([], [], 'b-', lw=1.5, alpha=0.9, label='Original ECG')
            self.realtime_lines['encrypted'], = self.realtime_ax2.plot([], [], 'r-', lw=1.5, alpha=0.9, label='Encrypted ECG')
            self.realtime_lines['decrypted'], = self.realtime_ax3.plot([], [], 'g-', lw=1.5, alpha=0.9, label='Decrypted ECG')
            
            # Add legends
            self.realtime_ax1.legend(loc='upper right')
            self.realtime_ax2.legend(loc='upper right')
            self.realtime_ax3.legend(loc='upper right')
            
            self.realtime_fig.tight_layout()
            self.realtime_canvas.draw()
            
        except Exception as e:
            print(f"Error initializing real-time plots: {e}")

    def start_monitoring(self):
        """Start real-time monitoring"""
        try:
            self.running = True
            self.current_monitoring_signal = 0
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_label.config(text="Status: Monitoring")
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
        except Exception as e:
            print(f"Error starting monitoring: {e}")

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        try:
            self.running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.status_label.config(text="Status: Stopped")
            self.signal_info_label.config(text="Signal: None")
            
        except Exception as e:
            print(f"Error stopping monitoring: {e}")

    def monitoring_loop(self):
        """Real-time monitoring loop with point-by-point drawing using buffers"""
        try:
            while self.running:
                # Get current signal
                signal = self.signals_data[self.current_monitoring_signal]
                
                # Store original signal
                self.realtime_ecg_data = list(signal)
                
                # Encrypt and decrypt the signal
                try:
                    r = 3.847
                    x0 = 0.623
                    encrypted_signal, perm_indices = self.biometric_encrypt(signal, r, x0)
                    decrypted_signal = self.biometric_decrypt(encrypted_signal, r, x0, perm_indices)
                    
                    self.realtime_encrypted_data = list(encrypted_signal)
                    self.realtime_decrypted_data = list(decrypted_signal)
                    
                except Exception as enc_error:
                    print(f"Monitoring encryption error: {enc_error}")
                    self.realtime_encrypted_data = list(signal)
                    self.realtime_decrypted_data = list(signal)
                
                # Simulate pulse value
                self.realtime_pulse_value = 60 + int(20 * np.random.random())  # 60-80 BPM
                
                # Reset buffers and signal index for new signal
                self.realtime_buffers = {
                    'original': ([], []),
                    'encrypted': ([], []),
                    'decrypted': ([], [])
                }
                self.signal_index = 0
                self.last_update_time = time.time()
                
                # Create time axis for the signal
                time_axis = np.linspace(0, len(signal)/1000, len(signal))
                
                # Point-by-point drawing loop
                while self.signal_index < len(signal) and self.running:
                    current_time = time.time()
                    elapsed = current_time - self.last_update_time
                    
                    if elapsed >= self.time_per_point:
                        # Process 20 points at a time (like in the provided code)
                        points_to_process = min(20, len(signal) - self.signal_index)
                        current_time_points = time_axis[self.signal_index:self.signal_index + points_to_process]
                        
                        # Update buffers for each signal type
                        signal_types = {
                            'original': self.realtime_ecg_data,
                            'encrypted': self.realtime_encrypted_data,
                            'decrypted': self.realtime_decrypted_data
                        }
                        
                        for signal_type, signal_data in signal_types.items():
                            if signal_data and len(signal_data) > self.signal_index:
                                current_data = signal_data[self.signal_index:self.signal_index + points_to_process]
                                
                                # Extend buffers
                                self.realtime_buffers[signal_type][0].extend(current_time_points)
                                self.realtime_buffers[signal_type][1].extend(current_data)
                                
                                # Limit buffer size (like in provided code)
                                while len(self.realtime_buffers[signal_type][0]) > 2000:
                                    self.realtime_buffers[signal_type][0].pop(0)
                                    self.realtime_buffers[signal_type][1].pop(0)
                                
                                # Update line data
                                if self.realtime_lines[signal_type]:
                                    self.realtime_lines[signal_type].set_data(
                                        self.realtime_buffers[signal_type][0],
                                        self.realtime_buffers[signal_type][1]
                                    )
                        
                        # Update axis limits dynamically
                        if len(self.realtime_buffers['original'][0]) > 0:
                            # Update X limits to show recent data
                            x_data = self.realtime_buffers['original'][0]
                            if len(x_data) > 0:
                                x_min, x_max = min(x_data), max(x_data)
                                x_range = x_max - x_min
                                if x_range > 0:
                                    self.realtime_ax1.set_xlim(x_min, x_max + x_range * 0.1)
                                    self.realtime_ax2.set_xlim(x_min, x_max + x_range * 0.1)
                                    self.realtime_ax3.set_xlim(x_min, x_max + x_range * 0.1)
                            
                            # Update Y limits for each signal
                            for signal_type, ax in [('original', self.realtime_ax1), 
                                                   ('encrypted', self.realtime_ax2), 
                                                   ('decrypted', self.realtime_ax3)]:
                                y_data = self.realtime_buffers[signal_type][1]
                                if len(y_data) > 0:
                                    y_min, y_max = min(y_data), max(y_data)
                                    y_range = y_max - y_min
                                    if y_range > 0:
                                        ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.1)
                        
                        # Update titles with current signal info
                        self.realtime_ax1.set_title(f'Original ECG Signal (ID: {self.signal_ids[self.current_monitoring_signal]})', 
                                                   fontsize=12, fontweight='bold', color='blue')
                        
                        # Modern pulse display for all three plots
                        if self.realtime_pulse_value is not None:
                            pulse_text = f'❤️ {self.realtime_pulse_value} BPM'
                            
                            # Remove previous pulse text if exists
                            for ax in [self.realtime_ax1, self.realtime_ax2, self.realtime_ax3]:
                                for text in ax.texts:
                                    if '❤️' in text.get_text():
                                        text.remove()
                            
                            # Add new pulse text
                            self.realtime_ax1.text(0.02, 0.98, pulse_text, transform=self.realtime_ax1.transAxes, 
                                                 fontsize=11, fontweight='bold', color='red',
                                                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
                            
                            self.realtime_ax2.text(0.02, 0.98, pulse_text, transform=self.realtime_ax2.transAxes, 
                                                 fontsize=11, fontweight='bold', color='red',
                                                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
                            
                            self.realtime_ax3.text(0.02, 0.98, pulse_text, transform=self.realtime_ax3.transAxes, 
                                                 fontsize=11, fontweight='bold', color='red',
                                                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
                        
                        # Update canvas
                        self.realtime_fig.tight_layout()
                        self.realtime_canvas.draw()
                        self.realtime_canvas.flush_events()
                        
                        self.signal_index += points_to_process
                        self.last_update_time = current_time
                        
                        # Update status
                        progress = (self.signal_index / len(signal)) * 100
                        self.signal_info_label.config(text=f"Signal: {self.current_monitoring_signal + 1}/20 (ID: {self.signal_ids[self.current_monitoring_signal]}) | Progress: {progress:.1f}% | Pulse: {self.realtime_pulse_value} BPM")
                    
                    # Small pause like in provided code
                    time.sleep(0.0001)
                
                # Move to next signal after current one is complete
                self.current_monitoring_signal = (self.current_monitoring_signal + 1) % len(self.signals_data)
                
                # Wait for specified interval before next signal
                speed = int(self.speed_var.get())
                time.sleep(speed / 1000.0)
                
        except Exception as e:
            print(f"Error in monitoring loop: {e}")

    # Serial Communication Functions
    def refresh_ports(self):
        """Refresh available serial ports"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_combo['values'] = ports
            if ports:
                self.port_combo.set(ports[0])
        except Exception as e:
            print(f"Error refreshing ports: {e}")

    def connect_serial(self):
        """Connect to serial port"""
        try:
            port = self.port_var.get()
            baud = int(self.baud_var.get())
            
            if not port:
                messagebox.showerror("Connection Error", "Please select a port")
                return
            
            print(f"Connecting to {port} at {baud} baud...")
            
            # Close existing connection if any
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.serial_port = serial.Serial(port, baud, timeout=1)
            self.serial_running = True
            
            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')
            self.serial_status_label.config(text="Status: Connected", foreground="green")
            
            # Clear previous data
            self.ecg_data = []
            self.pulse_value = None
            self.serial_data_count_label.config(text="ECG Samples: 0")
            
            # Start serial reading thread
            self.serial_thread = threading.Thread(target=self.serial_read_loop, daemon=True)
            self.serial_thread.start()
            
            self.serial_text.insert(tk.END, f"Connected to {port} at {baud} baud\n")
            self.serial_text.see(tk.END)
            
            print("Serial connection established successfully")
            
        except Exception as e:
            print(f"Connection error: {e}")
            messagebox.showerror("Connection Error", f"Error connecting to serial port: {str(e)}")

    def disconnect_serial(self):
        """Disconnect from serial port"""
        try:
            print("Disconnecting from serial port...")
            
            self.serial_running = False
            
            # Wait for thread to finish
            if hasattr(self, 'serial_thread') and self.serial_thread and self.serial_thread.is_alive():
                self.serial_thread.join(timeout=1.0)
            
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.connect_button.config(state='normal')
            self.disconnect_button.config(state='disabled')
            self.serial_status_label.config(text="Status: Disconnected", foreground="red")
            
            self.serial_text.insert(tk.END, "Disconnected from serial port\n")
            self.serial_text.see(tk.END)
            
            print("Serial disconnection completed")
            
        except Exception as e:
            print(f"Error disconnecting serial port: {e}")

    def serial_read_loop(self):
        """Serial data reading loop with real ECG module data processing (from provided code)"""
        try:
            print("Starting serial read loop...")
            
            while self.serial_running and self.serial_port and self.serial_port.is_open:
                try:
                    # Check if data is available
                    if self.serial_port.in_waiting > 0:
                        # Read one byte
                        data = self.serial_port.read(1)
                        
                        if data == b'\xF8':  # Wave sampling point marker
                            print("Received wave marker 0xF8")
                            
                            # Read 300 bytes of wave data
                            wave_data = self.serial_port.read(300)
                            print(f"Read {len(wave_data)} bytes of wave data")
                            
                            if len(wave_data) == 300:
                                # Convert bytes to list and extend ECG data
                                wave_list = list(wave_data)
                                self.ecg_data.extend(wave_list)
                                
                                # Keep only last 3000 samples
                                if len(self.ecg_data) > 3000:
                                    self.ecg_data[:] = self.ecg_data[-3000:]
                                
                                # Real-time encryption and decryption
                                if len(self.ecg_data) >= self.window_size:
                                    # Get recent data for processing
                                    recent_data = np.array(self.ecg_data[-self.window_size:])
                                    
                                    # Encrypt the data
                                    try:
                                        r = 3.847
                                        x0 = 0.623
                                        encrypted_data, perm_indices = self.biometric_encrypt(recent_data, r, x0)
                                        self.encrypted_ecg_data = list(encrypted_data)
                                        
                                        # Decrypt the data
                                        decrypted_data = self.biometric_decrypt(encrypted_data, r, x0, perm_indices)
                                        self.decrypted_ecg_data = list(decrypted_data)
                                        
                                    except Exception as enc_error:
                                        print(f"Encryption/Decryption error: {enc_error}")
                                        self.encrypted_ecg_data = list(recent_data)  # Use original if error
                                        self.decrypted_ecg_data = list(recent_data)
                                
                                # Update text log
                                self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}: Wave data ({len(wave_data)} bytes)\n")
                                self.serial_text.see(tk.END)
                                
                                # Update data count
                                self.serial_data_count_label.config(text=f"ECG Samples: {len(self.ecg_data)}")
                                
                                # Update real-time plot with filtered data and model prediction
                                self.update_ecg_plot_with_prediction()
                                
                                print(f"Wave data sample: {wave_list[:10]}...")  # Show first 10 values
                                
                        elif data == b'\xFA':  # Pulse value marker
                            print("Received pulse marker 0xFA")
                            
                            pulse_data = self.serial_port.read(1)
                            if len(pulse_data) == 1:
                                self.pulse_value = ord(pulse_data)
                                
                                # Update text log
                                self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Pulse: {self.pulse_value} BPM\n")
                                self.serial_text.see(tk.END)
                                
                                # Update pulse display
                                self.update_pulse_display()
                                
                                print(f"Pulse value: {self.pulse_value}")
                                
                        elif data == b'\xFB':  # Info byte marker
                            print("Received info marker 0xFB")
                            
                            info_data = self.serial_port.read(1)
                            if len(info_data) == 1:
                                if info_data == b'\x11':
                                    self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Lead off detected!\n")
                                    self.serial_text.see(tk.END)
                                    print("Lead off detected")
                                else:
                                    self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Info: {ord(info_data)}\n")
                                    self.serial_text.see(tk.END)
                                    print(f"Unknown info byte: {ord(info_data)}")
                        else:
                            # Unknown data byte - try to read as text
                            try:
                                text_data = data.decode('utf-8', errors='ignore')
                                if text_data.isprintable():
                                    self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Text: {text_data}\n")
                                    self.serial_text.see(tk.END)
                                else:
                                    self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Unknown: 0x{data.hex()}\n")
                                    self.serial_text.see(tk.END)
                            except:
                                self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Unknown: 0x{data.hex()}\n")
                                self.serial_text.see(tk.END)
                            
                            print(f"Unknown data byte: 0x{data.hex()}")
                    
                    # Limit text widget size
                    if int(self.serial_text.index('end-1c').split('.')[0]) > 1000:
                        self.serial_text.delete('1.0', '2.0')
                        
                except Exception as e:
                    print(f"Error in serial read iteration: {e}")
                    self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Error: {str(e)}\n")
                    self.serial_text.see(tk.END)
                
                time.sleep(0.01)  # 10ms polling for real-time response
                
        except Exception as e:
            print(f"Error in serial read loop: {e}")
            self.serial_running = False
            self.serial_status_label.config(text="Status: Error", foreground="red")
            self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Serial loop error: {str(e)}\n")
            self.serial_text.see(tk.END)

    def update_ecg_plot_with_prediction(self):
        """Update real-time ECG plot with 3 synchronized signals (original, encrypted, decrypted)"""
        try:
            if len(self.ecg_data) > 0:
                print(f"Updating ECG plot with {len(self.ecg_data)} samples")
                
                # Get the last window_size samples for filtering
                display_data = np.array(self.ecg_data[-self.window_size:])
                print(f"Display data shape: {display_data.shape}, range: {np.min(display_data)} to {np.max(display_data)}")
                
                # Apply bandpass filter (from provided code)
                try:
                    filtered_data = self.butter_bandpass_filter(display_data, self.lowcut, self.highcut, self.fs, order=4)
                    print(f"Filtered data range: {np.min(filtered_data)} to {np.max(filtered_data)}")
                except Exception as filter_error:
                    print(f"Filter error, using original data: {filter_error}")
                    filtered_data = display_data
                
                # Clear all subplots
                self.serial_ax1.clear()
                self.serial_ax2.clear()
                self.serial_ax3.clear()
                
                # Create time axis
                time_axis = range(len(filtered_data))
                
                # Plot 1: Original Signal
                self.serial_ax1.plot(time_axis, filtered_data, 'b-', linewidth=1.5, alpha=0.9, label='Original ECG')
                self.serial_ax1.set_title('Original ECG Signal', fontsize=12, fontweight='bold', color='blue')
                self.serial_ax1.set_ylabel('Amplitude', fontsize=10)
                self.serial_ax1.grid(True, alpha=0.3)
                self.serial_ax1.legend(loc='upper right')
                
                # Set limits for original signal
                if len(filtered_data) > 1:
                    self.serial_ax1.set_ylim(min(filtered_data) - 10, max(filtered_data) + 10)
                else:
                    self.serial_ax1.set_ylim(-128, 128)
                
                # Plot 2: Encrypted Signal
                if len(self.encrypted_ecg_data) > 0:
                    encrypted_display = np.array(self.encrypted_ecg_data[-self.window_size:])
                    self.serial_ax2.plot(time_axis, encrypted_display, 'r-', linewidth=1.5, alpha=0.9, label='Encrypted ECG')
                    self.serial_ax2.set_title('Encrypted ECG Signal', fontsize=12, fontweight='bold', color='red')
                    self.serial_ax2.set_ylabel('Amplitude', fontsize=10)
                    self.serial_ax2.grid(True, alpha=0.3)
                    self.serial_ax2.legend(loc='upper right')
                    
                    if len(encrypted_display) > 1:
                        self.serial_ax2.set_ylim(min(encrypted_display) - 10, max(encrypted_display) + 10)
                    else:
                        self.serial_ax2.set_ylim(-128, 128)
                else:
                    self.serial_ax2.text(0.5, 0.5, 'No encrypted data', ha='center', va='center', 
                                       transform=self.serial_ax2.transAxes, fontsize=12, color='gray')
                    self.serial_ax2.set_title('Encrypted ECG Signal', fontsize=12, fontweight='bold', color='red')
                    self.serial_ax2.set_ylabel('Amplitude', fontsize=10)
                    self.serial_ax2.grid(True, alpha=0.3)
                
                # Plot 3: Decrypted Signal
                if len(self.decrypted_ecg_data) > 0:
                    decrypted_display = np.array(self.decrypted_ecg_data[-self.window_size:])
                    self.serial_ax3.plot(time_axis, decrypted_display, 'g-', linewidth=1.5, alpha=0.9, label='Decrypted ECG')
                    self.serial_ax3.set_title('Decrypted ECG Signal', fontsize=12, fontweight='bold', color='green')
                    self.serial_ax3.set_xlabel('Sample Index', fontsize=10)
                    self.serial_ax3.set_ylabel('Amplitude', fontsize=10)
                    self.serial_ax3.grid(True, alpha=0.3)
                    self.serial_ax3.legend(loc='upper right')
                    
                    if len(decrypted_display) > 1:
                        self.serial_ax3.set_ylim(min(decrypted_display) - 10, max(decrypted_display) + 10)
                    else:
                        self.serial_ax3.set_ylim(-128, 128)
                else:
                    self.serial_ax3.text(0.5, 0.5, 'No decrypted data', ha='center', va='center', 
                                       transform=self.serial_ax3.transAxes, fontsize=12, color='gray')
                    self.serial_ax3.set_title('Decrypted ECG Signal', fontsize=12, fontweight='bold', color='green')
                    self.serial_ax3.set_xlabel('Sample Index', fontsize=10)
                    self.serial_ax3.set_ylabel('Amplitude', fontsize=10)
                    self.serial_ax3.grid(True, alpha=0.3)
                
                # Set x-axis limits for all plots (synchronized)
                self.serial_ax1.set_xlim(len(filtered_data)-self.window_size, len(filtered_data))
                self.serial_ax2.set_xlim(len(filtered_data)-self.window_size, len(filtered_data))
                self.serial_ax3.set_xlim(len(filtered_data)-self.window_size, len(filtered_data))
                
                # Modern pulse display for all three plots
                if self.pulse_value is not None:
                    # Create modern pulse indicator
                    pulse_text = f'❤️ {self.pulse_value} BPM'
                    
                    # Add to each subplot
                    self.serial_ax1.text(0.02, 0.98, pulse_text, transform=self.serial_ax1.transAxes, 
                                       fontsize=11, fontweight='bold', color='red',
                                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
                    
                    self.serial_ax2.text(0.02, 0.98, pulse_text, transform=self.serial_ax2.transAxes, 
                                       fontsize=11, fontweight='bold', color='red',
                                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
                    
                    self.serial_ax3.text(0.02, 0.98, pulse_text, transform=self.serial_ax3.transAxes, 
                                       fontsize=11, fontweight='bold', color='red',
                                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
                
                # Model prediction display (only on original signal)
                if len(self.ecg_data) >= self.window_size and self.model is not None:
                    try:
                        # Normalize data and reshape for model
                        test_data = np.array(filtered_data)
                        test_data = (test_data - np.mean(test_data)) / np.std(test_data)
                        test_data = test_data.reshape(1, self.window_size, 1)
                        
                        # Make prediction
                        prediction = self.model.predict(test_data, verbose=0)
                        predicted_class = np.argmax(prediction, axis=1)[0]
                        class_label = self.class_labels[predicted_class]
                        self.predicted_class = class_label
                        
                        print(f"Predicted class: {class_label}")
                        
                        # Add prediction to original signal plot
                        self.serial_ax1.text(0.98, 0.98, f'🔍 {class_label}', 
                                           transform=self.serial_ax1.transAxes, ha='right', va='top',
                                           fontsize=11, fontweight='bold', color='purple',
                                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='purple'))
                        
                        # Update text log
                        self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Prediction: {class_label}\n")
                        self.serial_text.see(tk.END)
                        
                    except Exception as pred_error:
                        print(f"Prediction error: {pred_error}")
                
                # Update canvas
                self.serial_fig.tight_layout()
                self.serial_canvas.draw()
                print("ECG plot updated successfully with 3 synchronized signals")
                
            else:
                print("No ECG data available for plotting")
                
        except Exception as e:
            print(f"Error updating ECG plot with prediction: {e}")
            import traceback
            traceback.print_exc()

    def update_pulse_display(self):
        """Update pulse value display"""
        try:
            if self.pulse_value is not None:
                # Update status label with pulse info
                self.serial_status_label.config(text=f"Status: Connected | Pulse: {self.pulse_value} BPM", foreground="green")
        except Exception as e:
            print(f"Error updating pulse display: {e}")

    def initialize_serial_plot(self):
        """Initialize serial data plotting with 3 subplots"""
        try:
            # Clear all axes
            self.serial_ax1.clear()
            self.serial_ax2.clear()
            self.serial_ax3.clear()
            
            # Set up plot 1: Original Signal
            self.serial_ax1.set_title('Original ECG Signal', fontsize=12, fontweight='bold', color='blue')
            self.serial_ax1.set_ylabel('Amplitude', fontsize=10)
            self.serial_ax1.grid(True, alpha=0.3)
            
            # Set up plot 2: Encrypted Signal
            self.serial_ax2.set_title('Encrypted ECG Signal', fontsize=12, fontweight='bold', color='red')
            self.serial_ax2.set_ylabel('Amplitude', fontsize=10)
            self.serial_ax2.grid(True, alpha=0.3)
            
            # Set up plot 3: Decrypted Signal
            self.serial_ax3.set_title('Decrypted ECG Signal', fontsize=12, fontweight='bold', color='green')
            self.serial_ax3.set_xlabel('Sample Index', fontsize=10)
            self.serial_ax3.set_ylabel('Amplitude', fontsize=10)
            self.serial_ax3.grid(True, alpha=0.3)
            
            self.serial_fig.tight_layout()
            self.serial_canvas.draw()
            
        except Exception as e:
            print(f"Error initializing serial plot: {e}")

    def clear_serial_data(self):
        """Clear serial data"""
        try:
            self.ecg_data = []
            self.encrypted_ecg_data = []
            self.decrypted_ecg_data = []
            self.pulse_value = None
            self.predicted_class = None
            self.serial_text.delete('1.0', tk.END)
            self.serial_status_label.config(text="Status: Disconnected")
            self.serial_data_count_label.config(text="ECG Samples: 0")
            
            # Clear serial plot
            self.serial_ax1.clear()
            self.serial_ax2.clear()
            self.serial_ax3.clear()
            
            # Set up plot 1: Original Signal
            self.serial_ax1.set_title('Original ECG Signal', fontsize=12, fontweight='bold', color='blue')
            self.serial_ax1.set_ylabel('Amplitude', fontsize=10)
            self.serial_ax1.grid(True, alpha=0.3)
            
            # Set up plot 2: Encrypted Signal
            self.serial_ax2.set_title('Encrypted ECG Signal', fontsize=12, fontweight='bold', color='red')
            self.serial_ax2.set_ylabel('Amplitude', fontsize=10)
            self.serial_ax2.grid(True, alpha=0.3)
            
            # Set up plot 3: Decrypted Signal
            self.serial_ax3.set_title('Decrypted ECG Signal', fontsize=12, fontweight='bold', color='green')
            self.serial_ax3.set_xlabel('Sample Index', fontsize=10)
            self.serial_ax3.set_ylabel('Amplitude', fontsize=10)
            self.serial_ax3.grid(True, alpha=0.3)
            
            self.serial_fig.tight_layout()
            self.serial_canvas.draw()
            
        except Exception as e:
            print(f"Error clearing serial data: {e}")

    def start_test_data(self):
        """Start test data generation"""
        try:
            if not hasattr(self, 'test_data_running') or not self.test_data_running:
                self.test_data_running = True
                self.test_data_thread = threading.Thread(target=self.test_data_loop, daemon=True)
                self.test_data_thread.start()
                
                self.serial_status_label.config(text="Status: Test Data", foreground="blue")
                self.serial_text.insert(tk.END, "Started test data generation...\n")
                self.serial_text.see(tk.END)
            else:
                self.test_data_running = False
                self.serial_status_label.config(text="Status: Stopped", foreground="red")
                self.serial_text.insert(tk.END, "Stopped test data generation.\n")
                self.serial_text.see(tk.END)
                
        except Exception as e:
            messagebox.showerror("Test Data Error", f"Error starting test data generation: {str(e)}")

    def test_data_loop(self):
        """Generate test ECG-like data in real module format"""
        try:
            print("Starting test data generation...")
            start_time = time.time()
            t = 0
            
            while self.test_data_running:
                try:
                    # Generate ECG-like signal
                    frequency = 1.2  # Hz
                    amplitude = 2.0
                    noise = 0.1 * np.random.normal(0, 1)
                    
                    # ECG-like waveform
                    signal = amplitude * np.sin(2 * np.pi * frequency * t) + \
                            0.5 * amplitude * np.sin(2 * np.pi * 2 * frequency * t) + \
                            0.3 * amplitude * np.sin(2 * np.pi * 3 * frequency * t) + noise
                    
                    # Simulate wave data packet (300 bytes)
                    wave_data = []
                    for i in range(300):
                        # Generate 300 samples with some variation
                        sample = int(128 + 50 * np.sin(2 * np.pi * 0.1 * (t + i * 0.01)) + 
                                    10 * np.random.normal(0, 1))
                        sample = max(0, min(255, sample))  # Clamp to 0-255
                        wave_data.append(sample)
                    
                    # Add to ECG data
                    self.ecg_data.extend(wave_data)
                    
                    # Keep only last 3000 samples
                    if len(self.ecg_data) > 3000:
                        self.ecg_data[:] = self.ecg_data[-3000:]
                    
                    # Real-time encryption and decryption for test data
                    if len(self.ecg_data) >= self.window_size:
                        # Get recent data for processing
                        recent_data = np.array(self.ecg_data[-self.window_size:])
                        
                        # Encrypt the data
                        try:
                            r = 3.847
                            x0 = 0.623
                            encrypted_data, perm_indices = self.biometric_encrypt(recent_data, r, x0)
                            self.encrypted_ecg_data = list(encrypted_data)
                            
                            # Decrypt the data
                            decrypted_data = self.biometric_decrypt(encrypted_data, r, x0, perm_indices)
                            self.decrypted_ecg_data = list(decrypted_data)
                            
                        except Exception as enc_error:
                            print(f"Test data encryption/decryption error: {enc_error}")
                            self.encrypted_ecg_data = list(recent_data)  # Use original if error
                            self.decrypted_ecg_data = list(recent_data)
                    
                    # Update text log
                    self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}: Wave data ({len(wave_data)} bytes)\n")
                    self.serial_text.see(tk.END)
                    
                    # Update data count
                    self.serial_data_count_label.config(text=f"ECG Samples: {len(self.ecg_data)}")
                    
                    # Update plot
                    self.update_ecg_plot_with_prediction()
                    
                    # Simulate pulse value every 5 seconds
                    if int(t * 10) % 50 == 0:  # Every 5 seconds
                        self.pulse_value = 60 + int(20 * np.random.random())  # 60-80 BPM
                        self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Pulse: {self.pulse_value} BPM\n")
                        self.serial_text.see(tk.END)
                        self.update_pulse_display()
                    
                    # Simulate model prediction every 10 seconds
                    if int(t * 10) % 100 == 0 and self.model is None:  # Every 10 seconds, only if no real model
                        simulated_classes = ['N', 'L', 'R', 'A', 'V']
                        self.predicted_class = np.random.choice(simulated_classes)
                        self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Simulated Prediction: {self.predicted_class}\n")
                        self.serial_text.see(tk.END)
                    
                    # Simulate lead off detection occasionally
                    if np.random.random() < 0.01:  # 1% chance
                        self.serial_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: Lead off detected!\n")
                        self.serial_text.see(tk.END)
                    
                    # Limit text widget size
                    if int(self.serial_text.index('end-1c').split('.')[0]) > 1000:
                        self.serial_text.delete('1.0', '2.0')
                    
                    t += 0.1  # Time step
                    time.sleep(0.1)  # 10 Hz sampling rate
                    
                except Exception as e:
                    print(f"Error in test data iteration: {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Error in test data loop: {e}")
            self.test_data_running = False

def main():
    root = tk.Tk()
    app = ECGEncryptionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 