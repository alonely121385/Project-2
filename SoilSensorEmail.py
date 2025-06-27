#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pytz

# GPIO setup
SOIL_MOISTURE_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOIL_MOISTURE_PIN, GPIO.IN)

# Email configuration
SMTP_CONFIG = {
    "server": "smtp.qq.com",
    "port": 587,
    "sender": "3081037024@qq.com",
    "password": "uxweabuszncqdfac",  # Consider using environment variables
    "recipient": "15365075682@163.com"
}

# Daily reading schedule (24-hour format)
READING_TIMES = ["08:00", "12:00", "16:00", "20:00"]

# Plant information (customize as needed)
PLANT_INFO = {
    "name": "My Plant",
    "type": "Succulent",
    "location": "Living Room"
}

def create_email_body(status, reading_time):
    """Create a nicely formatted HTML email body"""
    emoji = "💧" if "NOT" in status else "⚠️"
    color = "green" if "NOT" in status else "red"
    
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h1 style="color: #2c3e50; text-align: center;">
                    {emoji} Plant Status Update {emoji}
                </h1>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 15px 0;">
                    <h2 style="color: {color}; margin-top: 0;">{status}</h2>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee; width: 30%;">Plant Name:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{PLANT_INFO['name']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Plant Type:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{PLANT_INFO['type']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Location:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{PLANT_INFO['location']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">Reading Time:</td>
                            <td style="padding: 8px 0;">{reading_time.strftime('%Y-%m-%d %H:%M')}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="text-align: center; color: #7f8c8d; font-size: 0.9em;">
                    This is an automated message from your Raspberry Pi Plant Monitoring System
                </p>
            </div>
        </body>
    </html>
    """

def send_email(subject, status, reading_time):
    """Send email with formatted content"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_CONFIG['sender']
        msg['To'] = SMTP_CONFIG['recipient']
        msg['Subject'] = f"{subject} - {reading_time.strftime('%H:%M')}"
        
        # Create both plain text and HTML versions
        text = f"Plant Status:\n{status}\nTime: {reading_time}\nPlant: {PLANT_INFO['name']}"
        html = create_email_body(status, reading_time)
        
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['sender'], SMTP_CONFIG['password'])
            server.send_message(msg)
        
        print(f"Email sent successfully at {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"Email sending failed: {str(e)}")

def check_soil_moisture():
    """Check soil moisture status"""
    try:
        if GPIO.input(SOIL_MOISTURE_PIN):
            return "Please water your plant", "alert"
        else:
            return "Water NOT needed", "ok"
    except Exception as e:
        return f"Error reading sensor: {str(e)}", "error"

def get_next_reading_time(time_str):
    """Calculate the next occurrence of a given time string"""
    now = datetime.now()
    reading_time = datetime.strptime(time_str, "%H:%M").replace(
        year=now.year,
        month=now.month,
        day=now.day
    )
    
    if now > reading_time:
        reading_time += timedelta(days=1)
    
    return reading_time

def daily_readings():
    """Main loop for taking scheduled readings"""
    print(f"Starting plant monitoring system at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Will take readings at: {', '.join(READING_TIMES)}")
    
    while True:
        for reading_time_str in READING_TIMES:
            next_reading = get_next_reading_time(reading_time_str)
            wait_seconds = (next_reading - datetime.now()).total_seconds()
            
            if wait_seconds > 0:
                print(f"Next reading at {reading_time_str} (in {wait_seconds/60:.1f} minutes)")
                time.sleep(wait_seconds)
            
            # Take reading
            status, status_type = check_soil_moisture()
            current_time = datetime.now()
            print(f"[{current_time.strftime('%H:%M:%S')}] Soil status: {status}")
            
            # Send email
            send_email(
                subject=f"Plant Status: {status_type.upper()}",
                status=status,
                reading_time=current_time
            )

if __name__ == "__main__":
    try:
        daily_readings()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")
