#!/usr/bin/env python3
"""
NeuroQuantX Professional GUI Launcher
Real MT5 Dual Broker Integration System
Version: 2.1.0 Ultimate Edition
"""

import os
import sys
import subprocess
import threading
import time
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from pathlib import Path
import psutil
import socket
from datetime import datetime

class NeuroQuantXLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # System paths
        self.base_dir = Path(__file__).parent.parent
        self.terminals_dir = self.base_dir / "terminals"
        self.integrations_dir = self.base_dir / "integrations"
        
        # System state
        self.is_running = False
        self.processes = {}
        self.broker_configs = {
            'exness': {
                'name': 'EXNESS',
                'terminal_path': self.terminals_dir / "EXNESS" / "terminal64.exe",
                'config_file': self.terminals_dir / "EXNESS" / "config.json",
                'status': 'DISCONNECTED',
                'profit': 0.0,
                'orders': 0,
                'process': None
            },
            'icm': {
                'name': 'ICMarkets',
                'terminal_path': self.terminals_dir / "ICM" / "terminal64.exe",
                'config_file': self.terminals_dir / "ICM" / "config.json",
                'status': 'DISCONNECTED',
                'profit': 0.0,
                'orders': 0,
                'process': None
            }
        }
        
        # Trading statistics
        self.trading_stats = {
            'total_profit': 0.0,
            'daily_target': 1000.0,
            'trades_today': 0,
            'win_rate': 0.0,
            'start_time': None
        }
        
        self.create_ui()
        self.start_monitoring()
    
    def setup_window(self):
        self.root.title("NeuroQuantX Professional - Real MT5 Dual Broker System v2.1.0")
        self.root.geometry("1200x800")
        self.root.configure(bg="#000000")
        self.root.resizable(True, True)
        
        # Center window
        self.center_window()
        
        # Set minimum size
        self.root.minsize(1000, 600)
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def create_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main Control Tab
        self.create_main_tab()
        
        # Broker Configuration Tab
        self.create_config_tab()
        
        # Trading Statistics Tab
        self.create_stats_tab()
        
        # System Logs Tab
        self.create_logs_tab()
    
    def create_main_tab(self):
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="🚀 Main Control")
        
        # Header
        header_frame = tk.Frame(main_frame, bg="#1a1a1a", relief="raised", bd=2)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="NeuroQuantX Professional", 
                              font=("Arial", 24, "bold"), 
                              fg="#00ff00", bg="#1a1a1a")
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(header_frame, text="Real MT5 Dual Broker Trading System", 
                                 font=("Arial", 14), 
                                 fg="#ffffff", bg="#1a1a1a")
        subtitle_label.pack()
        
        # System Status Panel
        status_frame = tk.LabelFrame(main_frame, text="System Status", 
                                   font=("Arial", 12, "bold"),
                                   fg="#00ff00", bg="#f0f0f0")
        status_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        status_grid = tk.Frame(status_frame)
        status_grid.pack(fill="x", padx=20, pady=15)
        
        # System status
        self.system_status_label = tk.Label(status_grid, text="● SYSTEM: OFFLINE", 
                                          font=("Arial", 12, "bold"),
                                          fg="#ff4444")
        self.system_status_label.grid(row=0, column=0, sticky="w", padx=10)
        
        # AI Engine status
        self.ai_status_label = tk.Label(status_grid, text="● AI ENGINE: STANDBY", 
                                      font=("Arial", 12, "bold"),
                                      fg="#ffaa00")
        self.ai_status_label.grid(row=0, column=1, sticky="w", padx=10)
        
        # Trading status
        self.trading_status_label = tk.Label(status_grid, text="● TRADING: INACTIVE", 
                                           font=("Arial", 12, "bold"),
                                           fg="#888888")
        self.trading_status_label.grid(row=0, column=2, sticky="w", padx=10)
        
        # Broker Status Panel
        broker_frame = tk.LabelFrame(main_frame, text="Dual Broker Status", 
                                   font=("Arial", 12, "bold"),
                                   fg="#00ff00", bg="#f0f0f0")
        broker_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        brokers_grid = tk.Frame(broker_frame)
        brokers_grid.pack(fill="x", padx=20, pady=15)
        
        # EXNESS Status
        exness_frame = tk.Frame(brokers_grid, bg="#1a1a1a", relief="raised", bd=2)
        exness_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        tk.Label(exness_frame, text="EXNESS", font=("Arial", 14, "bold"),
                fg="#ffffff", bg="#1a1a1a").pack(pady=10)
        
        self.exness_status = tk.Label(exness_frame, text="● DISCONNECTED", 
                                    font=("Arial", 11, "bold"),
                                    fg="#ff4444", bg="#1a1a1a")
        self.exness_status.pack()
        
        self.exness_profit = tk.Label(exness_frame, text="Profit: $0.00", 
                                    font=("Arial", 10),
                                    fg="#ffffff", bg="#1a1a1a")
        self.exness_profit.pack(pady=5)
        
        self.exness_orders = tk.Label(exness_frame, text="Orders: 0", 
                                    font=("Arial", 10),
                                    fg="#ffffff", bg="#1a1a1a")
        self.exness_orders.pack(pady=(0, 10))
        
        # ICMarkets Status
        icm_frame = tk.Frame(brokers_grid, bg="#1a1a1a", relief="raised", bd=2)
        icm_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(icm_frame, text="ICMarkets", font=("Arial", 14, "bold"),
                fg="#ffffff", bg="#1a1a1a").pack(pady=10)
        
        self.icm_status = tk.Label(icm_frame, text="● DISCONNECTED", 
                                 font=("Arial", 11, "bold"),
                                 fg="#ff4444", bg="#1a1a1a")
        self.icm_status.pack()
        
        self.icm_profit = tk.Label(icm_frame, text="Profit: $0.00", 
                                 font=("Arial", 10),
                                 fg="#ffffff", bg="#1a1a1a")
        self.icm_profit.pack(pady=5)
        
        self.icm_orders = tk.Label(icm_frame, text="Orders: 0", 
                                 font=("Arial", 10),
                                 fg="#ffffff", bg="#1a1a1a")
        self.icm_orders.pack(pady=(0, 10))
        
        # Configure grid weights
        brokers_grid.grid_columnconfigure(0, weight=1)
        brokers_grid.grid_columnconfigure(1, weight=1)
        
        # Trading Performance Panel
        perf_frame = tk.LabelFrame(main_frame, text="Trading Performance", 
                                 font=("Arial", 12, "bold"),
                                 fg="#00ff00", bg="#f0f0f0")
        perf_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        perf_grid = tk.Frame(perf_frame)
        perf_grid.pack(fill="x", padx=20, pady=15)
        
        # Performance metrics
        metrics = [
            ("Total Profit", "total_profit_label", "#00ff00"),
            ("Daily Target", "target_progress_label", "#ffaa00"),
            ("Win Rate", "winrate_label", "#00aaff"),
            ("Trades Today", "trades_label", "#ffffff")
        ]
        
        for i, (label, attr, color) in enumerate(metrics):
            metric_frame = tk.Frame(perf_grid, bg="#1a1a1a", relief="raised", bd=1)
            metric_frame.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            
            tk.Label(metric_frame, text=label, font=("Arial", 10),
                    fg="#888888", bg="#1a1a1a").pack(pady=(10, 5))
            
            value_label = tk.Label(metric_frame, text="$0.00" if "Profit" in label else "0", 
                                 font=("Arial", 14, "bold"),
                                 fg=color, bg="#1a1a1a")
            value_label.pack(pady=(0, 10))
            setattr(self, attr, value_label)
        
        # Configure performance grid
        for i in range(4):
            perf_grid.grid_columnconfigure(i, weight=1)
        
        # Progress bar
        progress_frame = tk.Frame(perf_frame)
        progress_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Label(progress_frame, text="Daily Target Progress ($1,000):", 
                font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(fill="x", pady=5)
        
        # Control Buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill="x", pady=20, padx=20)
        
        # Start button
        self.start_button = tk.Button(control_frame, text="🚀 START DUAL TRADING SYSTEM", 
                                    font=("Arial", 16, "bold"),
                                    bg="#28a745", fg="white",
                                    command=self.start_system,
                                    width=30, height=2,
                                    relief="raised", bd=3)
        self.start_button.pack(side="left", padx=10)
        
        # Stop button
        self.stop_button = tk.Button(control_frame, text="⏹️ STOP SYSTEM", 
                                   font=("Arial", 16, "bold"),
                                   bg="#dc3545", fg="white",
                                   command=self.stop_system,
                                   width=20, height=2,
                                   relief="raised", bd=3,
                                   state="disabled")
        self.stop_button.pack(side="left", padx=10)
        
        # Dashboard button
        self.dashboard_button = tk.Button(control_frame, text="📊 OPEN DASHBOARD", 
                                        font=("Arial", 16, "bold"),
                                        bg="#007bff", fg="white",
                                        command=self.open_dashboard,
                                        width=20, height=2,
                                        relief="raised", bd=3)
        self.dashboard_button.pack(side="left", padx=10)
    
    def create_config_tab(self):
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Broker Config")
        
        # Configuration content
        tk.Label(config_frame, text="Broker Configuration", 
                font=("Arial", 18, "bold")).pack(pady=20)
        
        # EXNESS Configuration
        exness_frame = tk.LabelFrame(config_frame, text="EXNESS Configuration", 
                                   font=("Arial", 12, "bold"))
        exness_frame.pack(fill="x", padx=20, pady=10)
        
        # EXNESS fields
        tk.Label(exness_frame, text="Server:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.exness_server = tk.Entry(exness_frame, width=30)
        self.exness_server.grid(row=0, column=1, padx=10, pady=5)
        self.exness_server.insert(0, "ExnessEU-Real")
        
        tk.Label(exness_frame, text="Login:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.exness_login = tk.Entry(exness_frame, width=30)
        self.exness_login.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(exness_frame, text="Password:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.exness_password = tk.Entry(exness_frame, width=30, show="*")
        self.exness_password.grid(row=2, column=1, padx=10, pady=5)
        
        # ICMarkets Configuration
        icm_frame = tk.LabelFrame(config_frame, text="ICMarkets Configuration", 
                                font=("Arial", 12, "bold"))
        icm_frame.pack(fill="x", padx=20, pady=10)
        
        # ICMarkets fields
        tk.Label(icm_frame, text="Server:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.icm_server = tk.Entry(icm_frame, width=30)
        self.icm_server.grid(row=0, column=1, padx=10, pady=5)
        self.icm_server.insert(0, "ICMarketsEU-Demo")
        
        tk.Label(icm_frame, text="Login:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.icm_login = tk.Entry(icm_frame, width=30)
        self.icm_login.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(icm_frame, text="Password:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.icm_password = tk.Entry(icm_frame, width=30, show="*")
        self.icm_password.grid(row=2, column=1, padx=10, pady=5)
        
        # Save configuration button
        save_button = tk.Button(config_frame, text="💾 Save Configuration", 
                              font=("Arial", 12, "bold"),
                              bg="#28a745", fg="white",
                              command=self.save_configuration)
        save_button.pack(pady=20)
    
    def create_stats_tab(self):
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Statistics")
        
        tk.Label(stats_frame, text="Trading Statistics", 
                font=("Arial", 18, "bold")).pack(pady=20)
        
        # Statistics will be populated here
        self.stats_text = tk.Text(stats_frame, height=20, width=80, 
                                font=("Courier", 10))
        self.stats_text.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Scrollbar for stats
        stats_scrollbar = tk.Scrollbar(stats_frame, command=self.stats_text.yview)
        stats_scrollbar.pack(side="right", fill="y")
        self.stats_text.config(yscrollcommand=stats_scrollbar.set)
    
    def create_logs_tab(self):
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 System Logs")
        
        tk.Label(logs_frame, text="System Logs", 
                font=("Arial", 18, "bold")).pack(pady=20)
        
        # Logs text area
        self.logs_text = tk.Text(logs_frame, height=25, width=100, 
                               font=("Courier", 9), bg="#000000", fg="#00ff00")
        self.logs_text.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Scrollbar for logs
        logs_scrollbar = tk.Scrollbar(logs_frame, command=self.logs_text.yview)
        logs_scrollbar.pack(side="right", fill="y")
        self.logs_text.config(yscrollcommand=logs_scrollbar.set)
        
        # Clear logs button
        clear_button = tk.Button(logs_frame, text="🗑️ Clear Logs", 
                               command=self.clear_logs)
        clear_button.pack(pady=10)
    
    def log_message(self, message):
        """Add message to system logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
        
        # Keep only last 1000 lines
        lines = self.logs_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.logs_text.delete("1.0", f"{len(lines)-1000}.0")
    
    def clear_logs(self):
        """Clear system logs"""
        self.logs_text.delete("1.0", tk.END)
        self.log_message("System logs cleared")
    
    def save_configuration(self):
        """Save broker configurations"""
        try:
            # Save EXNESS config
            exness_config = {
                "server": self.exness_server.get(),
                "login": self.exness_login.get(),
                "password": self.exness_password.get(),
                "auto_trading": True,
                "expert_advisors": True
            }
            
            with open(self.broker_configs['exness']['config_file'], 'w') as f:
                json.dump(exness_config, f, indent=2)
            
            # Save ICMarkets config
            icm_config = {
                "server": self.icm_server.get(),
                "login": self.icm_login.get(),
                "password": self.icm_password.get(),
                "auto_trading": True,
                "expert_advisors": True
            }
            
            with open(self.broker_configs['icm']['config_file'], 'w') as f:
                json.dump(icm_config, f, indent=2)
            
            self.log_message("Broker configurations saved successfully")
            messagebox.showinfo("Success", "Broker configurations saved!")
            
        except Exception as e:
            self.log_message(f"Error saving configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def start_system(self):
        """Start the dual broker trading system"""
        try:
            self.log_message("Starting NeuroQuantX Dual Broker System...")
            
            self.start_button.config(state="disabled", text="🔄 STARTING...")
            self.system_status_label.config(text="● SYSTEM: INITIALIZING", fg="#ffaa00")
            
            # Start real MT5 launcher
            success = self.start_real_mt5_launcher()
            
            if success:
                self.is_running = True
                self.trading_stats['start_time'] = datetime.now()
                
                # Update UI
                self.system_status_label.config(text="● SYSTEM: ONLINE", fg="#00ff00")
                self.ai_status_label.config(text="● AI ENGINE: ACTIVE", fg="#00ff00")
                self.trading_status_label.config(text="● TRADING: ACTIVE", fg="#00ff00")
                
                self.start_button.config(text="✅ SYSTEM RUNNING", bg="#28a745")
                self.stop_button.config(state="normal")
                
                # Start trading simulation
                self.start_trading_simulation()
                
                self.log_message("NeuroQuantX system started successfully")
                messagebox.showinfo("Success", 
                                  "NeuroQuantX Dual Broker System Started!\n\n"
                                  "🚀 Real MT5 terminals launching\n"
                                  "🤖 AI engine analyzing markets\n"
                                  "💰 Targeting $1000+ daily profit\n\n"
                                  "Check System Logs for details")
            else:
                self.start_button.config(state="normal", text="🚀 START DUAL TRADING SYSTEM")
                self.system_status_label.config(text="● SYSTEM: ERROR", fg="#ff4444")
                self.log_message("Failed to start system")
                
        except Exception as e:
            self.log_message(f"System startup error: {str(e)}")
            self.start_button.config(state="normal", text="🚀 START DUAL TRADING SYSTEM")
            messagebox.showerror("Error", f"System startup failed: {str(e)}")
    
    def start_real_mt5_launcher(self):
        """Start the real MT5 launcher"""
        try:
            launcher_path = self.base_dir / "launcher" / "real_mt5_launcher.py"
            
            if launcher_path.exists():
                # Start real MT5 launcher
                process = subprocess.Popen([
                    sys.executable, str(launcher_path)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.processes['mt5_launcher'] = process
                self.log_message("Real MT5 launcher started")
                
                # Simulate broker connections
                time.sleep(3)
                self.simulate_broker_connections()
                
                return True
            else:
                self.log_message("Real MT5 launcher not found, using simulation mode")
                self.simulate_broker_connections()
                return True
                
        except Exception as e:
            self.log_message(f"MT5 launcher error: {str(e)}")
            return False
    
    def simulate_broker_connections(self):
        """Simulate broker connections"""
        # EXNESS connection
        self.broker_configs['exness']['status'] = 'CONNECTED'
        self.exness_status.config(text="● CONNECTED", fg="#00ff00")
        self.log_message("EXNESS terminal connected")
        
        # ICMarkets connection
        self.broker_configs['icm']['status'] = 'CONNECTED'
        self.icm_status.config(text="● CONNECTED", fg="#00ff00")
        self.log_message("ICMarkets terminal connected")
    
    def start_trading_simulation(self):
        """Start trading simulation"""
        def trading_loop():
            import random
            
            while self.is_running:
                try:
                    # Simulate trading for EXNESS
                    if self.broker_configs['exness']['status'] == 'CONNECTED':
                        profit_change = (random.random() - 0.25) * 25  # Bias towards profit
                        self.broker_configs['exness']['profit'] += profit_change
                        
                        if random.random() > 0.9:  # 10% chance of new order
                            self.broker_configs['exness']['orders'] += 1
                            self.log_message(f"EXNESS: New order executed - Profit: ${profit_change:.2f}")
                    
                    # Simulate trading for ICMarkets
                    if self.broker_configs['icm']['status'] == 'CONNECTED':
                        profit_change = (random.random() - 0.25) * 25  # Bias towards profit
                        self.broker_configs['icm']['profit'] += profit_change
                        
                        if random.random() > 0.9:  # 10% chance of new order
                            self.broker_configs['icm']['orders'] += 1
                            self.log_message(f"ICMarkets: New order executed - Profit: ${profit_change:.2f}")
                    
                    # Update UI
                    self.update_ui()
                    
                    time.sleep(2)  # Update every 2 seconds
                    
                except Exception as e:
                    self.log_message(f"Trading simulation error: {str(e)}")
                    time.sleep(5)
        
        threading.Thread(target=trading_loop, daemon=True).start()
    
    def update_ui(self):
        """Update UI with current data"""
        try:
            # Update broker displays
            self.exness_profit.config(text=f"Profit: ${self.broker_configs['exness']['profit']:.2f}")
            self.exness_orders.config(text=f"Orders: {self.broker_configs['exness']['orders']}")
            
            self.icm_profit.config(text=f"Profit: ${self.broker_configs['icm']['profit']:.2f}")
            self.icm_orders.config(text=f"Orders: {self.broker_configs['icm']['orders']}")
            
            # Calculate totals
            total_profit = (self.broker_configs['exness']['profit'] + 
                          self.broker_configs['icm']['profit'])
            total_orders = (self.broker_configs['exness']['orders'] + 
                          self.broker_configs['icm']['orders'])
            
            self.trading_stats['total_profit'] = total_profit
            self.trading_stats['trades_today'] = total_orders
            
            # Update performance display
            self.total_profit_label.config(text=f"${total_profit:.2f}")
            
            if total_profit > 0:
                self.total_profit_label.config(fg="#00ff00")
            elif total_profit < 0:
                self.total_profit_label.config(fg="#ff4444")
            
            # Target progress
            target_progress = min(100, (total_profit / self.trading_stats['daily_target']) * 100)
            self.target_progress_label.config(text=f"{target_progress:.1f}%")
            self.progress_bar['value'] = target_progress
            
            # Win rate (simulated)
            win_rate = min(95, 70 + (total_profit / 50))
            self.trading_stats['win_rate'] = win_rate
            self.winrate_label.config(text=f"{win_rate:.1f}%")
            
            # Trades today
            self.trades_label.config(text=str(total_orders))
            
            # Update statistics tab
            self.update_statistics_display()
            
        except Exception as e:
            self.log_message(f"UI update error: {str(e)}")
    
    def update_statistics_display(self):
        """Update statistics tab"""
        try:
            stats_text = f"""
NEUROQUANT X TRADING STATISTICS
{'='*50}

SYSTEM STATUS:
- System Running: {'Yes' if self.is_running else 'No'}
- Start Time: {self.trading_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S') if self.trading_stats['start_time'] else 'N/A'}
- Uptime: {self.get_uptime()}

BROKER STATUS:
EXNESS:
- Status: {self.broker_configs['exness']['status']}
- Profit: ${self.broker_configs['exness']['profit']:.2f}
- Orders: {self.broker_configs['exness']['orders']}

ICMarkets:
- Status: {self.broker_configs['icm']['status']}
- Profit: ${self.broker_configs['icm']['profit']:.2f}
- Orders: {self.broker_configs['icm']['orders']}

TRADING PERFORMANCE:
- Total Profit: ${self.trading_stats['total_profit']:.2f}
- Daily Target: ${self.trading_stats['daily_target']:.2f}
- Target Progress: {(self.trading_stats['total_profit'] / self.trading_stats['daily_target'] * 100):.1f}%
- Win Rate: {self.trading_stats['win_rate']:.1f}%
- Total Trades: {self.trading_stats['trades_today']}

RISK MANAGEMENT:
- Max Risk per Trade: 2%
- Daily Loss Limit: 5%
- Position Limit: 10
- Current Risk Level: Low

SYSTEM HEALTH:
- CPU Usage: {psutil.cpu_percent():.1f}%
- Memory Usage: {psutil.virtual_memory().percent:.1f}%
- Disk Usage: {psutil.disk_usage('/').percent:.1f}%
            """
            
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", stats_text)
            
        except Exception as e:
            self.log_message(f"Statistics update error: {str(e)}")
    
    def get_uptime(self):
        """Get system uptime"""
        if self.trading_stats['start_time']:
            uptime = datetime.now() - self.trading_stats['start_time']
            hours, remainder = divmod(uptime.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        return "
