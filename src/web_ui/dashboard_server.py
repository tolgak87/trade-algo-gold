"""
Real-time Web Dashboard Server for Gold Trading Bot
Uses Flask + SocketIO for live trading monitoring interface
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from typing import Dict, Optional, List
from datetime import datetime
import json
import threading


class DashboardServer:
    """
    WebSocket-based dashboard server for real-time trading monitoring
    Provides live updates of positions, signals, SAR values, and account info
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """
        Initialize dashboard server
        
        Args:
            host: Server host address (default: localhost)
            port: Server port (default: 5000)
            debug: Enable Flask debug mode
        """
        self.host = host
        self.port = port
        self.debug = debug
        
        # Flask app setup
        self.app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='static')
        self.app.config['SECRET_KEY'] = 'gold-trading-bot-secret-2025'
        
        # SocketIO setup with threading
        self.socketio = SocketIO(self.app, 
                                 cors_allowed_origins="*",
                                 async_mode='threading')
        
        # Dashboard state
        self.current_state = {
            'bot_status': 'Initializing',
            'account': {},
            'position': None,
            'sar_data': {},
            'signal': {},
            'last_trades': [],
            'price_history': [],
            'timestamp': datetime.now().isoformat()
        }
        
        self.server_thread = None
        self.is_running = False
        
        # Setup routes
        self._setup_routes()
        self._setup_socketio_events()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/state')
        def get_state():
            """Get current dashboard state (REST API fallback)"""
            return json.dumps(self.current_state)
    
    def _setup_socketio_events(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Client connected to dashboard"""
            print(f"🌐 Dashboard client connected")
            # Send current state immediately
            emit('state_update', self.current_state)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Client disconnected from dashboard"""
            print(f"🔌 Dashboard client disconnected")
        
        @self.socketio.on('request_state')
        def handle_request_state():
            """Client requests current state"""
            emit('state_update', self.current_state)
    
    def start(self):
        """
        Start dashboard server in background thread
        Non-blocking - allows trading bot to continue running
        """
        if self.is_running:
            print("⚠️  Dashboard server already running")
            return
        
        def run_server():
            print(f"\n{'='*60}")
            print(f"🌐 DASHBOARD SERVER STARTING")
            print(f"{'='*60}")
            print(f"📊 Access dashboard at: http://{self.host}:{self.port}")
            print(f"🔄 Real-time updates enabled via WebSocket")
            print(f"{'='*60}\n")
            
            self.socketio.run(self.app, 
                             host=self.host, 
                             port=self.port, 
                             debug=self.debug,
                             use_reloader=False,
                             allow_unsafe_werkzeug=True)
        
        self.is_running = True
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
    
    def stop(self):
        """Stop dashboard server"""
        if self.is_running:
            print("🛑 Stopping dashboard server...")
            self.is_running = False
    
    # ===== Real-time Update Methods =====
    
    def update_bot_status(self, status: str):
        """
        Update bot status
        
        Args:
            status: Bot status message (e.g., "Waiting for signal", "Position open")
        """
        self.current_state['bot_status'] = status
        self.current_state['timestamp'] = datetime.now().isoformat()
        self._broadcast('status_update', {'status': status})
    
    def update_account_info(self, account_data: Dict):
        """
        Update account information
        
        Args:
            account_data: Dict with balance, equity, margin, etc.
        """
        self.current_state['account'] = {
            'balance': account_data.get('balance', 0),
            'equity': account_data.get('equity', 0),
            'margin': account_data.get('margin', 0),
            'free_margin': account_data.get('free_margin', 0),
            'margin_level': account_data.get('margin_level', 0),
            'profit': account_data.get('profit', 0)
        }
        self._broadcast('account_update', self.current_state['account'])
    
    def update_position(self, position_data: Optional[Dict]):
        """
        Update current position
        
        Args:
            position_data: Dict with position details or None if no position
        """
        if position_data:
            self.current_state['position'] = {
                'ticket': position_data.get('ticket'),
                'type': position_data.get('type'),
                'symbol': position_data.get('symbol'),
                'volume': position_data.get('volume'),
                'entry_price': position_data.get('entry_price'),
                'current_price': position_data.get('current_price'),
                'stop_loss': position_data.get('stop_loss'),
                'take_profit': position_data.get('take_profit'),
                'profit': position_data.get('profit', 0),
                'duration': position_data.get('duration', '0:00:00')
            }
        else:
            self.current_state['position'] = None
        
        self._broadcast('position_update', self.current_state['position'])
    
    def update_sar_data(self, sar_data: Dict):
        """
        Update Parabolic SAR indicator data
        
        Args:
            sar_data: Dict with SAR value, trend, signal
        """
        self.current_state['sar_data'] = {
            'sar_value': sar_data.get('sar_value', 0),
            'trend': sar_data.get('trend', 'Unknown'),
            'signal': sar_data.get('signal', 'HOLD'),
            'distance': sar_data.get('distance', 0),
            'acceleration': sar_data.get('acceleration', 0.02)
        }
        self._broadcast('sar_update', self.current_state['sar_data'])
    
    def update_signal(self, signal_data: Dict):
        """
        Update current trading signal
        
        Args:
            signal_data: Dict with signal type, reason, timestamp
        """
        self.current_state['signal'] = {
            'type': signal_data.get('type', 'HOLD'),
            'reason': signal_data.get('reason', ''),
            'timestamp': signal_data.get('timestamp', datetime.now().isoformat())
        }
        self._broadcast('signal_update', self.current_state['signal'])
    
    def add_trade(self, trade_data: Dict):
        """
        Add completed trade to history
        
        Args:
            trade_data: Dict with trade details (entry, exit, profit, etc.)
        """
        trade = {
            'ticket': trade_data.get('ticket'),
            'type': trade_data.get('type'),
            'entry_price': trade_data.get('entry_price'),
            'close_price': trade_data.get('close_price'),
            'volume': trade_data.get('volume'),
            'profit': trade_data.get('profit'),
            'duration': trade_data.get('duration'),
            'close_reason': trade_data.get('close_reason'),
            'timestamp': trade_data.get('timestamp', datetime.now().isoformat())
        }
        
        # Keep only last 20 trades
        self.current_state['last_trades'].insert(0, trade)
        self.current_state['last_trades'] = self.current_state['last_trades'][:20]
        
        self._broadcast('trade_added', trade)
    
    def add_price_point(self, price: float, sar_value: float):
        """
        Add price point to chart history
        
        Args:
            price: Current price
            sar_value: Current SAR value
        """
        point = {
            'timestamp': datetime.now().isoformat(),
            'price': price,
            'sar': sar_value
        }
        
        # Keep only last 100 points (for chart performance)
        self.current_state['price_history'].append(point)
        self.current_state['price_history'] = self.current_state['price_history'][-100:]
        
        self._broadcast('price_update', point)
    
    def send_notification(self, message: str, notification_type: str = 'info'):
        """
        Send notification to dashboard
        
        Args:
            message: Notification message
            notification_type: Type ('success', 'error', 'warning', 'info')
        """
        notification = {
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now().isoformat()
        }
        self._broadcast('notification', notification)
    
    def _broadcast(self, event: str, data: any):
        """
        Broadcast data to all connected clients
        
        Args:
            event: Event name
            data: Data to send
        """
        if self.is_running:
            try:
                self.socketio.emit(event, data)
            except Exception as e:
                print(f"⚠️  Failed to broadcast {event}: {e}")
    
    def get_url(self) -> str:
        """Get dashboard URL"""
        return f"http://{self.host}:{self.port}"


# Singleton instance for easy access across modules
_dashboard_instance: Optional[DashboardServer] = None


def get_dashboard() -> Optional[DashboardServer]:
    """Get global dashboard instance"""
    return _dashboard_instance


def initialize_dashboard(host: str = '127.0.0.1', port: int = 5000) -> DashboardServer:
    """
    Initialize and start global dashboard instance
    
    Args:
        host: Server host
        port: Server port
        
    Returns:
        DashboardServer instance
    """
    global _dashboard_instance
    
    if _dashboard_instance is None:
        _dashboard_instance = DashboardServer(host=host, port=port)
        _dashboard_instance.start()
    
    return _dashboard_instance
