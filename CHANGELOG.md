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
- **Web Dashboard**: Real-time monitoring interface (localhost, WebSocket-based)
- **Email Notifications**: Send email after manuel or TP/SL process

### 📱 Planned for v1.3
- **Back Testing**: Back testing from last 2 months of MT5 data (1 min candle)

### ✅ Completed for v1.4
- **Circuit Breaker System**: Automatic trading pause on loss patterns:
  - 5 consecutive losses → pause 3h | 3 more consecutive losses → pause 5h more
  - 70% losses in last 10 trades → pause 5h
  - Email notifications with account balance and loss details
  - State persistence across bot restarts
- **Daily Loss Limit**: Configurable maximum daily loss protection (Default 10% loss)
  - Tracks starting balance at beginning of each day
  - Real-time loss calculation from starting balance
  - Automatic pause until next day when limit reached
  - Percentage-based (default) or fixed dollar amount
  - Email notification on limit breach
  - Visual display of remaining loss allowance


## [Unreleased]

### 🧪 Planned for v1.5 - Testing & Quality
- [ ] **Unit Tests**: Comprehensive unit test suite for critical components
  - Risk calculation tests (position sizing, lot calculation)
  - Circuit breaker logic tests (consecutive losses, percentage losses)
  - Daily loss limit tests (threshold detection, balance tracking)
  - Trade logger tests (P/L calculation, statistics)
  - Config loading tests (path resolution, file creation)
- [ ] **Regression Tests**: Automated regression testing suite
  - Risk management functionality regression
  - Circuit breaker behavior regression
  - Daily loss limit logic regression
  - Configuration loading regression
  - Trade logging system regression
- [ ] **Test Documentation**: Test case documentation
  - Test scenarios and expected results
  - Test data preparation guidelines
  - Manual testing procedures
  - Integration test specifications

### 🤖 Planned for v1.
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



