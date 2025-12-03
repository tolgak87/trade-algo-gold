"""
Account Info Collector - Bridge Version
Collects account information via MQL Bridge
"""

import json
from datetime import datetime
import os


def collect_account_info(bridge) -> bool:
    """
    Collect account information via MQL Bridge and save to JSON.
    
    Args:
        bridge: MQLBridge instance
        
    Returns:
        True if successful, False otherwise
    """
    print("\n📊 Collecting Account Information via Bridge...")
    
    if not bridge.is_connected():
        print("❌ Bridge not connected to EA")
        return False
    
    # Get account info from bridge
    account_info = bridge.get_account_info()
    
    if not account_info:
        print("❌ No account information available")
        return False
    
    # Prepare account data
    account_data = {
        "balance": account_info.get('balance', 0),
        "equity": account_info.get('equity', 0),
        "margin": account_info.get('margin', 0),
        "free_margin": account_info.get('free_margin', 0),
        "profit": account_info.get('profit', 0),
        "leverage": account_info.get('leverage', 0),
        "collected_at": datetime.now().isoformat()
    }
    
    # Create logs directory if not exists
    os.makedirs('logs', exist_ok=True)
    
    # Save to file
    try:
        with open('logs/account_info.json', 'w', encoding='utf-8') as f:
            json.dump(account_data, f, indent=4, ensure_ascii=False)
        
        print("✅ Account information collected successfully")
        print(f"   Balance: ${account_data['balance']:.2f}")
        print(f"   Equity: ${account_data['equity']:.2f}")
        print(f"   Leverage: 1:{account_data['leverage']}")
        print(f"   Saved to: logs/account_info.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save account info: {e}")
        return False


def main():
    """Example usage"""
    from mql_bridge import MQLBridge
    
    print("=" * 60)
    print("Account Info Collector - Bridge Version")
    print("=" * 60)
    
    # Create and start bridge
    bridge = MQLBridge(host='127.0.0.1', port=9090)
    if not bridge.start():
        print("❌ Failed to start bridge")
        return
    
    # Wait for connection
    if not bridge.wait_for_connection(timeout=30):
        print("❌ No EA connection")
        bridge.stop()
        return
    
    # Collect account info
    success = collect_account_info(bridge)
    
    if not success:
        print("\n❌ Failed to collect account information")
    
    # Stop bridge
    bridge.stop()


if __name__ == "__main__":
    main()
