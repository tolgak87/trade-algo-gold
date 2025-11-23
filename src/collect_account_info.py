import MetaTrader5 as mt5
import json
from datetime import datetime

def collect_account_info():
    """
    Initialize MT5 connection and collect account information to JSON file.
    """
    # Initialize MT5 connection
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return False
    
    print("MT5 initialized successfully")
    
    # Get account info
    info = mt5.account_info()
    
    if info is None:
        print(f"Failed to get account info, error code = {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    # Prepare account data dictionary
    account_data = {
        "login": info.login,
        "trade_mode": info.trade_mode,
        "leverage": info.leverage,
        "balance": info.balance,
        "equity": info.equity,
        "trade_allowed": info.trade_allowed,
        "server": info.server,
        "currency": info.currency,
        "company": info.company,
        "margin_level": info.margin_level,
        "profit": info.profit,
        "margin_free": info.margin_free,
        "collected_at": datetime.now().isoformat()
    }
    
    # Save to JSON file
    try:
        with open('account_info.json', 'w', encoding='utf-8') as f:
            json.dump(account_data, f, indent=4, ensure_ascii=False)
        print("Account information saved to account_info.json")
        print(f"\nAccount Summary:")
        print(f"Login: {account_data['login']}")
        print(f"Server: {account_data['server']}")
        print(f"Balance: {account_data['balance']} {account_data['currency']}")
        print(f"Equity: {account_data['equity']} {account_data['currency']}")
        print(f"Profit: {account_data['profit']} {account_data['currency']}")
        print(f"Margin Free: {account_data['margin_free']} {account_data['currency']}")
        print(f"Leverage: 1:{account_data['leverage']}")
        
    except Exception as e:
        print(f"Error saving account info: {e}")
        mt5.shutdown()
        return False
    
    # Shutdown MT5 connection
    mt5.shutdown()
    print("\nMT5 connection closed")
    return True

if __name__ == "__main__":
    collect_account_info()
