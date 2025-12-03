# Gold Trading Bot - MQL Bridge Version 🌉

## Broker-Agnostic Trading System

This is a **completely broker-independent** trading system that works with **any MT4 or MT5 broker** without Python having direct access to MetaTrader APIs.

### 🎯 Key Features

- ✅ **No MetaTrader5 Python module** - Pure socket communication
- ✅ **Works with MT4 AND MT5** - Single Python codebase
- ✅ **Any broker** - Not tied to specific broker APIs
- ✅ **Network isolation** - Python doesn't need MetaTrader installed
- ✅ **Parabolic SAR** - Professional trend-following strategy
- ✅ **Risk Management** - 1:2 risk-reward ratio
- ✅ **Circuit Breaker** - Automatic loss protection
- ✅ **Trade Logging** - Complete trade history

---

## 📐 Architecture

```
┌─────────────────┐         Socket (TCP)          ┌──────────────────┐
│                 │  ◄─────────────────────────►  │                  │
│  MetaTrader     │     JSON Messages             │  Python Bot      │
│  (MT4/MT5)      │  ◄─────────────────────────►  │  (app_bridge.py) │
│                 │                               │                  │
│ ┌─────────────┐ │                               │ ┌──────────────┐ │
│ │ PythonBridge│ │                               │ │ MQLBridge    │ │
│ │ EA (MQL)    │ │                               │ │ Server       │ │
│ └─────────────┘ │                               │ └──────────────┘ │
└─────────────────┘                               └──────────────────┘
   Your Broker                                      Localhost:9090
```

### Communication Flow:

1. **EA → Python**: Market data (bid, ask, account info) every tick
2. **Python → EA**: Trading commands (BUY, SELL, CLOSE, MODIFY)
3. **EA → Python**: Order execution results
4. **Python ↔ EA**: Heartbeat every 5 seconds

---

## 🚀 Quick Start

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

**Note**: `MetaTrader5` module is NOT required anymore!

### 2. Install MetaTrader Expert Advisor

#### For MT5:
1. Copy `mql/PythonBridge_MT5.mq5` to `MetaTrader5/MQL5/Experts/`
2. Open MetaEditor (F4 in MT5)
3. Open `PythonBridge_MT5.mq5`
4. Compile (F7) - Should show "0 errors"
5. Drag EA onto XAUUSD chart

#### For MT4:
1. Copy `mql/PythonBridge_MT4.mq4` to `MetaTrader4/MQL4/Experts/`
2. Open MetaEditor (F4 in MT4)
3. Open `PythonBridge_MT4.mq4`
4. Compile (F7)
5. Drag EA onto XAUUSD chart

**See `mql/INSTALLATION_MT5.md` for detailed setup guide**

### 3. Start Trading Bot

```powershell
python app_bridge.py
```

The bot will:
1. Start MQL Bridge Server on `localhost:9090`
2. Wait for EA connection (60 seconds timeout)
3. Detect trading symbol from EA
4. Initialize trading components
5. Show main menu for manual/auto trading

---

## 📋 Configuration

Edit `src/configs/trade_config.json`:

```json
{
    "trading": {
        "desired_signal": "BOTH",
        "risk_percentage": 1.0,
        "signal_check_interval": 5,
        "position_check_interval": 5
    },
    "symbols": {
        "priority_list": ["XAUUSD", "XAUUSD.", "GOLD"]
    }
}
```

### Parameters:

- **desired_signal**: `"BUY"`, `"SELL"`, or `"BOTH"` (trade both directions)
- **risk_percentage**: Risk per trade (1% = $100 risk on $10,000 account)
- **signal_check_interval**: Seconds between signal checks
- **position_check_interval**: Seconds between position monitoring
- **priority_list**: Symbols to search for (uses EA's symbol)

---

## 🎛️ Trading Modes

### 1. Full Auto-Trading Cycle

```python
# Automatically:
# - Wait for SAR signal
# - Execute trade with risk management
# - Monitor position with SAR reversal detection
# - Close on SAR reversal, SL, or TP
# - Repeat cycle
```

### 2. Manual Trading

Execute single BUY or SELL orders via menu with automatic:
- Position sizing based on risk percentage
- SAR-based Stop Loss
- 1:2 Risk-Reward Take Profit

### 3. Signal Waiting

Wait for specific Parabolic SAR signal before trading.

---

## 🛡️ Safety Features

### Circuit Breaker Protection

Automatically pauses trading when:
- **5 consecutive losses** → 30-minute pause
- **70% losses in last 10 trades** → 60-minute pause
- **5% daily loss** → Paused until next day

### SAR Reversal Detection

Monitors open positions and closes immediately when:
- Uptrend changes to downtrend (BUY position)
- Downtrend changes to uptrend (SELL position)

### Emergency Stop Loss

Force closes position if price breaks stop loss but MT5/MT4 didn't trigger.

---

## 📊 File Structure

```
trade-algo-gold/
├── app_bridge.py                      # Main application (NEW - bridge version)
├── mql/
│   ├── PythonBridge_MT5.mq5          # MT5 Expert Advisor
│   ├── PythonBridge_MT4.mq4          # MT4 Expert Advisor
│   ├── README.md                      # Bridge protocol docs
│   └── INSTALLATION_MT5.md            # Setup guide
├── src/
│   ├── mql_bridge.py                  # Socket server (NEW)
│   ├── symbol_detector_bridge.py      # Config-based detector (NEW)
│   ├── collect_account_info_bridge.py # Bridge account collector (NEW)
│   ├── order_executor.py              # Bridge-based executor (UPDATED)
│   ├── parabolic_sar.py               # Bridge-based SAR (UPDATED)
│   ├── risk_manager.py                # Risk calculations
│   ├── trade_logger.py                # JSON trade logging
│   ├── circuit_breaker.py             # Loss protection
│   ├── email_notifier.py              # Email alerts
│   └── configs/
│       └── trade_config.json          # Trading parameters
├── logs/
│   ├── account_info.json              # Account snapshot
│   └── trade_logs/                    # Daily trade logs
└── requirements.txt                    # Python dependencies (NO MT5!)
```

---

## 🔧 Troubleshooting

### EA not connecting?

1. **Check EA is running**: Look for 😊 icon on chart
2. **Check port**: Make sure port 9090 is not blocked
3. **Check firewall**: Allow Python to accept connections
4. **Check EA logs**: Open MT5/MT4 Experts tab for errors

### "Bridge not connected" errors?

- EA must be running BEFORE starting Python bot
- Or EA will auto-reconnect if Python starts later

### Position not closing?

- Check MT5/MT4 Experts tab for error messages
- Verify AutoTrading is enabled (EA settings)
- Check account has sufficient margin

---

## 📈 Strategy: Parabolic SAR

### How it works:

1. **Uptrend**: SAR dots below price → BUY signal
2. **Downtrend**: SAR dots above price → SELL signal
3. **Reversal**: SAR switches sides → Close position

### Parameters:

- **Acceleration**: 0.02 (how fast SAR moves)
- **Maximum**: 0.2 (maximum acceleration)
- **Timeframe**: 15 minutes

### Stop Loss:

- BUY: Current SAR value (below price)
- SELL: Current SAR value (above price)
- **Trailing**: SAR updates every bar

---

## 🆚 Comparison: Old vs New

| Feature | Old System | New Bridge System |
|---------|-----------|------------------|
| Python Module | MetaTrader5 | ❌ None |
| MT4 Support | ❌ No | ✅ Yes |
| MT5 Support | ✅ Yes | ✅ Yes |
| Broker Lock-in | ✅ Yes | ❌ No |
| Network Install | Required | Not Required |
| Communication | API Calls | Socket/Files |
| Data Flow | Polling | Real-time Stream |

---

## 📝 Example Session

```
[1/5] Starting MQL Bridge Server...
✅ MQL Bridge Server started on 127.0.0.1:9090
   Waiting for MT4/MT5 EA connection...

[2/5] Waiting for MT4/MT5 EA connection...

🔗 EA Connected from ('127.0.0.1', 54321)

[3/5] Detecting trading symbol...
✅ Symbol from EA: XAUUSD

[4/5] Collecting account information...
✅ Account information collected successfully
   Balance: $10000.00
   Leverage: 1:100

[5/5] Initializing Trading Bot...
✅ Bot Ready!

🎛️  TRADING BOT MENU
1. 🚀 Start Full Auto-Trading Cycle
2. 📊 Refresh Market Data
...
```

---

## 🤝 Contributing

This is the **broker-agnostic future** of algorithmic trading!

### Key Benefits:

1. **One Python codebase** for MT4 AND MT5
2. **Any broker** without API dependencies
3. **Network isolation** - Python can run anywhere
4. **Easy debugging** - JSON protocol is human-readable
5. **Future-proof** - Not tied to MetaTrader Python module versions

---

## 📄 License

This project is for educational purposes. **Trade at your own risk.**

---

## ⚠️ Disclaimer

- This bot uses **real money** - test on demo account first
- Past performance does not guarantee future results
- Parabolic SAR can produce false signals in ranging markets
- Always monitor your trades
- Use appropriate risk management (1-2% per trade recommended)

---

## 🔗 Related Files

- `mql/README.md` - Bridge protocol specification
- `mql/INSTALLATION_MT5.md` - Step-by-step EA installation
- `src/configs/trade_config.json` - Trading parameters
- `logs/trade_logs/` - Historical trade data

---

**Happy Trading! 📈**
