@echo off
echo ============================================================
echo  Gold Trading Bot - Dashboard Installation
echo ============================================================
echo.

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please make sure Python and pip are installed
    pause
    exit /b 1
)

echo.
echo [2/3] Creating configuration files...

if not exist email_credentials.json (
    echo Creating email_credentials.json template...
    echo { > email_credentials.json
    echo     "sender_email": "your_email@gmail.com", >> email_credentials.json
    echo     "sender_password": "your_16_digit_app_password", >> email_credentials.json
    echo     "recipient_email": "recipient@example.com" >> email_credentials.json
    echo } >> email_credentials.json
    echo Email template created - please edit with your credentials
) else (
    echo email_credentials.json already exists
)

echo.
echo [3/3] Installation complete!
echo.
echo ============================================================
echo  Next Steps:
echo ============================================================
echo  1. Open MetaTrader5 and login
echo  2. Edit email_credentials.json (optional)
echo  3. Run: python dashboard_app.py
echo  4. Open browser: http://localhost:5000
echo ============================================================
echo.
pause
