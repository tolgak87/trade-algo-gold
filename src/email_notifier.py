import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict
import json


class EmailNotifier:
    """
    Email notification system for trade events
    Sends alerts when positions close (TP, SL, manual, SAR reversal)
    """
    
    def __init__(self, smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 sender_email: str = "",
                 sender_password: str = "",
                 recipient_email: str = ""):
        """
        Initialize email notifier
        
        Args:
            smtp_server: SMTP server address (default: Gmail)
            smtp_port: SMTP port (default: 587 for TLS)
            sender_email: Sender's email address
            sender_password: Sender's email app password
            recipient_email: Recipient's email address
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.enabled = False
        
        # Check if credentials are provided
        if sender_email and sender_password and recipient_email:
            self.enabled = True
    
    def send_email(self, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """
        Send an email notification
        
        Args:
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            print("📧 Email notifications disabled (no credentials)")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Attach plain text
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Attach HTML if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"📧 Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def notify_position_closed(self, position_data: Dict) -> bool:
        """
        Send notification when position closes
        
        Args:
            position_data: Dictionary with position details
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            return False
        
        # Extract data with proper defaults
        symbol = position_data.get('symbol', 'Unknown')
        position_type = position_data.get('type', 'Unknown')
        entry_price = position_data.get('entry_price', 0)
        close_price = position_data.get('close_price', entry_price)  # Use entry_price if close_price not available
        volume = position_data.get('volume', 0)
        profit_loss = position_data.get('profit_loss', 0)
        close_reason = position_data.get('close_reason', 'Unknown')
        ticket = position_data.get('ticket', 'N/A')
        duration = position_data.get('duration', 'N/A')
        account_balance = position_data.get('account_balance', 0)
        
        # Format values for display
        entry_price_str = f"{entry_price:.2f}" if entry_price else "N/A"
        close_price_str = f"{close_price:.2f}" if close_price else "N/A"
        volume_str = f"{volume:.2f}" if volume else "N/A"
        balance_str = f"${account_balance:,.2f}" if account_balance else "N/A"
        
        # Determine emoji based on profit/loss
        if profit_loss > 0:
            emoji = "✅ PROFIT"
            color = "green"
        elif profit_loss < 0:
            emoji = "❌ LOSS"
            color = "red"
        else:
            emoji = "⚖️ BREAKEVEN"
            color = "gray"
        
        # Create subject
        subject = f"🔔 {emoji}: {symbol} {position_type} Position Closed"
        
        # Create plain text body
        body = f"""
Gold Trading Bot - Position Closed Notification
{'=' * 50}

{emoji}
Symbol: {symbol}
Position: {position_type}
Ticket: {ticket}

Entry Price: {entry_price_str}
Close Price: {close_price_str}
Volume: {volume_str} lots

Profit/Loss: ${profit_loss:.2f}

Close Reason: {close_reason}
Duration: {duration}

Account Balance: {balance_str}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 50}
Gold Trading Bot Alert System
"""
        
        # Create HTML body
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        
        <h2 style="color: {color}; text-align: center; border-bottom: 3px solid {color}; padding-bottom: 10px;">
            {emoji}
        </h2>
        
        <h3 style="text-align: center; color: #333;">
            {symbol} {position_type} Position Closed
        </h3>
        
        <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Ticket:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Position Type:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{position_type}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Entry Price:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{entry_price_str}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Close Price:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{close_price_str}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Volume:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{volume_str} lots</td>
            </tr>
            <tr style="background-color: {color}20;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; color: {color};">Profit/Loss:</td>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; color: {color}; font-size: 18px;">
                    ${profit_loss:.2f}
                </td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Close Reason:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{close_reason}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Duration:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{duration}</td>
            </tr>
            <tr style="background-color: #e8f5e9;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; color: #2e7d32;">Account Balance:</td>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; color: #2e7d32; font-size: 16px;">{balance_str}</td>
            </tr>
        </table>
        
        <p style="text-align: center; color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px;">
            Gold Trading Bot Alert System<br>
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
</body>
</html>
"""
        
        return self.send_email(subject, body, html_body)
    
    def notify_trade_opened(self, trade_data: Dict) -> bool:
        """
        Send notification when new position opens
        
        Args:
            trade_data: Dictionary with trade details
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            return False
        
        symbol = trade_data.get('symbol', 'Unknown')
        position_type = trade_data.get('type', 'Unknown')
        entry_price = trade_data.get('entry_price', 0)
        volume = trade_data.get('volume', 0)
        stop_loss = trade_data.get('stop_loss', 'N/A')
        take_profit = trade_data.get('take_profit', 'N/A')
        ticket = trade_data.get('ticket', 'N/A')
        
        subject = f"🚀 New {position_type} Position Opened: {symbol}"
        
        body = f"""
Gold Trading Bot - New Position Opened
{'=' * 50}

Symbol: {symbol}
Position: {position_type}
Ticket: {ticket}

Entry Price: {entry_price}
Volume: {volume} lots
Stop Loss: {stop_loss}
Take Profit: {take_profit}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 50}
Gold Trading Bot Alert System
"""
        
        return self.send_email(subject, body)
    
    def notify_circuit_breaker(self, breaker_data: Dict) -> bool:
        """
        Send notification when circuit breaker activates
        
        Args:
            breaker_data: Dictionary with circuit breaker details
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            return False
        
        reason = breaker_data.get('reason', 'Unknown')
        pause_hours = breaker_data.get('pause_hours', 0)
        consecutive_losses = breaker_data.get('consecutive_losses', 0)
        percentage_losses = breaker_data.get('percentage_losses', 'N/A')
        total_pauses = breaker_data.get('total_pauses', 0)
        total_daily_loss = breaker_data.get('total_daily_loss', 0)
        current_balance = breaker_data.get('current_balance', 0)
        
        # Check if this is a daily loss limit breach
        daily_loss = breaker_data.get('daily_loss')
        loss_percentage = breaker_data.get('loss_percentage')
        starting_balance = breaker_data.get('starting_balance')
        
        if daily_loss is not None:
            # Daily Loss Limit notification
            subject = f"🔴 DAILY LOSS LIMIT REACHED - Trading Paused"
            
            body = f"""
Gold Trading Bot - DAILY LOSS LIMIT ALERT
{'=' * 50}

⚠️  DAILY LOSS LIMIT REACHED - TRADING PAUSED UNTIL MIDNIGHT

💰 Account Status:
- Starting Balance (Today): ${starting_balance:.2f}
- Current Balance: ${current_balance:.2f}
- Daily Loss: ${daily_loss:.2f} ({loss_percentage:.1f}%)

📊 Loss Details:
- Total Trades Today: Multiple
- Total Loss Today: ${abs(total_daily_loss):.2f}
- Consecutive Losses: {consecutive_losses}

⏰ Trading will automatically resume at midnight (new trading day).

💡 Tip: Consider reviewing your strategy and risk management settings.

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 50}
Gold Trading Bot Protection System
"""
        else:
            # Circuit Breaker notification
            subject = f"🔴 CIRCUIT BREAKER ACTIVATED - Trading Paused"
            
            body = f"""
Gold Trading Bot - CIRCUIT BREAKER ALERT
{'=' * 50}

⚠️  TRADING PAUSED FOR {pause_hours} HOUR(S)

Reason: {reason}

💰 Account Status:
- Current Balance: ${current_balance:.2f}
- Total Loss Today: ${abs(total_daily_loss):.2f}

📊 Loss Metrics:
- Consecutive Losses: {consecutive_losses}
- Loss Percentage (Last 10): {percentage_losses}%
- Total Pauses Today: {total_pauses}

⏰ The bot will automatically resume trading when the pause period ends.

💡 Tip: Monitor your trading strategy during pause periods.

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 50}
Gold Trading Bot Protection System
"""
        
        return self.send_email(subject, body)


def load_email_config(config_file: str = "src/configs/email_config.json") -> Optional[EmailNotifier]:
    """
    Load email configuration from JSON file
    
    Args:
        config_file: Path to email configuration file (relative to project root)
        
    Returns:
        Configured EmailNotifier instance or None
    """
    import os
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Make config_file absolute if relative
    if not os.path.isabs(config_file):
        config_file = os.path.join(project_root, config_file)
    
    try:
        # Load main config (SMTP settings)
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Load credentials from separate file
        credentials_file = config.get('credentials_file', 'src/configs/email_credentials.json')
        
        # Make credentials_file absolute if relative
        if not os.path.isabs(credentials_file):
            credentials_file = os.path.join(project_root, credentials_file)
        
        credentials = {}
        
        try:
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Credentials file not found: {credentials_file}")
            print("📧 Create email_credentials.json with your email details")
        
        notifier = EmailNotifier(
            smtp_server=config.get('smtp_server', 'smtp.gmail.com'),
            smtp_port=config.get('smtp_port', 587),
            sender_email=credentials.get('sender_email', ''),
            sender_password=credentials.get('sender_password', ''),
            recipient_email=credentials.get('recipient_email', '')
        )
        
        if notifier.enabled:
            print("✅ Email notifications enabled")
        else:
            print("⚠️  Email notifications disabled (check credentials)")
        
        return notifier
        
    except FileNotFoundError:
        print(f"⚠️  Email config file not found: {config_file}")
        print("📧 Email notifications disabled")
        return EmailNotifier()  # Return disabled notifier
    except Exception as e:
        print(f"❌ Failed to load email config: {e}")
        return EmailNotifier()


def create_email_config_template(output_file: str = "src/configs/email_config.json"):
    """
    Create a template email configuration file
    
    Args:
        output_file: Path where template will be saved (relative to project root)
    """
    import os
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Make output_file absolute if relative
    if not os.path.isabs(output_file):
        output_file = os.path.join(project_root, output_file)
    
    template = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password_here",
        "recipient_email": "recipient@example.com",
        "_note": "For Gmail, use App Password (not regular password). Enable 2FA first."
    }
    
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(template, f, indent=4)
        print(f"✅ Email config template created: {output_file}")
        print("📝 Edit this file with your email credentials")
    except Exception as e:
        print(f"❌ Failed to create template: {e}")


if __name__ == "__main__":
    # Create template
    create_email_config_template()
    
    # Test email (if configured)
    notifier = load_email_config()
    
    if notifier.enabled:
        # Test notification
        test_data = {
            'symbol': 'XAUUSD',
            'type': 'SELL',
            'entry_price': 4148.32,
            'close_price': 4135.74,
            'volume': 0.16,
            'profit_loss': 201.28,
            'close_reason': 'Take Profit Hit',
            'ticket': '5775863997',
            'duration': '45 minutes'
        }
        
        notifier.notify_position_closed(test_data)
