# 📈 Gold Trading Bot

An automated trading system for gold (XAUUSD) using MetaTrader5 with Parabolic SAR indicator, real-time web dashboard, and email notifications.

## 🚀 Features

- ✅ **MetaTrader5 Integration**: Seamless connection to MT5 for live trading
- ✅ **Parabolic SAR Indicator**: 15-minute timeframe trend analysis
- ✅ **Dynamic Stop Loss**: SAR-based adaptive risk management
- ✅ **Trailing Stop Loss**: Automatic profit protection as price moves favorably
- ✅ **BUY/SELL Support**: Full support for both long and short positions
- ✅ **Emergency SL Monitor**: Code-level protection against slippage
- ✅ **SAR Reversal Detection**: Automatic position closure on trend change
- ✅ **🌐 Real-time Web Dashboard**: Beautiful localhost dashboard for live monitoring
- ✅ **📧 Email Notifications**: Instant alerts when positions close
- ✅ **Automated Trading Loop**: Continuous operation with signal detection
- ✅ **Risk Management**: Configurable risk-reward ratios (default 1:2)
- ✅ **Trade Logging**: Complete JSON-based trade history

---

## 📋 Requirements

**Note**: MetaTrader5 Python module works only on **Windows**

## 🛠️ Installation

1. **Install MetaTrader5 on Windows**
   - Download from: https://www.metatrader5.com/en/download

2. **Open MetaTrader5 and create/login to demo account**
   - The MT5 module automatically detects the active MT5 application
   - MT5 must be opened and logged in before running the Python code

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Email Notifications (Optional)**
   - Edit `email_credentials.json` with your Gmail credentials
   - See email setup instructions in the file

---

## 🏗️ Project Structure

```
trade-algo-gold/
├── app.py                      # Basic launcher (terminal only)
├── dashboard_app.py            # Dashboard launcher (recommended)
├── requirements.txt            # Python dependencies
│
├── src/
│   ├── trading_bot.py          # Main TradingBot class
│   ├── dashboard_server.py     # Real-time WebSocket server
│   ├── parabolic_sar.py        # SAR indicator
│   ├── order_executor.py       # Order execution
│   ├── risk_manager.py         # Risk calculations
│   ├── email_notifier.py       # Email alerts
│   ├── symbol_detector.py      # Gold symbol detection
│   └── trade_logger.py         # Trade logging
│
├── templates/
│   └── dashboard.html          # Dashboard UI
│
├── static/
│   ├── css/dashboard.css       # Dashboard styles
│   └── js/dashboard.js         # Dashboard logic
│
├── email_config.json           # Email SMTP settings
├── email_credentials.json      # Email credentials (in .gitignore)
├── account_info.json           # Account data (auto-generated)
└── trade_logs/                 # Trade history JSON files
```

---

## 🎯 Usage

### 🌐 Run with Web Dashboard (Recommended)

```bash
python dashboard_app.py
```

Then open your browser to: **http://localhost:5000**

The dashboard provides:
- 📊 Real-time account balance, equity, and profit
- 📈 Live position monitoring with P/L
- 🔮 Parabolic SAR indicator values and trends
- 📉 Price chart with SAR overlay
- 🎯 Current trading signals (BUY/SELL/HOLD)
- 📜 Trade history table
- 🔔 Real-time notifications

### 💻 Run Terminal-Only (No Dashboard)

```bash
python app.py
```

---

## ⚙️ Configuration

### Trading Parameters

Edit `dashboard_app.py` or `app.py`:

```python
desired_signal = 'BUY'          # or 'SELL'
risk_percentage = 1.0           # Risk 1% per trade
signal_check_interval = 30      # Check signals every 30 seconds
position_check_interval = 5     # Monitor position every 5 seconds
```

### Email Notifications

1. **Edit `email_credentials.json`:**
```json
{
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_16_digit_app_password",
    "recipient_email": "recipient@example.com"
}
```

2. **For Gmail:**
   - Enable 2-Factor Authentication
   - Generate App Password at: https://myaccount.google.com/apppasswords
   - Use the 16-digit password (not your regular password)

---

## 📊 How It Works

1. **🔍 Signal Detection**
   - Bot monitors Parabolic SAR on 15-minute timeframe
   - Waits for BUY or SELL signal based on configuration
   - Checks every 30 seconds (configurable)

2. **📈 Trade Execution**
   - Calculates position size based on risk percentage
   - Sets Stop Loss at current SAR value
   - Sets Take Profit at 1:2 risk-reward ratio
   - Executes order via MT5

3. **🔒 Position Monitoring** (every 5 seconds)
   - **Trailing Stop Loss**: Moves SL when SAR moves in profit direction
   - **SAR Reversal**: Closes position if trend reverses
   - **Emergency SL**: Code-level protection if MT5 SL fails
   - Updates dashboard in real-time

4. **✉️ Email & Dashboard Alerts**
   - Position closed (TP/SL/Manual/SAR reversal)
   - Profit/Loss details
   - Final account balance
   - Real-time dashboard updates

5. **🔄 Continuous Loop**
   - After position closes, bot automatically searches for next signal
   - Never-ending automated trading cycle

---

## 🖥️ Dashboard Features

### Account Panel
- Balance, Equity, Free Margin
- Current Profit

### Position Panel
- Ticket, Type (BUY/SELL)
- Entry/Current/SL/TP Prices
- Profit/Loss, Duration

### SAR Indicator Panel
- Current SAR Value
- Trend (UPTREND/DOWNTREND)
- Distance to price

### Signal Panel
- Current Signal (BUY/SELL/HOLD)
- Signal reason
- Timestamp

### Price Chart
- Real-time XAUUSD price
- SAR value overlay
- Last 100 data points

### Trade History
- Last 20 trades
- Profit/Loss with color coding
- Duration, Close reason

---

## 📝 Trade Logging

All trades are automatically logged to `trade_logs/trades_YYYY_MM_DD.json`:

```json
{
    "timestamp": "2025-11-28T14:30:15",
    "action": "BUY",
    "symbol": "XAUUSD",
    "entry_price": 4223.57,
    "stop_loss": 4195.23,
    "take_profit": 4280.25,
    "volume": 0.16,
    "risk_reward_ratio": 2.0,
    "result": "success"
}
```

---

## 🔧 Advanced Configuration

### Parabolic SAR Parameters

Edit `src/parabolic_sar.py`:

```python
ParabolicSAR(
    symbol="XAUUSD",
    timeframe=mt5.TIMEFRAME_M15,  # 15-minute
    acceleration=0.02,             # Acceleration factor
    maximum=0.2                    # Maximum acceleration
)
```

### Risk Management

Edit `src/risk_manager.py`:

```python
RiskManager(
    symbol="XAUUSD",
    risk_reward_ratio=2.0  # 1:2 risk-reward
)
```

## ⚠️ Disclaimer

This is a trading bot that executes real trades on MetaTrader5. Use at your own risk. 

**Always:**
- Test with demo account first
- Understand the code before running
- Monitor the bot regularly
- Set appropriate risk limits
- Never risk more than you can afford to lose

---

## 🤝 Contributing

This is a personal trading project. Feel free to fork and modify for your own use.
