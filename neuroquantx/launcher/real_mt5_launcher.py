#!/usr/bin/env python3
"""
Real MT5 Launcher - Dual Broker Integration
Launches actual MT5 terminals for Exness and ICMarkets
Version: 2.1.0 Professional Edition
"""

import os
import sys
import subprocess
import time
import json
import logging
from pathlib import Path
import psutil
import winreg
from datetime import datetime

class RealMT5Launcher:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.terminals_dir = self.base_dir / "terminals"
        self.logs_dir = self.base_dir / "logs"
        
        # Create logs directory
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # MT5 configurations
        self.brokers = {
            'exness': {
                'name': 'EXNESS',
                'terminal_dir': self.terminals_dir / "EXNESS",
                'executable': "terminal64.exe",
                'config_file': "config.json",
                'process': None,
                'status': 'DISCONNECTED'
            },
            'icm': {
                'name': 'ICMarkets',
                'terminal_dir': self.terminals_dir / "ICM",
                'executable': "terminal64.exe",
                'config_file': "config.json",
                'process': None,
                'status': 'DISCONNECTED'
            }
        }
        
        # System MT5 installation path
        self.mt5_system_path = self.find_mt5_installation()
        
    def setup_logging(self):
        """Setup logging system"""
        log_file = self.logs_dir / "mt5_launcher.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def find_mt5_installation(self):
        """Find MT5 installation path in system"""
        possible_paths = [
            "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            "C:\\Program Files (x86)\\MetaTrader 5\\terminal64.exe",
            "C:\\Users\\{}\\AppData\\Roaming\\MetaQuotes\\Terminal\\*.exe".format(os.getenv('USERNAME')),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found MT5 installation: {path}")
                return path
        
        # Try to find via registry
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    if "metatrader" in subkey_name.lower() or "mt5" in subkey_name.lower():
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                mt5_path = os.path.join(install_location, "terminal64.exe")
                                if os.path.exists(mt5_path):
                                    self.logger.info(f"Found MT5 via registry: {mt5_path}")
                                    return mt5_path
                            except FileNotFoundError:
                                continue
        except Exception as e:
            self.logger.warning(f"Registry search failed: {e}")
        
        self.logger.warning("MT5 installation not found in system")
        return None
    
    def create_broker_directories(self):
        """Create broker-specific directories"""
        for broker_key, broker in self.brokers.items():
            try:
                # Create terminal directory
                broker['terminal_dir'].mkdir(parents=True, exist_ok=True)
                
                # Copy MT5 executable if system installation found
                if self.mt5_system_path:
                    terminal_exe = broker['terminal_dir'] / broker['executable']
                    if not terminal_exe.exists():
                        import shutil
                        shutil.copy2(self.mt5_system_path, terminal_exe)
                        self.logger.info(f"Copied MT5 executable to {terminal_exe}")
                
                # Create default config if not exists
                config_path = broker['terminal_dir'] / broker['config_file']
                if not config_path.exists():
                    self.create_default_config(broker_key, config_path)
                
                self.logger.info(f"Broker directory setup complete: {broker['terminal_dir']}")
                
            except Exception as e:
                self.logger.error(f"Error setting up {broker['name']} directory: {e}")
    
    def create_default_config(self, broker_key, config_path):
        """Create default configuration for broker"""
        if broker_key == 'exness':
            config = {
                "server": "ExnessEU-Real",
                "login": "",
                "password": "",
                "auto_trading": True,
                "expert_advisors": True,
                "dll_imports": True,
                "external_expert_imports": True,
                "risk_management": {
                    "max_risk_percent": 2,
                    "max_daily_loss": 5,
                    "max_positions": 10
                },
                "trading_settings": {
                    "slippage": 3,
                    "magic_number": 12345,
                    "comment": "NeuroQuantX_EXNESS"
                }
            }
        else:  # ICMarkets
            config = {
                "server": "ICMarketsEU-Demo",
                "login": "",
                "password": "",
                "auto_trading": True,
                "expert_advisors": True,
                "dll_imports": True,
                "external_expert_imports": True,
                "risk_management": {
                    "max_risk_percent": 2,
                    "max_daily_loss": 5,
                    "max_positions": 10
                },
                "trading_settings": {
                    "slippage": 3,
                    "magic_number": 54321,
                    "comment": "NeuroQuantX_ICM"
                }
            }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"Created default config: {config_path}")
    
    def launch_mt5_terminal(self, broker_key):
        """Launch MT5 terminal for specific broker"""
        broker = self.brokers[broker_key]
        
        try:
            terminal_exe = broker['terminal_dir'] / broker['executable']
            
            if not terminal_exe.exists():
                self.logger.error(f"MT5 executable not found: {terminal_exe}")
                return False
            
            # Load configuration
            config_path = broker['terminal_dir'] / broker['config_file']
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                self.logger.warning(f"Config not found for {broker['name']}, using defaults")
                config = {}
            
            # Prepare launch arguments
            args = [str(terminal_exe)]
            
            # Add configuration arguments if available
            if config.get('login'):
                args.extend(['/login', str(config['login'])])
            if config.get('password'):
                args.extend(['/password', config['password']])
            if config.get('server'):
                args.extend(['/server', config['server']])
            
            # Set portable mode
            args.append('/portable')
            
            # Launch process
            self.logger.info(f"Launching {broker['name']} terminal: {' '.join(args)}")
            
            process = subprocess.Popen(
                args,
                cwd=str(broker['terminal_dir']),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            broker['process'] = process
            broker['status'] = 'CONNECTING'
            
            # Wait a moment and check if process started successfully
            time.sleep(3)
            
            if process.poll() is None:
                broker['status'] = 'CONNECTED'
                self.logger.info(f"{broker['name']} terminal launched successfully (PID: {process.pid})")
                return True
            else:
                broker['status'] = 'ERROR'
                stdout, stderr = process.communicate()
                self.logger.error(f"{broker['name']} terminal failed to start")
                self.logger.error(f"STDOUT: {stdout.decode()}")
                self.logger.error(f"STDERR: {stderr.decode()}")
                return False
                
        except Exception as e:
            broker['status'] = 'ERROR'
            self.logger.error(f"Error launching {broker['name']} terminal: {e}")
            return False
    
    def launch_all_terminals(self):
        """Launch all MT5 terminals"""
        self.logger.info("Starting dual MT5 terminal launch...")
        
        # Create broker directories first
        self.create_broker_directories()
        
        success_count = 0
        
        # Launch EXNESS terminal
        if self.launch_mt5_terminal('exness'):
            success_count += 1
        
        # Wait between launches
        time.sleep(2)
        
        # Launch ICMarkets terminal
        if self.launch_mt5_terminal('icm'):
            success_count += 1
        
        self.logger.info(f"Terminal launch complete: {success_count}/2 successful")
        
        return success_count == 2
    
    def monitor_terminals(self):
        """Monitor running terminals"""
        self.logger.info("Starting terminal monitoring...")
        
        while True:
            try:
                for broker_key, broker in self.brokers.items():
                    if broker['process']:
                        if broker['process'].poll() is None:
                            # Process is still running
                            if broker['status'] != 'CONNECTED':
                                broker['status'] = 'CONNECTED'
                                self.logger.info(f"{broker['name']} terminal is running")
                        else:
                            # Process has terminated
                            broker['status'] = 'DISCONNECTED'
                            self.logger.warning(f"{broker['name']} terminal has terminated")
                            
                            # Attempt restart
                            self.logger.info(f"Attempting to restart {broker['name']} terminal...")
                            if self.launch_mt5_terminal(broker_key):
                                self.logger.info(f"{broker['name']} terminal restarted successfully")
                            else:
                                self.logger.error(f"Failed to restart {broker['name']} terminal")
                
                # Log status every 5 minutes
                current_time = datetime.now()
                if current_time.minute % 5 == 0 and current_time.second < 10:
                    self.log_status()
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(30)
    
    def log_status(self):
        """Log current status of all terminals"""
        status_info = []
        for broker_key, broker in self.brokers.items():
            pid = broker['process'].pid if broker['process'] and broker['process'].poll() is None else 'N/A'
            status_info.append(f"{broker['name']}: {broker['status']} (PID: {pid})")
        
        self.logger.info(f"Terminal Status - {' | '.join(status_info)}")
    
    def shutdown_terminals(self):
        """Shutdown all terminals gracefully"""
        self.logger.info("Shutting down all terminals...")
        
        for broker_key, broker in self.brokers.items():
            if broker['process'] and broker['process'].poll() is None:
                try:
                    # Try graceful shutdown first
                    broker['process'].terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        broker['process'].wait(timeout=10)
                        self.logger.info(f"{broker['name']} terminal shut down gracefully")
                    except subprocess.TimeoutExpired:
                        # Force kill if necessary
                        broker['process'].kill()
                        self.logger.warning(f"{broker['name']} terminal force killed")
                    
                    broker['status'] = 'DISCONNECTED'
                    
                except Exception as e:
                    self.logger.error(f"Error shutting down {broker['name']} terminal: {e}")
    
    def get_system_info(self):
        """Get system information"""
        info = {
            'mt5_system_path': self.mt5_system_path,
            'base_directory': str(self.base_dir),
            'terminals_directory': str(self.terminals_dir),
            'python_version': sys.version,
            'platform': os.name,
            'cpu_count': os.cpu_count(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2)
        }
        
        return info
    
    def run(self):
        """Main run method"""
        try:
            self.logger.info("NeuroQuantX Real MT5 Launcher starting...")
            
            # Log system information
            sys_info = self.get_system_info()
            self.logger.info(f"System Info: {sys_info}")
            
            # Launch all terminals
            if self.launch_all_terminals():
                self.logger.info("All terminals launched successfully")
                
                # Start monitoring
                self.monitor_terminals()
            else:
                self.logger.error("Failed to launch all terminals")
                return False
                
        except KeyboardInterrupt:
            self.logger.info("Launcher interrupted by user")
        except Exception as e:
            self.logger.error(f"Launcher error: {e}")
        finally:
            self.shutdown_terminals()
            self.logger.info("NeuroQuantX Real MT5 Launcher stopped")

def main():
    """Main entry point"""
    try:
        launcher = RealMT5Launcher()
        launcher.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
