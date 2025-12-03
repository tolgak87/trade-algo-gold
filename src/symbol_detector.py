import MetaTrader5 as mt5
from typing import Optional, List
import json
import os

class SymbolDetector:
    """
    Auto-detection of trading symbols in MetaTrader 5.
    Supports multiple symbol variations loaded from config.
    """
    
    def __init__(self, symbols_list: Optional[List[str]] = None):
        """
        Initialize symbol detector.
        
        Args:
            symbols_list: Optional list of symbols to search for.
                         If None, loads from config file.
        """
        if symbols_list is None:
            symbols_list = self._load_symbols_from_config()
        
        self.SYMBOLS = symbols_list
    
        self.detected_symbol: Optional[str] = None
        self.available_symbols: List[str] = []
    
    def _load_symbols_from_config(self) -> List[str]:
        """
        Load symbol priority list from config file.
        
        Returns:
            List[str]: List of symbols in priority order
        """
        try:
            # Get project root (go up 2 levels from src/symbol_detector.py)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, 'configs', 'trade_config.json')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                symbols = config.get('symbols', {}).get('priority_list', [])
                
                if symbols:
                    print(f"✅ Loaded {len(symbols)} symbols from config: {', '.join(symbols)}")
                    return symbols
                else:
                    print("⚠️  No symbols found in config, using defaults")
                    return self._get_default_symbols()
        except Exception as e:
            print(f"⚠️  Failed to load symbols from config: {e}")
            print("   Using default gold symbols...")
            return self._get_default_symbols()
    
    def _get_default_symbols(self) -> List[str]:
        """
        Get default gold symbols as fallback.
        
        Returns:
            List[str]: Default gold symbol list
        """
        return [
            "XAUUSD",
            "XAUUSD.",
            "XAUUSD.m",
            "GOLD",
            "GOLD."
        ]
    
    def detect_symbol(self) -> Optional[str]:
        """
        Automatically detect which symbol is available in the MT5 account.
        
        Returns:
            str: The detected symbol name, or None if not found
        """
        if not mt5.initialize():
            print(f"MT5 initialization failed, error code = {mt5.last_error()}")
            return None
        
        # Get all available symbols
        all_symbols = mt5.symbols_get()
        if all_symbols is None:
            print("Failed to get symbols list")
            mt5.shutdown()
            return None
        
        # Create a set of available symbol names for faster lookup
        available_symbol_names = {symbol.name for symbol in all_symbols}
        
        # Check each symbol variant in priority order
        for symbol in self.SYMBOLS:
            if symbol in available_symbol_names:
                self.available_symbols.append(symbol)
        
        if not self.available_symbols:
            print(f"❌ None of the configured symbols found in your MT5 account")
            print(f"   Searched for: {', '.join(self.SYMBOLS)}")
            mt5.shutdown()
            return None
        
        # Select the first available symbol as default
        self.detected_symbol = self.available_symbols[0]
        
        # Enable the symbol for trading
        if not mt5.symbol_select(self.detected_symbol, True):
            print(f"Failed to select symbol {self.detected_symbol}")
            mt5.shutdown()
            return None
        
        # Get symbol info
        symbol_info = mt5.symbol_info(self.detected_symbol)
        
        return self.detected_symbol
    
    def detect_gold_symbol(self) -> Optional[str]:
        """
        Backward compatibility method.
        Calls detect_symbol().
        
        Returns:
            str: The detected symbol name, or None if not found
        """
        return self.detect_symbol()
    
    def get_all_available_symbols(self) -> List[str]:
        """
        Get list of all available symbols.
        
        Returns:
            List[str]: List of available symbol names
        """
        return self.available_symbols
    
    def get_all_available_gold_symbols(self) -> List[str]:
        """
        Backward compatibility method.
        Get list of all available symbols.
        
        Returns:
            List[str]: List of available symbol names
        """
        return self.available_symbols
    
    def get_symbol_info(self, symbol: Optional[str] = None) -> Optional[dict]:
        """
        Get detailed information about a specific gold symbol.
        
        Args:
            symbol: Symbol name (uses detected symbol if None)
            
        Returns:
            dict: Symbol information or None if not found
        """
        symbol_name = symbol or self.detected_symbol
        
        if not symbol_name:
            print("No symbol specified and no symbol detected")
            return None
        
        if not mt5.initialize():
            print(f"MT5 initialization failed")
            return None
        
        symbol_info = mt5.symbol_info(symbol_name)
        
        if symbol_info is None:
            print(f"Symbol {symbol_name} not found")
            mt5.shutdown()
            return None
        
        info_dict = {
            "name": symbol_info.name,
            "bid": symbol_info.bid,
            "ask": symbol_info.ask,
            "spread": symbol_info.spread,
            "digits": symbol_info.digits,
            "point": symbol_info.point,
            "volume_min": symbol_info.volume_min,
            "volume_max": symbol_info.volume_max,
            "volume_step": symbol_info.volume_step,
            "trade_contract_size": symbol_info.trade_contract_size,
            "trade_mode": symbol_info.trade_mode,
            "description": symbol_info.description,
            "currency_base": symbol_info.currency_base,
            "currency_profit": symbol_info.currency_profit,
            "currency_margin": symbol_info.currency_margin
        }
        
        mt5.shutdown()
        return info_dict
    
    def verify_symbol_tradeable(self, symbol: Optional[str] = None) -> bool:
        """
        Verify if a symbol is available and tradeable.
        
        Args:
            symbol: Symbol name (uses detected symbol if None)
            
        Returns:
            bool: True if symbol is tradeable, False otherwise
        """
        symbol_name = symbol or self.detected_symbol
        
        if not symbol_name:
            return False
        
        if not mt5.initialize():
            return False
        
        symbol_info = mt5.symbol_info(symbol_name)
        
        if symbol_info is None:
            mt5.shutdown()
            return False
        
        # Check if symbol is visible and tradeable
        is_tradeable = (
            symbol_info.visible and
            symbol_info.trade_mode in [mt5.SYMBOL_TRADE_MODE_FULL, mt5.SYMBOL_TRADE_MODE_LONGONLY, mt5.SYMBOL_TRADE_MODE_SHORTONLY]
        )
        
        mt5.shutdown()
        return is_tradeable


def main():
    """
    Example usage of SymbolDetector
    """
    # Load symbols from config (default behavior)
    detector = SymbolDetector()
    
    # Or specify custom symbols
    # detector = SymbolDetector(symbols_list=["EURUSD", "GBPUSD", "USDJPY"])
    
    # Detect symbol
    detected = detector.detect_symbol()
    
    if detected:
        print(f"\n✅ Successfully detected symbol: {detected}")
        
        # Verify if tradeable
        if detector.verify_symbol_tradeable():
            print(f"✅ {detected} is tradeable")
        else:
            print(f"⚠️ {detected} is not tradeable")
        
        # Get all available symbols
        all_available = detector.get_all_available_symbols()
        if len(all_available) > 1:
            print(f"\nℹ️ Other available symbols: {', '.join(all_available[1:])}")
    else:
        print("\n❌ Failed to detect symbol")
    
    mt5.shutdown()


if __name__ == "__main__":
    main()
