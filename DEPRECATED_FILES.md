# Deprecated Legacy Files

This document lists files that are deprecated and can be removed in future versions.

## ❌ Safe to Delete (Not Required for Bridge Mode)

These files are **ONLY** needed if you want to run the legacy `dashboard_app.py` with MT5 Python API:

### 1. `src/collect_account_info.py`
- **Status**: DEPRECATED - Legacy MT5 account collection
- **Replacement**: `src/collect_account_info_bridge.py`
- **Used by**: `trading_bot.py` (optional import)
- **Safe to delete if**: You only use `app_bridge.py`

### 2. `src/order_executor_legacy.py`
- **Status**: DEPRECATED - Legacy MT5 order execution
- **Replacement**: `src/order_executor.py` (Bridge version)
- **Used by**: `trading_bot.py` (optional import)
- **Safe to delete if**: You only use `app_bridge.py`

### 3. `src/risk_manager_legacy.py`
- **Status**: DEPRECATED - Legacy MT5 risk management
- **Replacement**: `src/risk_manager.py` (Bridge version)
- **Used by**: `trading_bot.py` (optional import)
- **Safe to delete if**: You only use `app_bridge.py`

### 4. `src/symbol_detector.py`
- **Status**: DEPRECATED - Legacy MT5 symbol detection
- **Replacement**: `src/symbol_detector_bridge.py`
- **Used by**: `trading_bot.py` (optional import)
- **Safe to delete if**: You only use `app_bridge.py`

### 5. `src/parabolic_sar.py`
- **Status**: LEGACY - MT5 direct version
- **Replacement**: `src/parabolic_sar_bridge.py`
- **Used by**: `trading_bot.py`
- **Safe to delete if**: You only use `app_bridge.py`

## ⚠️ Keep for Specific Use Cases

### 6. `src/backtest/backtest_engine.py`
- **Status**: ACCEPTABLE - Uses MT5 for historical data
- **Reason**: Backtesting legitimately needs historical market data
- **Note**: MT5 usage is acceptable here for historical data access

### 7. `src/trading_bot.py`
- **Status**: DEPRECATED - Legacy MT5 trading bot
- **Replacement**: `app_bridge.py` + `src/trading_bot_bridge.py`
- **Keep for**: Backward compatibility with `dashboard_app.py`
- **Note**: Will fail gracefully if legacy modules are deleted

## 📋 Summary

### If you ONLY use MQL Bridge (`app_bridge.py`):
```bash
# You can safely delete these files:
rm src/collect_account_info.py
rm src/order_executor_legacy.py
rm src/risk_manager_legacy.py
rm src/symbol_detector.py
rm src/parabolic_sar.py  # Optional - keep bridge version
```

### If you use Legacy Dashboard (`dashboard_app.py`):
```bash
# Keep all legacy files - they are required
# MT5 Python module must be installed: pip install MetaTrader5
```

## 🎯 Recommended Setup

### Modern Setup (MQL Bridge):
- ✅ Use `app_bridge.py`
- ✅ Use bridge versions: `*_bridge.py`
- ✅ No MetaTrader5 Python module required
- ✅ Works with MT4 and MT5

### Legacy Setup (Direct MT5):
- ⚠️ Use `dashboard_app.py`
- ⚠️ Requires all legacy files
- ⚠️ Requires `pip install MetaTrader5`
- ⚠️ Only works with MT5

## 🔄 Migration Path

To fully migrate from legacy to bridge:

1. **Stop using** `dashboard_app.py`
2. **Start using** `app_bridge.py`
3. **Delete legacy files** (listed above)
4. **Uninstall** MetaTrader5 Python module: `pip uninstall MetaTrader5`
5. **Keep** Expert Advisors: `PythonBridge_MT5.mq5` / `PythonBridge_MT4.mq4`

---

**Last Updated**: December 3, 2025
**Branch**: feature/create-mql
