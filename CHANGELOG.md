# 📝 Changelog

All notable changes to the **Gold Trading Bot** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### 🔮 Planned for v1.0
- [ ] **MT5 Integration**: Full MetaTrader5 connection and authentication
- [ ] **Account Data Collection**: Comprehensive account metrics gathering
- [ ] **Multi-Symbol Support**: Auto-detection of gold symbols (XAUUSD, XAUUSD., XAUUSD.m, GOLD, GOLD.)
- [ ] **Order Execution**: BUY orders with configurable parameters
- [ ] **Risk Management**: Automatic Stop Loss and Take Profit calculation
- [ ] **Trade Logging**: JSON-based trade history logging system

### 🚀 Planned for v1.1
- [ ] **Parabolic SAR Indicator**: Implementation of Parabolic SAR (Stop and Reverse) technical indicator with 15-minute timeframe data analysis
- [ ] **Dynamic Stop Loss Based on SAR**: Automatic Stop Loss placement at Parabolic SAR value position for adaptive risk management
- [ ] **Emergency Stop Loss Monitor**: Automatic position closure if price breaks SL level but SL order hasn't triggered (protection against slippage and sudden price gaps)

### 🔧 Planned for v1.2
- [ ] **Strategy Engine**: Multiple trading strategy support
- [ ] **Backtesting Module**: Historical data testing capability
- [ ] **Performance Analytics**: Win/loss ratio, profit factor calculations
- [ ] **Position Management**: Partial close, break-even, trailing features

### 🤖 Planned for v1.3
- [ ] **Automated Trading Loop**: Continuous trading bot operation
- [ ] **Circuit Breaker System**: Automatic trading pause conditions:
  - Stop trading for 1 hour if last 5 consecutive trades are losses
  - Stop trading for 1 hour if 70% of last 10 trades failed
- [ ] **Daily Loss Limit**: Configurable maximum daily loss protection
- [ ] **Trading Hours Control**: Specific time window restrictions

### 📱 Planned for v1.4
- [ ] **Telegram Integration**: Real-time trade notifications via Telegram
- [ ] **Email Notifications**: Trade alerts and daily reports via email
- [ ] **Discord Webhook**: Optional Discord integration for trade updates
- [ ] **Custom Alert Rules**: Configurable notification triggers

### 🌐 Planned for v1.5
- [ ] **Web Dashboard**: Real-time monitoring interface
- [ ] **Price Feed**: Live market price retrieval
- [ ] **Multiple Asset Support**: Extend beyond gold to forex pairs
- [ ] **AI/ML Integration**: Machine learning-based signal generation
- [ ] **Cloud Deployment**: Docker containerization and cloud hosting support

### � Planned for v1.6
- [ ] **MOST Indicator Integration**: Implementation of MOST (Moving Stop Loss) indicator for dynamic trend analysis
- [ ] **Multi-Indicator Strategy**: Combined signal generation using both MOST and Parabolic SAR indicators for enhanced trade accuracy
- [ ] **Indicator Confirmation System**: Trade execution only when both indicators align (consensus-based trading)


---

## 📌 Version Format

This project uses **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **MAJOR** (x.0.0): Breaking changes, major rewrites
- **MINOR** (0.x.0): New features, backward compatible additions
- **PATCH** (0.0.x): Bug fixes, small improvements, documentation updates

---

## 🏷️ Tags Legend

- 🎉 Initial Release
- ✨ New Feature
- 🐛 Bug Fix
- 🔧 Configuration
- 📚 Documentation
- 🚀 Performance
- 🔒 Security
- ⚠️ Breaking Change
