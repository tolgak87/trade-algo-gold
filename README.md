# 📈 Gold Trading Bot

An automated trading system for gold (XAUUSD) using MetaTrader5 API with risk/reward ratio management.

**I trade Gold only for LONG**, so in this code, I will focus to LONG, not SHORT for gold.

## 🚀 Features

---

## 📋 Requirements

**Note**: MetaTrader5 Python module works only on **Windows**

```bash
pip install MetaTrader5
```

## 🛠️ Installation

1. **Install MetaTrader5 on Windows**
   - Download from: https://www.metatrader5.com/en/download

2. **Open MetaTrader5 and create/login to demo account**
   - The MT5 module automatically detects the active MT5 application
   - MT5 must be opened and logged in before running the Python code

3. **Install Python dependencies**
   ```bash
   pip install MetaTrader5
   ```

## 🏗️ Project Structure

```
Trader/
├── app.py                 # Main entry point
├── account_info.json      # Account data (auto-generated)
├── logs/
---
---
---
---

```

## 🎯 Usage

### Basic Trading

```python
from src.trade_gold import GoldTrader

trader = GoldTrader()

# Connect to MT5
if trader.connect():
    # Find gold symbol
    symbol = trader.find_gold_symbol()
    
    # Get current price
    price = trader.get_current_price()
    print(f"{symbol} price: {price}")
    
    # Execute BUY trade with 1:2 risk/reward
    trader.buy_with_risk_reward(volume=0.1, risk_usd=3.0, rr_ratio=2.0)
    
    # Or execute SELL trade
    # trader.sell_with_risk_reward(volume=0.1, risk_usd=3.0, rr_ratio=2.0)
    
    trader.disconnect()
```

### Run the Application

```bash
python app.py
```

## 🔧 Configuration

### Trade Parameters

- `volume`: Trade volume (default: 0.1 lots)
- `risk_usd`: Risk amount in USD (default: 3.0)
- `rr_ratio`: Risk/Reward ratio (default: 2.0)

### Risk Management

The bot automatically calculates Stop Loss (SL) and Take Profit (TP) based on:
- **BUY**: SL = Entry - Risk, TP = Entry + (Risk × RR Ratio)
- **SELL**: SL = Entry + Risk, TP = Entry - (Risk × RR Ratio)

## 📊 Account Information

Get detailed account information:

```python
from src.mt5_client import MT5Client

client = MT5Client()
if client.connect():
    account = client.get_account_info()
    account.print_pretty()  # Formatted output
    account.to_json_file()  # Save to JSON
```

## 📝 Trade Logging

All trades are automatically logged to `logs/trades.json` with:
- Timestamp
- Action (BUY/SELL)
- Symbol
- Entry price
- Stop Loss
- Take Profit
- Volume
- Risk/Reward ratio
- Execution result

## ⚠️ Disclaimer

This is a trading bot that executes real trades. Use at your own risk. Always test with a demo account first.

