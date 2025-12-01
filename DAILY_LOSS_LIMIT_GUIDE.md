# 📉 Daily Loss Limit System - Complete Guide

## 🎯 What is Daily Loss Limit?

Daily Loss Limit is an advanced protection system that automatically pauses trading when you lose a certain percentage of your account balance in a single trading day. This prevents catastrophic losses and protects your capital.

---

## ⚙️ How It Works

### 1. **Starting Balance Tracking**
- Every day at the first trade check, the system records your current account balance as "starting balance"
- This starting balance is used as the reference point for all loss calculations
- Resets automatically at midnight (new trading day)

### 2. **Real-Time Loss Calculation**
```
Daily Loss = Starting Balance - Current Balance
Loss Percentage = (Daily Loss / Starting Balance) × 100
```

### 3. **Automatic Pause**
When loss limit is reached:
- ✅ Trading is automatically paused
- ✅ Email notification is sent with details
- ✅ Bot continues running but won't execute new trades
- ✅ Automatically resumes at midnight (new day)

---

## 🔧 Configuration

Edit `protection_config.json`:

```json
{
    "daily_loss_limit": {
        "enabled": true,
        "max_daily_loss_dollars": 1000,
        "max_daily_loss_percentage": 10,
        "use_percentage": true,
        "description": "Daily loss limit protection"
    }
}
```

### Configuration Options:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `true` | Enable/disable daily loss limit |
| `max_daily_loss_percentage` | `10` | Maximum loss percentage (10% = lose 10% of starting balance) |
| `max_daily_loss_dollars` | `1000` | Maximum loss in dollars (fixed amount) |
| `use_percentage` | `true` | Use percentage (true) or fixed dollars (false) |

---

## 💡 Examples

### Example 1: Percentage-Based (Default)

**Settings:**
- Starting Balance: $10,000
- Max Loss: 10%

**Calculation:**
- Maximum allowed loss: $10,000 × 10% = $1,000
- When balance drops to $9,000 or below → Trading paused

**Scenarios:**
- Balance $9,500 → ✅ Trading allowed ($500 loss = 5%)
- Balance $9,000 → 🔴 Trading paused ($1,000 loss = 10%)
- Balance $8,500 → 🔴 Trading paused ($1,500 loss = 15%)

### Example 2: Fixed Dollar Amount

**Settings:**
- Starting Balance: $10,000
- Max Loss: $500 (fixed)

**Calculation:**
- Maximum allowed loss: $500 (regardless of balance)
- When balance drops to $9,500 or below → Trading paused

---

## 📊 Testing

Run the test script to check your current status:

```bash
python test_daily_loss_limit.py
```

**Output:**
```
📊 Current Account Balance: $9,650.00

💡 Daily Loss Limit Details:
   Starting Balance: $10,000.00
   Max Loss Allowed: 10% ($1,000.00)
   Current Loss: $350.00
   Remaining: $650.00 (6.5%)

✅ Daily loss limit OK - Trading allowed
```

---

## 🔍 Monitoring

### View Status in Dashboard
```bash
python dashboard_app.py
```

The dashboard shows:
- Starting balance vs current balance
- Daily loss amount and percentage
- Remaining loss allowance
- Red alert when limit is approaching

### Check Manually
```python
from src.circuit_breaker import CircuitBreaker
from src.trade_logger import TradeLogger

breaker = CircuitBreaker(TradeLogger())
breaker.display_status()
```

---

## 📧 Email Notifications

When daily loss limit is reached, you receive an email with:

```
🔴 DAILY LOSS LIMIT REACHED - Trading Paused

💰 Account Status:
- Starting Balance (Today): $10,000.00
- Current Balance: $9,000.00
- Daily Loss: $1,000.00 (10.0%)

📊 Loss Details:
- Total Trades Today: 8
- Total Loss Today: $1,050.00
- Consecutive Losses: 5

⏰ Trading will automatically resume at midnight.
```

---

## 🎛️ Customization

### Conservative Settings (Tight Protection)
```json
{
    "max_daily_loss_percentage": 5,  // Only 5% loss allowed
    "use_percentage": true
}
```

### Moderate Settings (Default)
```json
{
    "max_daily_loss_percentage": 10,  // 10% loss allowed
    "use_percentage": true
}
```

### Aggressive Settings (Loose Protection)
```json
{
    "max_daily_loss_percentage": 15,  // 15% loss allowed
    "use_percentage": true
}
```

### Fixed Dollar Amount (For Specific Risk)
```json
{
    "max_daily_loss_dollars": 500,   // Fixed $500 max loss
    "use_percentage": false
}
```

---

## 🔄 Reset & Override

### Reset Daily Loss Limit
```bash
python reset_circuit_breaker.py
```

Choose option to clear state. This will reset:
- Starting balance tracking
- Daily pause counters
- Circuit breaker state

**Warning:** Only use when you want to start completely fresh (e.g., after depositing/withdrawing funds)

---

## ❓ FAQ

### Q: Why use starting balance instead of trade logs?
**A:** More accurate! Starting balance reflects your actual account value, including:
- Manual trades on MT5
- Withdrawals/deposits
- Overnight interest/swap
- Other trading activities

### Q: What happens at midnight?
**A:** New trading day starts:
- Starting balance resets to current balance
- Loss counter resets to $0
- Trading automatically resumes
- Daily pause counter resets

### Q: Can I override the pause?
**A:** Yes, but not recommended! Use:
```bash
python reset_circuit_breaker.py
```

### Q: Percentage vs Fixed Dollar - Which is better?
**A:** 
- **Percentage**: Better for growing/shrinking accounts (scales automatically)
- **Fixed Dollar**: Better for specific risk targets (doesn't scale)

### Q: Does it work with other protections?
**A:** Yes! Daily Loss Limit works alongside:
- Circuit Breaker (consecutive losses)
- Stop Loss per trade
- Risk percentage per trade

---

## 🚨 Important Notes

1. **Not a replacement for Stop Loss**: Each trade still needs proper Stop Loss
2. **Account-wide protection**: Includes ALL trading activity, not just bot trades
3. **Cannot prevent slippage**: If market gaps down, loss may exceed limit
4. **New day = Fresh start**: Limit resets at midnight every day
5. **Keeps bot running**: Bot continues running during pause (only blocks new trades)

---

## 📈 Best Practices

1. **Set realistic limits**: 5-10% is typical for day trading
2. **Monitor regularly**: Check dashboard throughout the day
3. **Review losing days**: Analyze what went wrong when limit is hit
4. **Adjust strategy**: If hitting limit often, review your trading approach
5. **Combine protections**: Use with Circuit Breaker for maximum safety

---

## 🔗 Related Features

- **Circuit Breaker**: Protects against consecutive loss patterns
- **Per-Trade Risk**: Controls individual trade risk (default 1%)
- **Stop Loss**: Trade-level protection
- **Email Alerts**: Real-time notifications

---

## 📞 Support

For issues or questions:
1. Check `circuit_breaker_state.json` for current state
2. Review `protection_config.json` for settings
3. Run `python test_daily_loss_limit.py` to diagnose
4. Check email notifications (if enabled)

---

**Remember:** The goal is to protect your capital and live to trade another day! 🛡️
