#!/usr/bin/env python3
"""
MetaAPI Bridge - Advanced MT5 Integration
Connects to MetaTrader 5 terminals via MetaAPI or direct socket connection
Version: 2.1.0 Professional Edition
"""

import os
import sys
import time
import json
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import socket
import struct
import uuid

# MetaAPI integration (if available)
try:
    from metaapi_cloud_sdk import MetaApi
    METAAPI_AVAILABLE = True
except ImportError:
    METAAPI_AVAILABLE = False

@dataclass
class MarketData:
    symbol: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime
    volume: int = 0

@dataclass
class Position:
    id: str
    symbol: str
    type: str  # 'buy' or 'sell'
    volume: float
    open_price: float
    current_price: float
    profit: float
    swap: float
    commission: float
    comment: str
    magic_number: int
    open_time: datetime

@dataclass
class Order:
    id: str
    symbol: str
    type: str
    volume: float
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    comment: str = ""
    magic_number: int = 0
    timestamp: datetime = None

class MetaAPIBridge:
    def __init__(self, broker_name: str, config: Dict[str, Any]):
        self.broker_name = broker_name
        self.config = config
        self.base_dir = Path(__file__).parent.parent
        self.logs_dir = self.base_dir / "logs"
        
        # Create logs directory
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Connection state
        self.is_connected = False
        self.connection_type = None  # 'metaapi', 'socket', or 'file'
        self.last_heartbeat = None
        
        # MetaAPI connection (if available)
        self.meta_api = None
        self.account = None
        
        # Socket connection
        self.socket_connection = None
        
        # Data storage
        self.market_data = {}
        self.positions = {}
        self.orders = {}
        self.account_info = {}
        
        # Statistics
        self.stats = {
            'connection_attempts': 0,
            'successful_connections': 0,
            'orders_sent': 0,
            'orders_executed': 0,
            'data_updates': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        # Initialize connection
        self.initialize_connection()
    
    def setup_logging(self):
        """Setup logging system"""
        log_file = self.logs_dir / f"meta_api_bridge_{self.broker_name.lower()}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(f"MetaAPIBridge_{self.broker_name}")
    
    def initialize_connection(self):
        """Initialize connection to MT5 terminal"""
        self.logger.info(f"Initializing MetaAPI Bridge for {self.broker_name}")
        
        # Try different connection methods in order of preference
        connection_methods = [
            ('metaapi', self.connect_via_metaapi),
            ('socket', self.connect_via_socket),
            ('file', self.connect_via_file_system)
        ]
        
        for method_name, method_func in connection_methods:
            try:
                self.stats['connection_attempts'] += 1
                self.logger.info(f"Attempting {method_name} connection...")
                
                if method_func():
                    self.connection_type = method_name
                    self.is_connected = True
                    self.stats['successful_connections'] += 1
                    self.logger.info(f"Connected via {method_name}")
                    break
                    
            except Exception as e:
                self.logger.warning(f"{method_name} connection failed: {e}")
                continue
        
        if not self.is_connected:
            self.logger.error("All connection methods failed")
            self.stats['errors'] += 1
        else:
            # Start monitoring
            self.start_monitoring()
    
    def connect_via_metaapi(self) -> bool:
        """Connect via MetaAPI cloud service"""
        if not METAAPI_AVAILABLE:
            self.logger.warning("MetaAPI SDK not available")
            return False
        
        try:
            # Get MetaAPI token from config
            token = self.config.get('metaapi_token')
            account_id = self.config.get('account_id')
            
            if not token or not account_id:
                self.logger.warning("MetaAPI credentials not configured")
                return False
            
            # Initialize MetaAPI
            self.meta_api = MetaApi(token)
            self.account = self.meta_api.metatrader_account_api.get_account(account_id)
            
            # Wait for account to be connected
            if self.account.state != 'DEPLOYED':
                self.logger.info("Waiting for account deployment...")
                self.account.wait_deployed()
            
            # Connect to terminal
            connection = self.account.get_rpc_connection()
            connection.connect()
            
            # Wait for connection
            connection.wait_synchronized()
            
            self.logger.info("MetaAPI connection established")
            return True
            
        except Exception as e:
            self.logger.error(f"MetaAPI connection error: {e}")
            return False
    
    def connect_via_socket(self) -> bool:
        """Connect via socket to MT5 terminal"""
        try:
            host = self.config.get('socket_host', 'localhost')
            port = self.config.get('socket_port', 9000)
            
            # Create socket connection
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.settimeout(10)
            
            result = self.socket_connection.connect_ex((host, port))
            
            if result == 0:
                self.logger.info(f"Socket connection established to {host}:{port}")
                return True
            else:
                self.socket_connection.close()
                self.socket_connection = None
                return False
                
        except Exception as e:
            self.logger.error(f"Socket connection error: {e}")
            if self.socket_connection:
                self.socket_connection.close()
                self.socket_connection = None
            return False
    
    def connect_via_file_system(self) -> bool:
        """Connect via file system communication"""
        try:
            # Create communication directories
            comm_dir = self.base_dir / "terminals" / self.broker_name.upper() / "communication"
            comm_dir.mkdir(parents=True, exist_ok=True)
            
            # Create input/output directories
            (comm_dir / "input").mkdir(exist_ok=True)
            (comm_dir / "output").mkdir(exist_ok=True)
            
            # Create status file
            status_file = comm_dir / "status.json"
            status_data = {
                'broker': self.broker_name,
                'status': 'CONNECTED',
                'timestamp': datetime.now().isoformat(),
                'pid': os.getpid()
            }
            
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            self.logger.info("File system communication initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"File system connection error: {e}")
            return False
    
    def start_monitoring(self):
        """Start monitoring threads"""
        if self.connection_type == 'metaapi':
            threading.Thread(target=self.monitor_metaapi, daemon=True).start()
        elif self.connection_type == 'socket':
            threading.Thread(target=self.monitor_socket, daemon=True).start()
        elif self.connection_type == 'file':
            threading.Thread(target=self.monitor_file_system, daemon=True).start()
        
        # Start heartbeat
        threading.Thread(target=self.heartbeat_monitor, daemon=True).start()
        
        self.logger.info("Monitoring threads started")
    
    def monitor_metaapi(self):
        """Monitor MetaAPI connection"""
        while self.is_connected:
            try:
                if self.account:
                    # Get account information
                    account_info = self.account.get_account_information()
                    self.account_info = {
                        'balance': account_info.balance,
                        'equity': account_info.equity,
                        'margin': account_info.margin,
                        'free_margin': account_info.margin_free,
                        'profit': account_info.profit
                    }
                    
                    # Get positions
                    positions = self.account.get_positions()
                    self.positions = {}
                    for pos in positions:
                        self.positions[pos.id] = Position(
                            id=pos.id,
                            symbol=pos.symbol,
                            type=pos.type,
                            volume=pos.volume,
                            open_price=pos.open_price,
                            current_price=pos.current_price,
                            profit=pos.profit,
                            swap=pos.swap,
                            commission=pos.commission,
                            comment=pos.comment,
                            magic_number=pos.magic,
                            open_time=pos.time
                        )
                    
                    self.stats['data_updates'] += 1
                    self.last_heartbeat = datetime.now()
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                self.logger.error(f"MetaAPI monitoring error: {e}")
                self.stats['errors'] += 1
                time.sleep(5)
    
    def monitor_socket(self):
        """Monitor socket connection"""
        while self.is_connected and self.socket_connection:
            try:
                # Send heartbeat
                heartbeat_msg = json.dumps({
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat()
                })
                
                self.socket_connection.send(heartbeat_msg.encode() + b'\n')
                
                # Receive data
                data = self.socket_connection.recv(4096)
                if data:
                    self.process_socket_data(data.decode())
                    self.last_heartbeat = datetime.now()
                    self.stats['data_updates'] += 1
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Socket monitoring error: {e}")
                self.stats['errors'] += 1
                self.is_connected = False
                break
    
    def monitor_file_system(self):
        """Monitor file system communication"""
        comm_dir = self.base_dir / "terminals" / self.broker_name.upper() / "communication"
        output_dir = comm_dir / "output"
        
        while self.is_connected:
            try:
                # Check for new data files
                for file_path in output_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        self.process_file_data(data)
                        
                        # Move processed file
                        processed_dir = output_dir / "processed"
                        processed_dir.mkdir(exist_ok=True)
                        file_path.rename(processed_dir / file_path.name)
                        
                        self.stats['data_updates'] += 1
                        self.last_heartbeat = datetime.now()
                        
                    except Exception as e:
                        self.logger.error(f"Error processing file {file_path}: {e}")
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                self.logger.error(f"File system monitoring error: {e}")
                self.stats['errors'] += 1
                time.sleep(5)
    
    def process_socket_data(self, data: str):
        """Process data received via socket"""
        try:
            for line in data.strip().split('\n'):
                if line:
                    msg = json.loads(line)
                    self.process_message(msg)
        except Exception as e:
            self.logger.error(f"Socket data processing error: {e}")
    
    def process_file_data(self, data: Dict[str, Any]):
        """Process data from file system"""
        try:
            self.process_message(data)
        except Exception as e:
            self.logger.error(f"File data processing error: {e}")
    
    def process_message(self, msg: Dict[str, Any]):
        """Process incoming message"""
        try:
            msg_type = msg.get('type')
            
            if msg_type == 'market_data':
                self.update_market_data(msg)
            elif msg_type == 'position_update':
                self.update_position(msg)
            elif msg_type == 'order_update':
                self.update_order(msg)
            elif msg_type == 'account_info':
                self.update_account_info(msg)
            elif msg_type == 'error':
                self.logger.error(f"Received error: {msg.get('message')}")
                self.stats['errors'] += 1
            
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")
    
    def update_market_data(self, msg: Dict[str, Any]):
        """Update market data"""
        symbol = msg.get('symbol')
        if symbol:
            self.market_data[symbol] = MarketData(
                symbol=symbol,
                bid=msg.get('bid', 0.0),
                ask=msg.get('ask', 0.0),
                spread=msg.get('spread', 0.0),
                timestamp=datetime.now(),
                volume=msg.get('volume', 0)
            )
    
    def update_position(self, msg: Dict[str, Any]):
        """Update position information"""
        pos_id = msg.get('id')
        if pos_id:
            self.positions[pos_id] = Position(
                id=pos_id,
                symbol=msg.get('symbol', ''),
                type=msg.get('type', ''),
                volume=msg.get('volume', 0.0),
                open_price=msg.get('open_price', 0.0),
                current_price=msg.get('current_price', 0.0),
                profit=msg.get('profit', 0.0),
                swap=msg.get('swap', 0.0),
                commission=msg.get('commission', 0.0),
                comment=msg.get('comment', ''),
                magic_number=msg.get('magic_number', 0),
                open_time=datetime.fromisoformat(msg.get('open_time', datetime.now().isoformat()))
            )
    
    def update_order(self, msg: Dict[str, Any]):
        """Update order information"""
        order_id = msg.get('id')
        if order_id:
            self.orders[order_id] = Order(
                id=order_id,
                symbol=msg.get('symbol', ''),
                type=msg.get('type', ''),
                volume=msg.get('volume', 0.0),
                price=msg.get('price', 0.0),
                stop_loss=msg.get('stop_loss'),
                take_profit=msg.get('take_profit'),
                comment=msg.get('comment', ''),
                magic_number=msg.get('magic_number', 0),
                timestamp=datetime.fromisoformat(msg.get('timestamp', datetime.now().isoformat()))
            )
    
    def update_account_info(self, msg: Dict[str, Any]):
        """Update account information"""
        self.account_info = {
            'balance': msg.get('balance', 0.0),
            'equity': msg.get('equity', 0.0),
            'margin': msg.get('margin', 0.0),
            'free_margin': msg.get('free_margin', 0.0),
            'profit': msg.get('profit', 0.0),
            'currency': msg.get('currency', 'USD'),
            'leverage': msg.get('leverage', 1)
        }
    
    def send_order(self, order: Order) -> bool:
        """Send trading order"""
        try:
            self.stats['orders_sent'] += 1
            
            order_data = {
                'type': 'place_order',
                'order': asdict(order),
                'timestamp': datetime.now().isoformat(),
                'broker': self.broker_name
            }
            
            if self.connection_type == 'metaapi':
                return self.send_order_via_metaapi(order_data)
            elif self.connection_type == 'socket':
                return self.send_order_via_socket(order_data)
            elif self.connection_type == 'file':
                return self.send_order_via_file(order_data)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Order sending error: {e}")
            self.stats['errors'] += 1
            return False
    
    def send_order_via_metaapi(self, order_data: Dict[str, Any]) -> bool:
        """Send order via MetaAPI"""
        try:
            if self.account:
                order = order_data['order']
                
                # Convert to MetaAPI format
                trade_request = {
                    'symbol': order['symbol'],
                    'cmd': 0 if order['type'].upper() == 'BUY' else 1,
                    'volume': order['volume'],
                    'price': order['price'],
                    'sl': order.get('stop_loss'),
                    'tp': order.get('take_profit'),
                    'comment': order.get('comment', ''),
                    'magic': order.get('magic_number', 0)
                }
                
                # Remove None values
                trade_request = {k: v for k, v in trade_request.items() if v is not None}
                
                # Send order
                result = self.account.trade(trade_request)
                
                if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                    self.stats['orders_executed'] += 1
                    self.logger.info(f"Order executed via MetaAPI: {result.get('order')}")
                    return True
                else:
                    self.logger.error(f"MetaAPI order failed: {result}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"MetaAPI order error: {e}")
            return False
    
    def send_order_via_socket(self, order_data: Dict[str, Any]) -> bool:
        """Send order via socket"""
        try:
            if self.socket_connection:
                message = json.dumps(order_data) + '\n'
                self.socket_connection.send(message.encode())
                
                # Wait for response
                response = self.socket_connection.recv(1024)
                if response:
                    result = json.loads(response.decode())
                    if result.get('status') == 'success':
                        self.stats['orders_executed'] += 1
                        self.logger.info(f"Order executed via socket: {result.get('order_id')}")
                        return True
                    else:
                        self.logger.error(f"Socket order failed: {result.get('error')}")
                        return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Socket order error: {e}")
            return False
    
    def send_order_via_file(self, order_data: Dict[str, Any]) -> bool:
        """Send order via file system"""
        try:
            comm_dir = self.base_dir / "terminals" / self.broker_name.upper() / "communication"
            input_dir = comm_dir / "input"
            
            # Create unique filename
            filename = f"order_{uuid.uuid4().hex[:8]}_{int(time.time())}.json"
            file_path = input_dir / filename
            
            # Write order data
            with open(file_path, 'w') as f:
                json.dump(order_data, f, indent=2)
            
            # Wait for response file
            response_file = input_dir / f"response_{filename}"
            
            # Wait up to 10 seconds for response
            for _ in range(100):  # 10 seconds with 0.1s intervals
                if response_file.exists():
                    try:
                        with open(response_file, 'r') as f:
                            result = json.load(f)
                        
                        response_file.unlink()  # Delete response file
                        
                        if result.get('status') == 'success':
                            self.stats['orders_executed'] += 1
                            self.logger.info(f"Order executed via file: {result.get('order_id')}")
                            return True
                        else:
                            self.logger.error(f"File order failed: {result.get('error')}")
                            return False
                            
                    except Exception as e:
                        self.logger.error(f"Response file error: {e}")
                        return False
                
                time.sleep(0.1)
            
            self.logger.error("Order response timeout")
            return False
            
        except Exception as e:
            self.logger.error(f"File order error: {e}")
            return False
    
    def heartbeat_monitor(self):
        """Monitor connection health"""
        while self.is_connected:
            try:
                current_time = datetime.now()
                
                # Check if we've received data recently
                if self.last_heartbeat:
                    time_since_heartbeat = current_time - self.last_heartbeat
                    
                    if time_since_heartbeat > timedelta(minutes=2):
                        self.logger.warning(f"No heartbeat for {time_since_heartbeat}")
                        
                        # Attempt reconnection
                        self.reconnect()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Heartbeat monitor error: {e}")
                time.sleep(60)
    
    def reconnect(self):
        """Attempt to reconnect"""
        self.logger.info("Attempting to reconnect...")
        
        # Close existing connections
        self.disconnect()
        
        # Wait a moment
        time.sleep(5)
        
        # Reinitialize connection
        self.initialize_connection()
    
    def disconnect(self):
        """Disconnect from MT5 terminal"""
        try:
            self.is_connected = False
            
            if self.socket_connection:
                self.socket_connection.close()
                self.socket_connection = None
            
            if self.account:
                # Close MetaAPI connection
                self.account = None
                self.meta_api = None
            
            self.logger.info("Disconnected from MT5 terminal")
            
        except Exception as e:
            self.logger.error(f"Disconnect error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            'broker': self.broker_name,
            'connected': self.is_connected,
            'connection_type': self.connection_type,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'uptime_seconds': uptime.total_seconds(),
            'statistics': self.stats,
            'account_info': self.account_info,
            'positions_count': len(self.positions),
            'orders_count': len(self.orders),
            'market_data_symbols': list(self.market_data.keys())
        }
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data for symbol"""
        return self.market_data.get(symbol)
    
    def get_positions(self) -> List[Position]:
        """Get all positions"""
        return list(self.positions.values())
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return self.account_info.copy()

def main():
    """Main entry point for testing"""
    try:
        # Test configuration
        config = {
            'socket_host': 'localhost',
            'socket_port': 9001,
            'metaapi_token': None,  # Add your MetaAPI token here
            'account_id': None      # Add your account ID here
        }
        
        # Create bridge for EXNESS
        bridge = MetaAPIBridge('EXNESS', config)
        
        if bridge.is_connected:
            print(f"Bridge connected via {bridge.connection_type}")
            
            # Test order
            test_order = Order(
                id=str(uuid.uuid4()),
                symbol='EURUSD',
                type='BUY',
                volume=0.1,
                price=1.0850,
                stop_loss=1.0800,
                take_profit=1.0900,
                comment='Test order from MetaAPI Bridge'
            )
            
            print("Sending test order...")
            success = bridge.send_order(test_order)
            print(f"Order result: {'Success' if success else 'Failed'}")
            
            # Keep running
            try:
                while True:
                    time.sleep(10)
                    status = bridge.get_status()
                    print(f"Status: {status}")
                    
            except KeyboardInterrupt:
                print("\nShutting down...")
                bridge.disconnect()
        else:
            print("Failed to connect bridge")
            
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
