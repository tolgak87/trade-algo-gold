# 📝 Changelog

All notable changes to the **Gold Trading Bot** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/).
 
---

## [Released]

### 🔮 Planned for v1.0
- **MT5 Integration**: Full MetaTrader5 connection and authentication
- **Account Data Collection**: Comprehensive account metrics gathering
- **Multi-Symbol Support**: Auto-detection of gold symbols (XAUUSD, XAUUSD., XAUUSD.m, GOLD, GOLD.)
- **Order Execution**: BUY orders with configurable parameters
- **Risk Management**: Automatic Stop Loss and Take Profit calculation
- **Trade Logging**: JSON-based trade history logging system

### 🚀 Planned for v1.1
- **Parabolic SAR Indicator**: Implementation of Parabolic SAR (Stop and Reverse) technical indicator with 15-minute timeframe data analysis
- **Dynamic Stop Loss Based on SAR**: Automatic Stop Loss placement at Parabolic SAR value position for adaptive risk management
- **Emergency Stop Loss Monitor**: Automatic position closure if price breaks SL level but SL order hasn't triggered (protection against slippage and sudden price gaps)
- **Monitor SAR**: Clsoe position if SAR turns to DOWNTREND
- **Open Position**: Either open LONG/SHORT position
- **Trail Stop Loss**: Increase the Stop-loss price by trail for price rises (It will not decrase the stop-loss price)
- **Close Position if SL passed**: Close position for sudden decreases and stop loss not worked
- **Automated Trading Loop**: Continuous trading bot operation, even the position closed manually, code will check for new opportunity

### 📱 Planned for v1.2
- [x] **Web Dashboard**: Real-time monitoring interface (localhost, WebSocket-based)
- [x] **Email Notifications**: Send email after manuel or TP/SL process

## [Unreleased]

### 🤖 Planned for v1.
- [ ] **Circuit Breaker System**: Automatic trading pause conditions:
  - Stop trading for 1 hour if last 5 consecutive trades are losses
  - Stop trading for 1 hour if 70% of last 10 trades failed
- [ ] **Daily Loss Limit**: Configurable maximum daily loss protection


### � Planned for v1.
- [ ] **MOST Indicator Integration**: Implementation of MOST (Moving Stop Loss) indicator for dynamic trend analysis
- [ ] **Multi-Indicator Strategy**: Combined signal generation using both MOST and Parabolic SAR indicators for enhanced trade accuracy
- [ ] **Indicator Confirmation System**: Trade execution only when both indicators align (consensus-based trading)

### 🔧 Planned for v1.
- [ ] **Keep Time of Position**: Keep time of a opened position in a log
- [ ] **Performance Analytics**: Win/loss ratio, profit factor calculations
- [ ] **Daily Revenue/Loss Limit**: After a big win/loss with a limit, exit from python code
- [ ] **Collect data and create a solution**: Current TP/SL is a set price. Keep track the price and give a solution for better prices for TP/SL from historical data (keep historical data)

### 🔧 Planned for v1.
- [ ] **Multiple Asset Support**: Extend beyond gold to forex pairs
- [ ] **AI/ML Integration**: Machine learning-based signal generation
- [ ] **Cloud Deployment**: Docker containerization and cloud hosting support
- [ ] **Custom Alert Rules**: Configurable notification triggers



