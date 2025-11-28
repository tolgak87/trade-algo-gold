# 🚀 Quick Start Guide - Web Dashboard

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- MetaTrader5 (MT5 integration)
- pandas (data processing)
- Flask (web server)
- Flask-SocketIO (real-time updates)

## Step 2: Open MetaTrader5

1. Launch MetaTrader5
2. Login to your demo or live account
3. Make sure MT5 is running in the background

## Step 3: Configure Email (Optional)

Edit `email_credentials.json`:

```json
{
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_16_digit_app_password",
    "recipient_email": "recipient@example.com"
}
```

For Gmail app password:
1. Enable 2FA: https://myaccount.google.com/security
2. Create app password: https://myaccount.google.com/apppasswords
3. Select "Mail" and generate 16-digit password

## Step 4: Run Dashboard

```bash
python dashboard_app.py
```

You'll see:
```
============================================================
🌐 DASHBOARD SERVER STARTING
============================================================
📊 Access dashboard at: http://127.0.0.1:5000
🔄 Real-time updates enabled via WebSocket
============================================================
```

## Step 5: Open Dashboard

Open your browser and go to: **http://localhost:5000**

## Step 6: Monitor Trading

The dashboard shows:
- ✅ Account balance, equity, profit
- ✅ Current position (if any)
- ✅ Parabolic SAR indicator
- ✅ Trading signals (BUY/SELL/HOLD)
- ✅ Real-time price chart
- ✅ Trade history

## Configuration

Edit `dashboard_app.py` to change:

```python
# Trading settings
desired_signal = 'BUY'           # or 'SELL'
risk_percentage = 1.0            # Risk per trade
signal_check_interval = 30       # Seconds between signal checks
position_check_interval = 5      # Seconds between position updates
```

## Dashboard Features

### 📊 Account Panel
- Balance: Your account balance
- Equity: Current equity (balance + profit)
- Free Margin: Available margin
- Current Profit: Unrealized P/L

### 📈 Position Panel
- Shows current open position (if any)
- Entry price, Current price
- Stop Loss, Take Profit
- Real-time profit/loss
- Position duration

### 🔮 SAR Indicator Panel
- Current SAR value
- Trend (UPTREND/DOWNTREND)
- Distance to price

### 🎯 Signal Panel
- Current signal: BUY/SELL/HOLD
- Reason for signal
- Timestamp

### 📉 Price Chart
- Real-time XAUUSD price
- Parabolic SAR overlay
- Auto-updates every check

### 📜 Trade History
- Last 20 trades
- Color-coded profit/loss
- Close reason, Duration

## Access from Phone/Tablet

1. Find your PC's IP address:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. Edit `dashboard_app.py`:
   ```python
   dashboard = initialize_dashboard(host='0.0.0.0', port=5000)
   ```

3. Open on phone: `http://YOUR_PC_IP:5000`

## Troubleshooting

### Dashboard not loading?
- Check if MT5 is running
- Make sure port 5000 is not in use
- Try opening http://127.0.0.1:5000

### No data showing?
- Ensure MT5 is logged in
- Check terminal for errors
- Refresh browser page

### Position not updating?
- Check WebSocket connection (green badge in header)
- Look for JavaScript errors in browser console (F12)
- Restart dashboard_app.py

### Email not working?
- Check email_credentials.json format
- Verify Gmail app password (not regular password)
- Check 2FA is enabled on Gmail

## Stop Trading

Press `Ctrl+C` in terminal to stop bot gracefully.

## Run Without Dashboard

If you prefer terminal only:

```bash
python app.py
```

This runs the bot without web interface.

## Next Steps

1. Test on demo account first
2. Monitor for 24 hours
3. Adjust risk percentage if needed
4. Enable email notifications
5. Consider adding circuit breakers (v1.3)

## Support

- Check logs in `trade_logs/` folder
- Review CHANGELOG.md for features
- Read README.md for detailed docs

Happy Trading! 🚀
