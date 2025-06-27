import RPi.GPIO as GPIO
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# GPIO setup
channel = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

# Email setup
SMTP_SERVER = "smtp.gmail.com"  # Use your email provider's SMTP server
SMTP_PORT = 587
EMAIL_ADDRESS = "youremail@example.com"  # Replace with your email address
EMAIL_PASSWORD = "yourpassword"         # Replace with your email password
TO_EMAIL = "recipient@example.com"      # Replace with recipient's email address

# Function to send email
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check soil moisture
def check_soil_moisture():
    if GPIO.input(channel):  # No water detected
        return "Please water your plant"
    else:  # Water detected
        return "Water NOT needed"

# Function to take four daily readings
def daily_readings():
    # Set daily times for the readings
    reading_times = ["08:00", "12:00", "16:00", "20:00"]

    for time_str in reading_times:
        # Wait until the scheduled time
        now = datetime.now()
        scheduled_time = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        if now > scheduled_time:
            scheduled_time = scheduled_time.replace(day=now.day + 1)

        time_to_wait = (scheduled_time - now).total_seconds()
        print(f"Waiting until {time_str} for the next reading...")
        time.sleep(time_to_wait)

        # Check soil moisture and send an email
        plant_status = check_soil_moisture()
        print(f"Reading at {time_str}: {plant_status}")
        send_email(subject="Plant Status Update", body=f"Time: {time_str}\nStatus: {plant_status}")

# Main function
if __name__ == "__main__":
    try:
        print("Starting SoilSensorEmail script...")
        daily_readings()
    except KeyboardInterrupt:
        print("Script interrupted by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up.")
