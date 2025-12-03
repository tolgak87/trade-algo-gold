"""
DEPRECATED: This file is no longer supported.

Legacy MT5 modules have been removed. Use app_bridge.py instead.

Migration Guide:
    OLD: python dashboard_app.py
    NEW: python app_bridge.py

The new MQL Bridge version provides:
- MT4 and MT5 support
- Better broker compatibility  
- No MetaTrader5 Python module required
- Uses Expert Advisor bridge for communication

Setup Instructions:
1. Copy PythonBridge_MT5.mq5 (or MT4 version) to your MT terminal
2. Compile and attach the EA to a chart
3. Run: python app_bridge.py

For detailed instructions, see: README_BRIDGE.md
"""

import sys


def main():
    """Display deprecation message and exit."""
    print("=" * 70)
    print("❌ DEPRECATED: dashboard_app.py is no longer available")
    print("=" * 70)
    print()
    print("Legacy MetaTrader5 Python modules have been removed.")
    print("Please use the new MQL Bridge version instead:")
    print()
    print("  → python app_bridge.py")
    print()
    print("Benefits of MQL Bridge:")
    print("  ✓ Works with both MT4 and MT5")
    print("  ✓ Better broker compatibility")
    print("  ✓ No Python dependencies for MT5")
    print("  ✓ Uses Expert Advisor for communication")
    print()
    print("Quick Setup:")
    print("  1. Copy PythonBridge_MT5.mq5 or PythonBridge_MT4.mq4 to MT terminal")
    print("  2. Compile and attach EA to chart")
    print("  3. Run: python app_bridge.py")
    print()
    print("Documentation: README_BRIDGE.md")
    print("=" * 70)
    return 1


if __name__ == "__main__":
    sys.exit(main())
