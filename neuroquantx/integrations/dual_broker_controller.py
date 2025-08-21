#!/usr/bin/env python3
"""
Dual Broker Controller - Advanced Trading Bridge
Controls both Exness and ICMarkets terminals simultaneously
Version: 2.1.0 Professional Edition
"""

import os
import sys
import time
import json
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
import queue
import socket
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"
    MODIFY = "MODIFY"

class OrderStatus(Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class TradingSignal:
    symbol: str
    order_type: OrderType
    volume: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    comment: str = ""
    magic_number: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class OrderResult:
    broker: str
    order_id: Optional[str]
    status: OrderStatus
    execution_time: float
    error_message: Optional[str] = None
    executed_price: Optional[float] = None

class DualBrokerController:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.logs_dir = self.base_dir / "logs"
        self.config_dir = self.base_dir / "config"
        
        # Create directories
        self.logs_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Broker configurations
        self.brokers = {
            'exness': {
                'name': 'EXNESS',
                'host': 'localhost',
                'port': 9001,
                'socket': None,
                'connected': False,
                'last_ping': None,
                'orders_sent': 0,
                'orders_executed': 0,
                'total_profit': 0.0,
                'magic_number': 12345
            },
            'icm': {
                'name': 'ICMarkets',
                'host': 'localhost',
                'port': 9002,
                'socket': None,
                'connected': False,
                'last_ping': None,
                'orders_sent': 0,
                'orders_executed': 0,
                'total_profit': 0.0,
                'magic_number': 54321
            }
        }
        
        # Trading state
        self.is_running = False
        self.signal_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.active_orders = {}
        
        # Risk management
        self.risk_settings = {
            'max_risk_per_trade': 2.0,  # 2%
            'max_daily_loss': 5.0,      # 5%
            'max_positions': 10,
            'max_lot_size': 1.0,
            'min_lot_size': 0.01
        }
        
        # Performance tracking
        self.performance_stats = {
            'total_signals': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_profit': 0.0,
            'start_time': datetime.now(),
            'last_signal_time': None
        }
        
        # Load configuration
        self.load_configuration()
    
    def setup_logging(self):
        """Setup logging system"""
        log_file = self.logs_dir / "dual_broker_controller.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Create separate loggers for each broker
        self.exness_logger = self.create_broker_logger('exness')
        self.icm_logger = self.create_broker_logger('icm')
    
    def create_broker_logger(self, broker_name):
        """Create separate logger for each broker"""
        logger = logging.getLogger(f"{broker_name}_trades")
        handler = logging.FileHandler(self.logs_dir / f"{broker_name}_trades.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def load_configuration(self):
        """Load system configuration"""
        config_file = self.config_dir / "dual_broker_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Update broker settings
                for broker_key in self.brokers:
                    if broker_key in config.get('brokers', {}):
                        self.brokers[broker_key].update(config['brokers'][broker_key])
                
                # Update risk settings
                if 'risk_management' in config:
                    self.risk_settings.update(config['risk_management'])
                
                self.logger.info("Configuration loaded successfully")
                
            except Exception as e:
                self.logger.error(f"Error loading configuration: {e}")
                self.create_default_configuration()
        else:
            self.create_default_configuration()
    
    def create_default_configuration(self):
        """Create default configuration file"""
        config = {
            "brokers": {
                "exness": {
                    "host": "localhost",
                    "port": 9001,
                    "magic_number": 12345,
                    "max_slippage": 3
                },
                "icm": {
                    "host": "localhost",
                    "port": 9002,
                    "magic_number": 54321,
                    "max_slippage": 3
                }
            },
            "risk_management": self.risk_settings,
            "trading_settings": {
                "enable_mirror_trading": True,
                "sync_timeout": 5.0,
                "retry_attempts": 3,
                "heartbeat_interval": 30
            }
        }
        
        config_file = self.config_dir / "dual_broker_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info("Default configuration created")
    
    def connect_to_brokers(self):
        """Connect to both broker terminals"""
        self.logger.info("Connecting to broker terminals...")
        
        connection_results = {}
        
        for broker_key, broker in self.brokers.items():
            try:
                # Create socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)  # 10 second timeout
                
                result = sock.connect_ex((broker['host'], broker['port']))
                
                if result == 0:
                    broker['socket'] = sock
                    broker['connected'] = True
                    broker['last_ping'] = datetime.now()
                    connection_results[broker_key] = True
                    self.logger.info(f"Connected to {broker['name']} terminal")
                else:
                    sock.close()
                    broker['connected'] = False
                    connection_results[broker_key] = False
                    self.logger.error(f"Failed to connect to {broker['name']} terminal")
                    
            except Exception as e:
                broker['connected'] = False
                connection_results[broker_key] = False
                self.logger.error(f"Connection error for {broker['name']}: {e}")
        
        # Check if at least one broker is connected
        connected_count = sum(connection_results.values())
        
        if connected_count == 0:
            self.logger.error("No brokers connected - cannot proceed")
            return False
        elif connected_count == 1:
            self.logger.warning("Only one broker connected - limited functionality")
        else:
            self.logger.info("All brokers connected successfully")
        
        return connected_count > 0
    
    def send_trading_signal(self, signal: TradingSignal) -> Dict[str, OrderResult]:
        """Send trading signal to all connected brokers"""
        self.logger.info(f"Processing trading signal: {signal.symbol} {signal.order_type.value} {signal.volume}")
        
        # Validate signal
        if not self.validate_signal(signal):
            self.logger.error("Signal validation failed")
            return {}
        
        # Update performance stats
        self.performance_stats['total_signals'] += 1
        self.performance_stats['last_signal_time'] = datetime.now()
        
        results = {}
        
        # Send to all connected brokers
        for broker_key, broker in self.brokers.items():
            if broker['connected']:
                result = self.execute_order_on_broker(broker_key, signal)
                results[broker_key] = result
                
                # Log to broker-specific log
                if broker_key == 'exness':
                    self.exness_logger.info(f"Signal: {signal.symbol} {signal.order_type.value} - Result: {result.status.value}")
                else:
                    self.icm_logger.info(f"Signal: {signal.symbol} {signal.order_type.value} - Result: {result.status.value}")
        
        # Update statistics
        successful_executions = sum(1 for r in results.values() if r.status == OrderStatus.EXECUTED)
        failed_executions = len(results) - successful_executions
        
        self.performance_stats['successful_executions'] += successful_executions
        self.performance_stats['failed_executions'] += failed_executions
        
        self.logger.info(f"Signal execution complete: {successful_executions}/{len(results)} successful")
        
        return results
    
    def validate_signal(self, signal: TradingSignal) -> bool:
        """Validate trading signal"""
        try:
            # Check volume limits
            if signal.volume < self.risk_settings['min_lot_size']:
                self.logger.error(f"Volume too small: {signal.volume}")
                return False
            
            if signal.volume > self.risk_settings['max_lot_size']:
                self.logger.error(f"Volume too large: {signal.volume}")
                return False
            
            # Check symbol format
            if not signal.symbol or len(signal.symbol) < 6:
                self.logger.error(f"Invalid symbol: {signal.symbol}")
                return False
            
            # Check order type
            if signal.order_type not in OrderType:
                self.logger.error(f"Invalid order type: {signal.order_type}")
                return False
            
            # Check risk management
            if not self.check_risk_limits():
                self.logger.error("Risk limits exceeded")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Signal validation error: {e}")
            return False
    
    def check_risk_limits(self) -> bool:
        """Check if current risk is within limits"""
        try:
            # Check daily loss limit
            total_daily_loss = abs(min(0, self.performance_stats['total_profit']))
            daily_loss_percent = (total_daily_loss / 10000) * 100  # Assuming $10k account
            
            if daily_loss_percent >= self.risk_settings['max_daily_loss']:
                self.logger.warning(f"Daily loss limit reached: {daily_loss_percent:.2f}%")
                return False
            
            # Check maximum positions
            active_positions = len(self.active_orders)
            if active_positions >= self.risk_settings['max_positions']:
                self.logger.warning(f"Maximum positions limit reached: {active_positions}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Risk check error: {e}")
            return False
    
    def execute_order_on_broker(self, broker_key: str, signal: TradingSignal) -> OrderResult:
        """Execute order on specific broker"""
        broker = self.brokers[broker_key]
        start_time = time.time()
        
        try:
            # Prepare order data
            order_data = {
                'action': 'TRADE',
                'symbol': signal.symbol,
                'cmd': signal.order_type.value,
                'volume': signal.volume,
                'price': signal.price,
                'sl': signal.stop_loss,
                'tp': signal.take_profit,
                'comment': signal.comment or f"NeuroQuantX_{broker_key.upper()}",
                'magic': broker['magic_number'],
                'timestamp': signal.timestamp.isoformat()
            }
            
            # Send order to broker terminal (simulated)
            order_id = self.simulate_order_execution(broker_key, order_data)
            
            execution_time = time.time() - start_time
            
            if order_id:
                # Update broker statistics
                broker['orders_sent'] += 1
                broker['orders_executed'] += 1
                
                # Store active order
                self.active_orders[order_id] = {
                    'broker': broker_key,
                    'signal': signal,
                    'timestamp': datetime.now()
                }
                
                result = OrderResult(
                    broker=broker['name'],
                    order_id=order_id,
                    status=OrderStatus.EXECUTED,
                    execution_time=execution_time,
                    executed_price=signal.price
                )
                
                self.logger.info(f"{broker['name']}: Order executed - ID: {order_id}, Time: {execution_time:.3f}s")
                
            else:
                broker['orders_sent'] += 1
                
                result = OrderResult(
                    broker=broker['name'],
                    order_id=None,
                    status=OrderStatus.FAILED,
                    execution_time=execution_time,
                    error_message="Order execution failed"
                )
                
                self.logger.error(f"{broker['name']}: Order execution failed")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = OrderResult(
                broker=broker['name'],
                order_id=None,
                status=OrderStatus.FAILED,
                execution_time=execution_time,
                error_message=str(e)
            )
            
            self.logger.error(f"{broker['name']}: Order execution error: {e}")
            return result
    
    def simulate_order_execution(self, broker_key: str, order_data: dict) -> Optional[str]:
        """Simulate order execution (replace with real MT5 API calls)"""
        try:
            # Simulate network delay
            time.sleep(0.05 + (0.1 * hash(broker_key) % 10) / 100)
            
            # Simulate 95% success rate
            import random
            if random.random() < 0.95:
                # Generate order ID
                order_id = f"{broker_key.upper()}_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Simulate profit/loss
                profit_change = (random.random() - 0.3) * 50  # Bias towards profit
                self.brokers[broker_key]['total_profit'] += profit_change
                self.performance_stats['total_profit'] += profit_change
                
                return order_id
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Order simulation error: {e}")
            return None
    
    def start_heartbeat_monitor(self):
        """Start heartbeat monitoring for broker connections"""
        def heartbeat_loop():
            while self.is_running:
                try:
                    for broker_key, broker in self.brokers.items():
                        if broker['connected']:
                            # Send ping to broker
                            if self.ping_broker(broker_key):
                                broker['last_ping'] = datetime.now()
                            else:
                                self.logger.warning(f"{broker['name']} heartbeat failed")
                                broker['connected'] = False
                                
                                # Attempt reconnection
                                self.reconnect_broker(broker_key)
                    
                    time.sleep(30)  # Heartbeat every 30 seconds
                    
                except Exception as e:
                    self.logger.error(f"Heartbeat monitor error: {e}")
                    time.sleep(60)
        
        threading.Thread(target=heartbeat_loop, daemon=True).start()
        self.logger.info("Heartbeat monitor started")
    
    def ping_broker(self, broker_key: str) -> bool:
        """Ping broker to check connection"""
        try:
            broker = self.brokers[broker_key]
            if broker['socket']:
                # Send ping message (simulated)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ping error for {broker_key}: {e}")
            return False
    
    def reconnect_broker(self, broker_key: str):
        """Attempt to reconnect to broker"""
        self.logger.info(f"Attempting to reconnect to {self.brokers[broker_key]['name']}")
        
        try:
            broker = self.brokers[broker_key]
            
            # Close existing socket
            if broker['socket']:
                broker['socket'].close()
                broker['socket'] = None
            
            # Attempt new connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            result = sock.connect_ex((broker['host'], broker['port']))
            
            if result == 0:
                broker['socket'] = sock
                broker['connected'] = True
                broker['last_ping'] = datetime.now()
                self.logger.info(f"Reconnected to {broker['name']}")
            else:
                sock.close()
                self.logger.error(f"Reconnection failed for {broker['name']}")
                
        except Exception as e:
            self.logger.error(f"Reconnection error for {broker_key}: {e}")
    
    def get_broker_status(self) -> Dict:
        """Get current status of all brokers"""
        status = {}
        
        for broker_key, broker in self.brokers.items():
            status[broker_key] = {
                'name': broker['name'],
                'connected': broker['connected'],
                'last_ping': broker['last_ping'].isoformat() if broker['last_ping'] else None,
                'orders_sent': broker['orders_sent'],
                'orders_executed': broker['orders_executed'],
                'total_profit': broker['total_profit'],
                'success_rate': (broker['orders_executed'] / max(1, broker['orders_sent'])) * 100
            }
        
        return status
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        uptime = datetime.now() - self.performance_stats['start_time']
        
        stats = {
            'total_signals': self.performance_stats['total_signals'],
            'successful_executions': self.performance_stats['successful_executions'],
            'failed_executions': self.performance_stats['failed_executions'],
            'success_rate': (self.performance_stats['successful_executions'] / 
                           max(1, self.performance_stats['total_signals'])) * 100,
            'total_profit': self.performance_stats['total_profit'],
            'uptime_hours': uptime.total_seconds() / 3600,
            'last_signal_time': (self.performance_stats['last_signal_time'].isoformat() 
                                if self.performance_stats['last_signal_time'] else None),
            'active_orders': len(self.active_orders)
        }
        
        return stats
    
    def start(self):
        """Start the dual broker controller"""
        try:
            self.logger.info("Starting Dual Broker Controller...")
            
            # Connect to brokers
            if not self.connect_to_brokers():
                self.logger.error("Failed to connect to brokers")
                return False
            
            self.is_running = True
            
            # Start heartbeat monitor
            self.start_heartbeat_monitor()
            
            self.logger.info("Dual Broker Controller started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start controller: {e}")
            return False
    
    def stop(self):
        """Stop the dual broker controller"""
        try:
            self.logger.info("Stopping Dual Broker Controller...")
            
            self.is_running = False
            
            # Close all broker connections
            for broker_key, broker in self.brokers.items():
                if broker['socket']:
                    broker['socket'].close()
                    broker['socket'] = None
                broker['connected'] = False
            
            self.logger.info("Dual Broker Controller stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping controller: {e}")
    
    def run_test_signal(self):
        """Run a test trading signal"""
        test_signal = TradingSignal(
            symbol="EURUSD",
            order_type=OrderType.BUY,
            volume=0.1,
            price=1.0850,
            stop_loss=1.0800,
            take_profit=1.0900,
            comment="Test signal from NeuroQuantX"
        )
        
        self.logger.info("Sending test trading signal...")
        results = self.send_trading_signal(test_signal)
        
        for broker_key, result in results.items():
            self.logger.info(f"Test result for {broker_key}: {result.status.value}")
        
        return results

def main():
    """Main entry point for testing"""
    try:
        controller = DualBrokerController()
        
        if controller.start():
            print("Dual Broker Controller started successfully")
            
            # Run test signal
            controller.run_test_signal()
            
            # Keep running
            try:
                while True:
                    time.sleep(10)
                    
                    # Print status every minute
                    status = controller.get_broker_status()
                    stats = controller.get_performance_stats()
                    
                    print(f"\nBroker Status: {status}")
                    print(f"Performance: {stats}")
                    
            except KeyboardInterrupt:
                print("\nShutting down...")
                controller.stop()
        else:
            print("Failed to start Dual Broker Controller")
            
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
