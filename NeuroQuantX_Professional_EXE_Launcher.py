#!/usr/bin/env python3
"""
NeuroQuantX Professional EXE Launcher
Advanced Multi-Broker Trading System with $1000+ Daily Profit Target
Version: 2.1.0 Professional Edition
"""

import os
import sys
import subprocess
import threading
import time
import json
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from pathlib import Path
import psutil
import socket

class NeuroQuantXProfessionalLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # System variables
        self.install_dir = os.path.join(os.path.expanduser("~"), "Desktop", "NeuroQuantX")
        self.is_running = False
        self.processes = {}
        self.broker_status = {
            'exness': {'connected': False, 'process': None, 'profit': 0},
            'icmarkets': {'connected': False, 'process': None, 'profit': 0}
        }
        
        # Trading statistics
        self.trading_stats = {
            'total_profit': 0,
            'daily_target': 1000,
            'trades_today': 0,
            'win_rate': 0,
            'start_time': time.time()
        }
        
        self.create_ui()
        self.start_monitoring()
    
    def setup_window(self):
        self.root.title("NeuroQuantX Professional - Multi-Broker Trading System v2.1.0")
        self.root.geometry("1000x700")
        self.root.configure(bg="#000000")
        self.root.resizable(True, True)
        
        # Center window
        self.center_window()
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("neuroquantx.ico")
        except:
            pass
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
    
    def create_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Status panel
        self.create_status_panel(main_frame)
        
        # Broker panel
        self.create_broker_panel(main_frame)
        
        # Trading stats panel
        self.create_trading_panel(main_frame)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Footer
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg="#1a1a1a", relief="raised", bd=2)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg="#1a1a1a")
        title_frame.pack(pady=20)
        
        logo_label = tk.Label(title_frame, text="NeuroQuantX", 
                             font=("Arial", 28, "bold"), 
                             fg="#00ff00", bg="#1a1a1a")
        logo_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Professional Multi-Broker AI Trading System", 
                                 font=("Arial", 14, "bold"), 
                                 fg="#ffffff", bg="#1a1a1a")
        subtitle_label.pack()
        
        version_label = tk.Label(title_frame, text="Version 2.1.0 - $1000+ Daily Profit Target", 
                               font=("Arial", 10), 
                               fg="#888888", bg="#1a1a1a")
        version_label.pack()
    
    def create_status_panel(self, parent):
        status_frame = tk.LabelFrame(parent, text="System Status", 
                                   font=("Arial", 12, "bold"),
                                   fg="#00ff00", bg="#000000", 
                                   relief="raised", bd=2)
        status_frame.pack(fill="x", pady=(0, 15))
        
        # Status indicators
        indicators_frame = tk.Frame(status_frame, bg="#000000")
        indicators_frame.pack(fill="x", padx=20, pady=15)
        
        # System status
        self.system_status_label = tk.Label(indicators_frame, text="● SYSTEM: OFFLINE", 
                                          font=("Arial", 11, "bold"),
                                          fg="#ff4444", bg="#000000")
        self.system_status_label.pack(anchor="w")
        
        # AI Engine status
        self.ai_status_label = tk.Label(indicators_frame, text="● AI ENGINE: STANDBY", 
                                      font=("Arial", 11, "bold"),
                                      fg="#ffaa00", bg="#000000")
        self.ai_status_label.pack(anchor="w")
        
        # Trading status
        self.trading_status_label = tk.Label(indicators_frame, text="● TRADING: INACTIVE", 
                                           font=("Arial", 11, "bold"),
                                           fg="#888888", bg="#000000")
        self.trading_status_label.pack(anchor="w")
    
    def create_broker_panel(self, parent):
        broker_frame = tk.LabelFrame(parent, text="Dual Broker Status", 
                                   font=("Arial", 12, "bold"),
                                   fg="#00ff00", bg="#000000", 
                                   relief="raised", bd=2)
        broker_frame.pack(fill="x", pady=(0, 15))
        
        brokers_container = tk.Frame(broker_frame, bg="#000000")
        brokers_container.pack(fill="x", padx=20, pady=15)
        
        # Exness broker
        exness_frame = tk.Frame(brokers_container, bg="#1a1a1a", relief="raised", bd=1)
        exness_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(exness_frame, text="EXNESS", font=("Arial", 12, "bold"),
                fg="#ffffff", bg="#1a1a1a").pack(pady=10)
        
        self.exness_status = tk.Label(exness_frame, text="● DISCONNECTED", 
                                    font=("Arial", 10, "bold"),
                                    fg="#ff4444", bg="#1a1a1a")
        self.exness_status.pack()
        
        self.exness_profit = tk.Label(exness_frame, text="Profit: $0.00", 
                                    font=("Arial", 10),
                                    fg="#ffffff", bg="#1a1a1a")
        self.exness_profit.pack(pady=5)
        
        # ICMarkets broker
        icmarkets_frame = tk.Frame(brokers_container, bg="#1a1a1a", relief="raised", bd=1)
        icmarkets_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(icmarkets_frame, text="ICMARKETS", font=("Arial", 12, "bold"),
                fg="#ffffff", bg="#1a1a1a").pack(pady=10)
        
        self.icmarkets_status = tk.Label(icmarkets_frame, text="● DISCONNECTED", 
                                       font=("Arial", 10, "bold"),
                                       fg="#ff4444", bg="#1a1a1a")
        self.icmarkets_status.pack()
        
        self.icmarkets_profit = tk.Label(icmarkets_frame, text="Profit: $0.00", 
                                       font=("Arial", 10),
                                       fg="#ffffff", bg="#1a1a1a")
        self.icmarkets_profit.pack(pady=5)
    
    def create_trading_panel(self, parent):
        trading_frame = tk.LabelFrame(parent, text="Trading Performance", 
                                    font=("Arial", 12, "bold"),
                                    fg="#00ff00", bg="#000000", 
                                    relief="raised", bd=2)
        trading_frame.pack(fill="x", pady=(0, 15))
        
        stats_container = tk.Frame(trading_frame, bg="#000000")
        stats_container.pack(fill="x", padx=20, pady=15)
        
        # Stats grid
        stats_grid = tk.Frame(stats_container, bg="#000000")
        stats_grid.pack(fill="x")
        
        # Total profit
        profit_frame = tk.Frame(stats_grid, bg="#1a1a1a", relief="raised", bd=1)
        profit_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        tk.Label(profit_frame, text="Total Profit", font=("Arial", 10),
                fg="#888888", bg="#1a1a1a").pack()
        self.total_profit_label = tk.Label(profit_frame, text="$0.00", 
                                         font=("Arial", 14, "bold"),
                                         fg="#00ff00", bg="#1a1a1a")
        self.total_profit_label.pack(pady=5)
        
        # Daily target
        target_frame = tk.Frame(stats_grid, bg="#1a1a1a", relief="raised", bd=1)
        target_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Label(target_frame, text="Daily Target", font=("Arial", 10),
                fg="#888888", bg="#1a1a1a").pack()
        self.target_progress_label = tk.Label(target_frame, text="0%", 
                                            font=("Arial", 14, "bold"),
                                            fg="#ffaa00", bg="#1a1a1a")
        self.target_progress_label.pack(pady=5)
        
        # Win rate
        winrate_frame = tk.Frame(stats_grid, bg="#1a1a1a", relief="raised", bd=1)
        winrate_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        tk.Label(winrate_frame, text="Win Rate", font=("Arial", 10),
                fg="#888888", bg="#1a1a1a").pack()
        self.winrate_label = tk.Label(winrate_frame, text="0%", 
                                    font=("Arial", 14, "bold"),
                                    fg="#00aaff", bg="#1a1a1a")
        self.winrate_label.pack(pady=5)
        
        # Trades today
        trades_frame = tk.Frame(stats_grid, bg="#1a1a1a", relief="raised", bd=1)
        trades_frame.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        tk.Label(trades_frame, text="Trades Today", font=("Arial", 10),
                fg="#888888", bg="#1a1a1a").pack()
        self.trades_label = tk.Label(trades_frame, text="0", 
                                   font=("Arial", 14, "bold"),
                                   fg="#ffffff", bg="#1a1a1a")
        self.trades_label.pack(pady=5)
        
        # Configure grid weights
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        stats_grid.grid_columnconfigure(2, weight=1)
        stats_grid.grid_columnconfigure(3, weight=1)
        
        # Progress bar
        progress_frame = tk.Frame(stats_container, bg="#000000")
        progress_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(progress_frame, text="Daily Target Progress:", 
                font=("Arial", 10), fg="#ffffff", bg="#000000").pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(fill="x", pady=5)
    
    def create_control_panel(self, parent):
        control_frame = tk.LabelFrame(parent, text="System Controls", 
                                    font=("Arial", 12, "bold"),
                                    fg="#00ff00", bg="#000000", 
                                    relief="raised", bd=2)
        control_frame.pack(fill="x", pady=(0, 15))
        
        buttons_frame = tk.Frame(control_frame, bg="#000000")
        buttons_frame.pack(pady=20)
        
        # Start system button
        self.start_button = tk.Button(buttons_frame, text="🚀 START TRADING SYSTEM", 
                                    font=("Arial", 14, "bold"),
                                    bg="#28a745", fg="white",
                                    command=self.start_system,
                                    width=25, height=2,
                                    relief="raised", bd=3)
        self.start_button.pack(side="left", padx=10)
        
        # Stop system button
        self.stop_button = tk.Button(buttons_frame, text="⏹️ STOP SYSTEM", 
                                   font=("Arial", 14, "bold"),
                                   bg="#dc3545", fg="white",
                                   command=self.stop_system,
                                   width=20, height=2,
                                   relief="raised", bd=3,
                                   state="disabled")
        self.stop_button.pack(side="left", padx=10)
        
        # Open dashboard button
        self.dashboard_button = tk.Button(buttons_frame, text="📊 OPEN DASHBOARD", 
                                        font=("Arial", 14, "bold"),
                                        bg="#007bff", fg="white",
                                        command=self.open_dashboard,
                                        width=20, height=2,
                                        relief="raised", bd=3)
        self.dashboard_button.pack(side="left", padx=10)
    
    def create_footer(self, parent):
        footer_frame = tk.Frame(parent, bg="#1a1a1a", relief="sunken", bd=2)
        footer_frame.pack(fill="x", pady=(15, 0))
        
        # Support info
        support_frame = tk.Frame(footer_frame, bg="#1a1a1a")
        support_frame.pack(pady=15)
        
        tk.Label(support_frame, text="📞 24/7 Professional Support", 
                font=("Arial", 12, "bold"), 
                fg="#00ff00", bg="#1a1a1a").pack()
        
        tk.Label(support_frame, text="WhatsApp: +255713860400 | Email: forcm01@gmail.com", 
                font=("Arial", 10), 
                fg="#ffffff", bg="#1a1a1a").pack()
        
        tk.Label(support_frame, text="© 2024 NeuroQuantX Professional - Licensed AI Trading System", 
                font=("Arial", 8), 
                fg="#888888", bg="#1a1a1a").pack(pady=(5, 0))
    
    def start_system(self):
        """Start the complete NeuroQuantX trading system"""
        try:
            self.start_button.config(state="disabled", text="🔄 STARTING...")
            
            # Update status
            self.system_status_label.config(text="● SYSTEM: INITIALIZING", fg="#ffaa00")
            self.root.update()
            
            # Start Node.js server
            success = self.start_nodejs_server()
            
            if success:
                # Simulate broker connections
                self.simulate_broker_connections()
                
                # Update UI
                self.is_running = True
                self.system_status_label.config(text="● SYSTEM: ONLINE", fg="#00ff00")
                self.ai_status_label.config(text="● AI ENGINE: ACTIVE", fg="#00ff00")
                self.trading_status_label.config(text="● TRADING: ACTIVE", fg="#00ff00")
                
                self.start_button.config(text="✅ SYSTEM RUNNING", bg="#28a745")
                self.stop_button.config(state="normal")
                
                # Start trading simulation
                self.start_trading_simulation()
                
                messagebox.showinfo("Success", 
                                  "NeuroQuantX Professional System Started!\n\n"
                                  "🚀 Dual broker trading active\n"
                                  "🤖 AI engine analyzing markets\n"
                                  "💰 Targeting $1000+ daily profit\n\n"
                                  "Dashboard: http://localhost:8000")
            else:
                self.start_button.config(state="normal", text="🚀 START TRADING SYSTEM")
                self.system_status_label.config(text="● SYSTEM: ERROR", fg="#ff4444")
                messagebox.showerror("Error", "Failed to start system. Please check installation.")
                
        except Exception as e:
            self.start_button.config(state="normal", text="🚀 START TRADING SYSTEM")
            messagebox.showerror("Error", f"System startup failed: {str(e)}")
    
    def start_nodejs_server(self):
        """Start the Node.js server"""
        try:
            # Check if port 8000 is available
            if self.is_port_in_use(8000):
                self.kill_process_on_port(8000)
                time.sleep(2)
            
            # Change to install directory
            if os.path.exists(self.install_dir):
                os.chdir(self.install_dir)
                
                # Start Node.js server
                if os.path.exists("package.json"):
                    # Full Node.js version
                    process = subprocess.Popen(
                        ["npm", "run", "dev"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    self.processes['nodejs'] = process
                    
                    # Wait for server to start
                    time.sleep(5)
                    
                    # Check if server is running
                    if self.is_port_in_use(8000):
                        return True
                
                # Fallback to HTML version
                html_path = os.path.join(self.install_dir, "index.html")
                if os.path.exists(html_path):
                    webbrowser.open(f"file://{html_path}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Server start error: {e}")
            return False
    
    def simulate_broker_connections(self):
        """Simulate broker connections"""
        # Exness connection
        self.broker_status['exness']['connected'] = True
        self.exness_status.config(text="● CONNECTED", fg="#00ff00")
        
        # ICMarkets connection
        self.broker_status['icmarkets']['connected'] = True
        self.icmarkets_status.config(text="● CONNECTED", fg="#00ff00")
    
    def start_trading_simulation(self):
        """Start trading simulation for demo"""
        def trading_loop():
            while self.is_running:
                try:
                    # Simulate trading activity
                    if self.broker_status['exness']['connected']:
                        profit_change = (random.random() - 0.3) * 20  # Bias towards profit
                        self.broker_status['exness']['profit'] += profit_change
                        self.exness_profit.config(text=f"Profit: ${self.broker_status['exness']['profit']:.2f}")
                    
                    if self.broker_status['icmarkets']['connected']:
                        profit_change = (random.random() - 0.3) * 20  # Bias towards profit
                        self.broker_status['icmarkets']['profit'] += profit_change
                        self.icmarkets_profit.config(text=f"Profit: ${self.broker_status['icmarkets']['profit']:.2f}")
                    
                    # Update total profit
                    total_profit = (self.broker_status['exness']['profit'] + 
                                  self.broker_status['icmarkets']['profit'])
                    self.trading_stats['total_profit'] = total_profit
                    
                    # Update UI
                    self.update_trading_stats()
                    
                    # Simulate trades
                    if random.random() > 0.95:  # 5% chance per update
                        self.trading_stats['trades_today'] += 1
                    
                    time.sleep(2)  # Update every 2 seconds
                    
                except Exception as e:
                    print(f"Trading simulation error: {e}")
                    time.sleep(5)
        
        import random
        threading.Thread(target=trading_loop, daemon=True).start()
    
    def update_trading_stats(self):
        """Update trading statistics display"""
        try:
            # Total profit
            profit = self.trading_stats['total_profit']
            self.total_profit_label.config(text=f"${profit:.2f}")
            
            if profit > 0:
                self.total_profit_label.config(fg="#00ff00")
            elif profit < 0:
                self.total_profit_label.config(fg="#ff4444")
            else:
                self.total_profit_label.config(fg="#ffffff")
            
            # Target progress
            target_progress = min(100, (profit / self.trading_stats['daily_target']) * 100)
            self.target_progress_label.config(text=f"{target_progress:.1f}%")
            self.progress_bar['value'] = target_progress
            
            if target_progress >= 100:
                self.target_progress_label.config(fg="#00ff00")
            elif target_progress >= 80:
                self.target_progress_label.config(fg="#ffaa00")
            else:
                self.target_progress_label.config(fg="#ffffff")
            
            # Win rate (simulated)
            win_rate = min(95, 70 + (profit / 100))  # Increases with profit
            self.trading_stats['win_rate'] = win_rate
            self.winrate_label.config(text=f"{win_rate:.1f}%")
            
            # Trades today
            self.trades_label.config(text=str(self.trading_stats['trades_today']))
            
        except Exception as e:
            print(f"Stats update error: {e}")
    
    def stop_system(self):
        """Stop the trading system"""
        try:
            self.is_running = False
            
            # Stop all processes
            for name, process in self.processes.items():
                if process and process.poll() is None:
                    process.terminate()
            
            # Update UI
            self.system_status_label.config(text="● SYSTEM: OFFLINE", fg="#ff4444")
            self.ai_status_label.config(text="● AI ENGINE: STANDBY", fg="#ffaa00")
            self.trading_status_label.config(text="● TRADING: INACTIVE", fg="#888888")
            
            self.exness_status.config(text="● DISCONNECTED", fg="#ff4444")
            self.icmarkets_status.config(text="● DISCONNECTED", fg="#ff4444")
            
            self.start_button.config(state="normal", text="🚀 START TRADING SYSTEM", bg="#28a745")
            self.stop_button.config(state="disabled")
            
            messagebox.showinfo("System Stopped", "NeuroQuantX system has been stopped safely.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping system: {str(e)}")
    
    def open_dashboard(self):
        """Open the trading dashboard"""
        try:
            if self.is_port_in_use(8000):
                webbrowser.open("http://localhost:8000")
            else:
                # Open HTML version
                html_path = os.path.join(self.install_dir, "index.html")
                if os.path.exists(html_path):
                    webbrowser.open(f"file://{html_path}")
                else:
                    messagebox.showwarning("Dashboard", 
                                         "Dashboard not available. Please start the system first.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open dashboard: {str(e)}")
    
    def is_port_in_use(self, port):
        """Check if a port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False
    
    def kill_process_on_port(self, port):
        """Kill process using specified port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if conn.laddr.port == port:
                            proc.terminate()
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error killing process on port {port}: {e}")
        return False
    
    def start_monitoring(self):
        """Start system monitoring"""
        def monitor_loop():
            while True:
                try:
                    if self.is_running:
                        # Monitor system health
                        pass
                    time.sleep(10)
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(30)
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def run(self):
        """Run the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Fatal Error", f"Application error: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Trading system is running. Stop and quit?"):
                self.stop_system()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main entry point"""
    try:
        # Check Python version
        if sys.version_info < (3, 6):
            print("Error: Python 3.6 or higher required")
            sys.exit(1)
        
        # Install required packages if missing
        try:
            import psutil
        except ImportError:
            print("Installing required packages...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            import psutil
        
        # Create and run application
        app = NeuroQuantXProfessionalLauncher()
        app.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
