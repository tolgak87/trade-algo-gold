"""
MQL Bridge - Socket Server for MT4/MT5 Communication
Replaces MetaTrader5 Python module with MQL Expert Advisor bridge
"""

import socket
import json
import threading
import queue
from datetime import datetime
from typing import Optional, Dict, List, Callable
import time


class MQLBridge:
    """
    Socket-based bridge server for communicating with MT4/MT5 Expert Advisors.
    Receives market data and sends trading commands via TCP socket connection.
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 9090):
        """
        Initialize MQL Bridge Server
        
        Args:
            host: Server IP address (default: localhost)
            port: Server port (default: 9090)
        """
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.client_address: Optional[tuple] = None
        self.running = False
        self.connected = False
        
        # Data storage
        self.market_data: Optional[Dict] = None
        self.positions: List[Dict] = []
        self.last_heartbeat: Optional[datetime] = None
        self.rates_data: Optional[List[Dict]] = None
        
        # Message queues
        self.incoming_queue = queue.Queue()
        self.outgoing_queue = queue.Queue()
        
        # Callbacks
        self.on_market_data: Optional[Callable] = None
        self.on_position_update: Optional[Callable] = None
        self.on_heartbeat: Optional[Callable] = None
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        
        # Threading
        self.server_thread: Optional[threading.Thread] = None
        self.receiver_thread: Optional[threading.Thread] = None
        self.sender_thread: Optional[threading.Thread] = None
    
    def start(self) -> bool:
        """
        Start the bridge server and listen for connections
        
        Returns:
            True if server started successfully
        """
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            self.running = True
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.server_thread.start()
            
            print(f"✅ MQL Bridge Server started on {self.host}:{self.port}")
            print(f"   Waiting for MT4/MT5 EA connection...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start MQL Bridge Server: {e}")
            return False
    
    def stop(self):
        """Stop the bridge server and close connections"""
        print("\n🛑 Stopping MQL Bridge Server...")
        self.running = False
        
        # Close client connection
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        self.connected = False
        print("✅ MQL Bridge Server stopped")
    
    def _accept_connections(self):
        """Accept incoming EA connections (server thread)"""
        while self.running:
            try:
                if not self.server_socket:
                    break
                
                # Set timeout to check running flag periodically
                self.server_socket.settimeout(1.0)
                
                try:
                    client_socket, client_address = self.server_socket.accept()
                except socket.timeout:
                    continue
                
                print(f"\n🔗 EA Connected from {client_address}")
                
                # Close previous connection if exists
                if self.client_socket:
                    try:
                        self.client_socket.close()
                    except:
                        pass
                
                self.client_socket = client_socket
                self.client_address = client_address
                self.connected = True
                
                # Trigger connection callback
                if self.on_connect:
                    self.on_connect()
                
                # Start receiver and sender threads
                self.receiver_thread = threading.Thread(target=self._receive_messages, daemon=True)
                self.receiver_thread.start()
                
                self.sender_thread = threading.Thread(target=self._send_messages, daemon=True)
                self.sender_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"⚠️  Connection error: {e}")
                    time.sleep(1)
    
    def _receive_messages(self):
        """Receive messages from EA (receiver thread)"""
        buffer = ""
        
        while self.running and self.connected:
            try:
                if not self.client_socket:
                    break
                
                # Receive data
                data = self.client_socket.recv(4096)
                if not data:
                    # Connection closed
                    print("\n⚠️  EA disconnected")
                    self._handle_disconnect()
                    break
                
                # Decode and add to buffer
                buffer += data.decode('utf-8')
                
                # Process complete JSON messages (newline-delimited)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self._process_message(line.strip())
                
            except Exception as e:
                if self.running and self.connected:
                    print(f"⚠️  Receive error: {e}")
                    self._handle_disconnect()
                break
    
    def _send_messages(self):
        """Send messages to EA (sender thread)"""
        while self.running and self.connected:
            try:
                # Get message from queue with timeout
                message = self.outgoing_queue.get(timeout=0.5)
                
                if not self.client_socket:
                    break
                
                # Send message (JSON + newline)
                data = (message + '\n').encode('utf-8')
                self.client_socket.sendall(data)
                
            except queue.Empty:
                continue
            except Exception as e:
                if self.running and self.connected:
                    print(f"⚠️  Send error: {e}")
                    self._handle_disconnect()
                break
    
    def _process_message(self, message: str):
        """Process incoming JSON message from EA"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'market_data':
                self.market_data = data
                if self.on_market_data:
                    self.on_market_data(data)
            
            elif msg_type == 'position':
                # Update or add position
                ticket = data.get('ticket')
                existing = next((p for p in self.positions if p.get('ticket') == ticket), None)
                if existing:
                    self.positions[self.positions.index(existing)] = data
                else:
                    self.positions.append(data)
                
                if self.on_position_update:
                    self.on_position_update(data)
            
            elif msg_type == 'heartbeat':
                self.last_heartbeat = datetime.now()
                if self.on_heartbeat:
                    self.on_heartbeat(data)
            
            elif msg_type == 'order_result':
                # Order execution result
                self.incoming_queue.put(data)
            
            elif msg_type == 'response':
                # General response
                self.incoming_queue.put(data)
            
            elif msg_type == 'rates':
                # Historical rates data
                self.rates_data = data.get('data', [])
                self.incoming_queue.put(data)
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON: {e}")
        except Exception as e:
            print(f"⚠️  Message processing error: {e}")
    
    def _handle_disconnect(self):
        """Handle EA disconnection"""
        self.connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        self.client_address = None
        self.market_data = None
        self.positions = []
        
        # Trigger disconnect callback
        if self.on_disconnect:
            self.on_disconnect()
        
        print("   Waiting for EA to reconnect...")
    
    def send_command(self, command: Dict) -> Optional[Dict]:
        """
        Send command to EA and wait for response
        
        Args:
            command: Command dictionary (action, parameters)
            
        Returns:
            Response dictionary or None if timeout
        """
        if not self.connected:
            return {"success": False, "error": "Not connected to EA"}
        
        try:
            # Clear incoming queue
            while not self.incoming_queue.empty():
                try:
                    self.incoming_queue.get_nowait()
                except:
                    break
            
            # Send command
            message = json.dumps(command)
            self.outgoing_queue.put(message)
            
            # Wait for response (5 second timeout)
            try:
                response = self.incoming_queue.get(timeout=5.0)
                return response
            except queue.Empty:
                return {"success": False, "error": "Command timeout (no response)"}
        
        except Exception as e:
            return {"success": False, "error": f"Send command failed: {e}"}
    
    def buy_order(self, volume: float, sl: Optional[float] = None, 
                  tp: Optional[float] = None, comment: str = "Python Bridge") -> Dict:
        """
        Send BUY order command to EA
        
        Args:
            volume: Lot size
            sl: Stop Loss price (optional)
            tp: Take Profit price (optional)
            comment: Order comment
            
        Returns:
            Order result dictionary
        """
        command = {
            "action": "BUY",
            "volume": volume,
            "sl": sl if sl else 0,
            "tp": tp if tp else 0,
            "comment": comment
        }
        
        return self.send_command(command)
    
    def sell_order(self, volume: float, sl: Optional[float] = None,
                   tp: Optional[float] = None, comment: str = "Python Bridge") -> Dict:
        """
        Send SELL order command to EA
        
        Args:
            volume: Lot size
            sl: Stop Loss price (optional)
            tp: Take Profit price (optional)
            comment: Order comment
            
        Returns:
            Order result dictionary
        """
        command = {
            "action": "SELL",
            "volume": volume,
            "sl": sl if sl else 0,
            "tp": tp if tp else 0,
            "comment": comment
        }
        
        return self.send_command(command)
    
    def close_position(self, ticket: int) -> Dict:
        """
        Send CLOSE position command to EA
        
        Args:
            ticket: Position ticket number
            
        Returns:
            Close result dictionary
        """
        command = {
            "action": "CLOSE",
            "ticket": ticket
        }
        
        return self.send_command(command)
    
    def modify_position(self, ticket: int, sl: Optional[float] = None,
                       tp: Optional[float] = None) -> Dict:
        """
        Send MODIFY position command to EA
        
        Args:
            ticket: Position ticket number
            sl: New Stop Loss price (optional)
            tp: New Take Profit price (optional)
            
        Returns:
            Modify result dictionary
        """
        command = {
            "action": "MODIFY",
            "ticket": ticket,
            "sl": sl if sl else 0,
            "tp": tp if tp else 0
        }
        
        return self.send_command(command)
    
    def get_positions(self) -> Dict:
        """
        Request current positions from EA
        
        Returns:
            Response dictionary
        """
        command = {"action": "GET_POSITIONS"}
        return self.send_command(command)
    
    def get_rates(self, count: int = 100, timeframe: int = 15) -> Optional[List[Dict]]:
        """
        Request historical rates from EA
        
        Args:
            count: Number of bars (default: 100)
            timeframe: Timeframe in minutes (default: 15)
            
        Returns:
            List of rate dictionaries or None
        """
        command = {
            "action": "GET_RATES",
            "count": count,
            "timeframe": timeframe
        }
        
        response = self.send_command(command)
        if response and response.get('type') == 'rates':
            return response.get('data', [])
        return None
    
    def get_market_data(self) -> Optional[Dict]:
        """
        Get latest market data received from EA
        
        Returns:
            Market data dictionary or None
        """
        return self.market_data
    
    def get_current_price(self) -> tuple:
        """
        Get current bid and ask prices
        
        Returns:
            Tuple of (bid, ask) or (0, 0) if not available
        """
        if self.market_data:
            return (self.market_data.get('bid', 0), self.market_data.get('ask', 0))
        return (0, 0)
    
    def get_symbol_info(self) -> Optional[Dict]:
        """
        Get symbol information from latest market data
        
        Returns:
            Symbol info dictionary or None
        """
        if not self.market_data:
            return None
        
        return {
            'symbol': self.market_data.get('symbol'),
            'bid': self.market_data.get('bid'),
            'ask': self.market_data.get('ask'),
            'spread': self.market_data.get('spread'),
            'point': self.market_data.get('point'),
            'digits': self.market_data.get('digits'),
            'volume_min': self.market_data.get('min_lot'),
            'volume_max': self.market_data.get('max_lot'),
            'volume_step': self.market_data.get('lot_step'),
            'contract_size': self.market_data.get('contract_size')
        }
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Get account information from latest market data
        
        Returns:
            Account info dictionary or None
        """
        if not self.market_data:
            return None
        
        return {
            'balance': self.market_data.get('balance'),
            'equity': self.market_data.get('equity'),
            'margin': self.market_data.get('margin'),
            'free_margin': self.market_data.get('free_margin'),
            'profit': self.market_data.get('profit'),
            'leverage': self.market_data.get('leverage')
        }
    
    def is_connected(self) -> bool:
        """Check if bridge is connected to EA"""
        return self.connected
    
    def wait_for_connection(self, timeout: int = 30) -> bool:
        """
        Wait for EA to connect
        
        Args:
            timeout: Maximum seconds to wait (default: 30)
            
        Returns:
            True if connected, False if timeout
        """
        print(f"⏳ Waiting for EA connection (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.connected:
                print("✅ EA connected successfully!")
                return True
            time.sleep(0.5)
        
        print(f"⚠️  Connection timeout ({timeout}s)")
        return False


def main():
    """Example usage of MQL Bridge"""
    print("=" * 60)
    print("🌉 MQL Bridge Server - Example")
    print("=" * 60)
    
    # Create bridge
    bridge = MQLBridge(host='127.0.0.1', port=9090)
    
    # Set callbacks
    def on_market_data(data):
        print(f"\n📊 Market Data: {data['symbol']} | Bid: {data['bid']} | Ask: {data['ask']}")
    
    def on_connect():
        print("\n✅ EA connected!")
    
    def on_disconnect():
        print("\n⚠️  EA disconnected!")
    
    bridge.on_market_data = on_market_data
    bridge.on_connect = on_connect
    bridge.on_disconnect = on_disconnect
    
    # Start server
    if not bridge.start():
        return
    
    # Wait for connection
    if not bridge.wait_for_connection(timeout=60):
        print("\n❌ No EA connection - exiting")
        bridge.stop()
        return
    
    try:
        print("\n💡 Bridge is running. Press Ctrl+C to stop.")
        print("   Market data will be displayed as it arrives...")
        
        while True:
            time.sleep(1)
            
            # Example: Display account info every 10 seconds
            if int(time.time()) % 10 == 0:
                account = bridge.get_account_info()
                if account:
                    print(f"\n💰 Account: Balance=${account['balance']:.2f} | Equity=${account['equity']:.2f}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    
    finally:
        bridge.stop()


if __name__ == "__main__":
    main()
