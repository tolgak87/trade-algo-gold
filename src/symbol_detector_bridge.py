"""
Symbol Detector - Config-based (Bridge Compatible)
Detects trading symbol from configuration priority list
"""

import json
from typing import Optional


class SymbolDetector:
    """
    Detects available trading symbol from configuration file.
    Works with MQL Bridge - no MT5 module dependency.
    """
    
    def __init__(self, config_path: str = "src/configs/trade_config.json"):
        """
        Initialize Symbol Detector with configuration file
        
        Args:
            config_path: Path to trade configuration JSON file
        """
        self.config_path = config_path
        self.detected_symbol: Optional[str] = None
        self.priority_list = []
        self._load_config()
    
    def _load_config(self):
        """Load symbol priority list from configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.priority_list = config.get('symbols', {}).get('priority_list', [])
                
                if not self.priority_list:
                    print("⚠️  No symbols defined in config, using default")
                    self.priority_list = ['XAUUSD', 'XAUUSD.', 'GOLD']
        
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {self.config_path}")
            self.priority_list = ['XAUUSD', 'XAUUSD.', 'GOLD']
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON in config: {e}")
            self.priority_list = ['XAUUSD', 'XAUUSD.', 'GOLD']
    
    def detect_symbol(self, bridge=None) -> Optional[str]:
        """
        Detect available trading symbol from priority list.
        If bridge provided, validates symbol is available from EA.
        Otherwise returns first symbol from config.
        
        Args:
            bridge: Optional MQLBridge instance for validation
            
        Returns:
            Detected symbol or None if not found
        """
        if not self.priority_list:
            print("❌ No symbols in priority list")
            return None
        
        # If bridge provided, use EA's symbol
        if bridge and bridge.is_connected():
            market_data = bridge.get_market_data()
            if market_data and market_data.get('symbol'):
                self.detected_symbol = market_data['symbol']
                print(f"✅ Symbol from EA: {self.detected_symbol}")
                return self.detected_symbol
        
        # Otherwise use first symbol from config
        self.detected_symbol = self.priority_list[0]
        print(f"✅ Symbol from config: {self.detected_symbol}")
        print(f"   Priority list: {', '.join(self.priority_list)}")
        
        return self.detected_symbol
    
    def get_symbol(self) -> Optional[str]:
        """
        Get the detected symbol
        
        Returns:
            Detected symbol or None
        """
        return self.detected_symbol


def main():
    """Example usage of Symbol Detector"""
    print("=" * 60)
    print("Symbol Detector - Config Based")
    print("=" * 60)
    
    # Create detector
    detector = SymbolDetector()
    
    # Detect symbol (without bridge - uses config)
    symbol = detector.detect_symbol()
    
    if symbol:
        print(f"\n✅ Selected symbol: {symbol}")
    else:
        print("\n❌ No symbol found")
    
    print("\n💡 To validate with EA, pass MQLBridge instance to detect_symbol()")


if __name__ == "__main__":
    main()
