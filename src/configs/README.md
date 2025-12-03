# 📁 Configuration Files

This directory contains all configuration files for the Gold Trading Bot. These JSON files allow you to customize bot behavior without modifying Python code.

---

## 📋 Configuration Files

### 1️⃣ `trade_config.json` - Trading Parameters

**Purpose:** Main trading configuration for automated trading cycle

**Parameters:**

```json
{
    "trading": {
        "desired_signal": "BUY",           // Signal to wait for: "BUY", "SELL", or "BOTH"
        "risk_percentage": 1.0,            // Risk per trade (% of account balance)
        "signal_check_interval": 30,       // Seconds between signal checks
        "position_check_interval": 5       // Seconds between position monitoring
    },
    "symbols": {
        "priority_list": [
            "XAUUSD",                      // Gold symbols in priority order
            "XAUUSD.",
            "XAUUSD.m",
            "GOLD",
            "GOLD."
        ]
    }
}
```

**How to Change Trading Product:**

1. Open `available_symbols.json` to see all available products
2. Find the product you want to trade (e.g., EURUSD, BITCOIN, US30)
3. Copy the symbol list
4. Paste into `trade_config.json` -> `symbols.priority_list`
5. Save and restart bot

**Example - Switch from Gold to EUR/USD:**
```json
// Copy from available_symbols.json -> "EURUSD" section:
"symbols": {
    "priority_list": [
        "EURUSD",
        "EUR/USD",
        "EURUSD.",
        "EURUSD.m"
    ]
}
```

---

### 1️⃣.A `available_symbols.json` - Symbol Library

**Purpose:** Pre-configured symbol lists for all major trading products

**Contents:**
- **Precious Metals:** GOLD, SILVER
- **Major Forex:** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD
- **Cross Pairs:** EURGBP, EURJPY, GBPJPY
- **Crypto:** BITCOIN, ETHEREUM
- **Indices:** US30, NAS100, SPX500
- **Commodities:** OIL, BRENT, NATURALGAS

**How to Use:**
1. Open `available_symbols.json`
2. Find your desired product (e.g., "BITCOIN")
3. Copy the array: `["BTCUSD", "BTC/USD", "BITCOIN", "BTCUSD.m"]`
4. Open `trade_config.json`
5. Paste into `symbols.priority_list`
6. Save and restart bot

**Quick Copy Examples:**

For **Gold** (default):
```json
"priority_list": ["XAUUSD", "XAUUSD.", "XAUUSD.m", "GOLD", "GOLD."]
```

For **Bitcoin**:
```json
"priority_list": ["BTCUSD", "BTC/USD", "BITCOIN", "BTCUSD.m"]
```

For **US30** (Dow Jones):
```json
"priority_list": ["US30", "DJ30", "DOWJONES", "US30.", "US30.m"]
```

For **EUR/USD**:
```json
"priority_list": ["EURUSD", "EUR/USD", "EURUSD.", "EURUSD.m"]
```

---

### 1️⃣.B Trading Configuration Details

**How to Modify:**

- **desired_signal**: 
  - `"BUY"` - Only open long positions
  - `"SELL"` - Only open short positions  
  - `"BOTH"` - Trade in both directions

- **risk_percentage**: 
  - `1.0` = Risk 1% per trade (Recommended for beginners)
  - `2.0` = Risk 2% per trade (Aggressive)
  - **Never exceed 2%** for safety

- **signal_check_interval**: How often to check for new trade signals (seconds)
- **position_check_interval**: How often to monitor open positions (seconds)

- **symbols.priority_list**: 
  - List of symbols to search for in MT5 account
  - Bot uses **first available** symbol found
  - Add other symbols for different markets:
    ```json
    "priority_list": ["EURUSD", "GBPUSD", "USDJPY"]  // Forex
    "priority_list": ["BTCUSD", "ETHUSD"]            // Crypto
    "priority_list": ["US30", "NAS100"]              // Indices
    ```

**⚠️ Important Notes:**

- **1% risk is recommended** for initial testing and safe trading
- With $11,541 account at 1% risk: ~0.06 lot per trade
- With $2,000 account at 1% risk: ~0.01 lot per trade
- Lot size automatically adjusts based on Stop Loss distance
- Higher risk = faster gains OR faster losses (exponential effect)

---

### 2️⃣ `protection_config.json` - Circuit Breaker & Loss Limits

**Purpose:** Protect account from excessive losses with automatic trading pauses

**Parameters:**

```json
{
    "circuit_breaker": {
        "consecutive_loss_threshold_1": 5,
        "pause_duration_1_hours": 3,
        "consecutive_loss_threshold_2": 8,
        "pause_duration_2_hours": 5,
        "loss_rate_window": 10,
        "loss_rate_threshold": 0.7,
        "loss_rate_pause_hours": 5
    },
    "daily_loss_limit": {
        "enabled": true,
        "percentage": 10.0,
        "fixed_amount": null
    }
}
```

**Circuit Breaker Logic:**

1. **5 consecutive losses** → Pause for 3 hours
2. **3 more losses (8 total)** → Pause for 5 more hours
3. **70% losses in last 10 trades** → Pause for 5 hours

**Daily Loss Limit:**

- **10% maximum daily loss** (default)
- Tracks from starting balance each day
- Bot stops trading until next day when limit reached

**⚠️ Never Disable These Protections** - They prevent catastrophic losses

---

### 3️⃣ `email_config.json` - Email Notifications

**Purpose:** Configure email notifications for important events

**Parameters:**

```json
{
    "sender_email": "your_email@gmail.com",
    "recipient_email": "your_email@gmail.com",
    "enabled": true
}
```

**Credentials:** Stored separately in `email_credentials.json` (not in git)

**Notification Events:**

- Circuit breaker activation (consecutive losses)
- Daily loss limit reached
- Position opened/closed
- System errors

---

## 🛠️ Quick Start Guide

### Change Risk Percentage

Edit `trade_config.json`:
```json
{
    "trading": {
        "risk_percentage": 1.5    // Change from 1.0 to 1.5 (1.5% risk)
    }
}
```

### Change Trading Direction

Edit `trade_config.json`:
```json
{
    "trading": {
        "desired_signal": "SELL"   // Only trade sell signals
    }
}
```

### Change Trading Symbol (e.g., Trade EUR/USD instead of Gold)

Edit `trade_config.json`:
```json
{
    "symbols": {
        "priority_list": ["EURUSD", "EUR/USD", "EURUSD."]  // Forex pair
    }
}
```

**Popular Symbol Examples:**
```json
// Gold (default)
"priority_list": ["XAUUSD", "XAUUSD.", "GOLD"]

// EUR/USD Forex
"priority_list": ["EURUSD", "EUR/USD"]

// GBP/USD Forex  
"priority_list": ["GBPUSD", "GBP/USD"]

// Bitcoin
"priority_list": ["BTCUSD", "BITCOIN"]

// US30 Index
"priority_list": ["US30", "DJ30", "DOWJONES"]
```

### Adjust Daily Loss Limit

Edit `protection_config.json`:
```json
{
    "daily_loss_limit": {
        "enabled": true,
        "percentage": 5.0         // Change from 10% to 5% (more conservative)
    }
}
```

---

## 📊 Risk Management Guidelines

### Recommended Risk Levels by Experience

| Experience Level | Risk % | Description |
|-----------------|--------|-------------|
| **Beginner** | 0.5-1% | Conservative, safe testing |
| **Intermediate** | 1-1.5% | Balanced growth |
| **Advanced** | 1.5-2% | Aggressive but manageable |
| **Never** | >2% | Gambling, not trading |

### Example: $11,541 Account

| Risk % | Risk per Trade | Typical Lot Size | 5 Wins | 5 Losses |
|--------|---------------|------------------|---------|----------|
| 1% | $115 | 0.06 lot | +$575 | -$575 |
| 2% | $231 | 0.12 lot | +$1,155 | -$1,155 |
| 10% | $1,154 | 0.62 lot | +$5,770 | **-40% account!** |

---

## 🔄 Testing Your Changes

After modifying config files:

1. **Save the file** (changes take effect on next bot start)
2. **Restart the bot**: `python dashboard_app.py`
3. **Check console output** for "✅ Loaded trading configuration"
4. **Verify settings** in bot startup display

---

## 🚨 Safety Reminders

✅ **DO:**
- Start with 1% risk for testing
- Keep circuit breaker enabled
- Use 10% daily loss limit (or lower)
- Test configuration changes in backtest mode first

❌ **DON'T:**
- Disable circuit breaker protections
- Use risk >2% per trade
- Trade with money you can't afford to lose
- Ignore consecutive losses (review strategy)

---

## 📞 Troubleshooting

**Config not loading?**
- Check JSON syntax (valid brackets, commas, quotes)
- Verify file is saved in `src/configs/` directory
- Check console for error messages

**Bot using wrong values?**
- Restart bot after config changes
- Check for typos in parameter names
- Ensure JSON is valid (use JSON validator online)

**Want to test safely?**
- Set `BACKTEST_MODE = True` in `dashboard_app.py`
- Run `python backtest_app.py` for parameter testing
- Use demo account before live trading

---

**Last Updated:** 2025-01-20  
**Bot Version:** v1.4
