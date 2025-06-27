import smtplib
from email.message import EmailMessage

#Set the sender email and password and recipient email
from_email_addr ="3081037024@qq.com"
from_email_pass ="uxweabuszncqdfac"
to_email_addr ="15365075682@163.com"

# Create a message object
msg = EmailMessage()

# Set the email body
body ="Hello from Raspberry Pi"
msg.set_content(body)

msg['From'] = from_email_addr
msg['To'] = to_email_addr

msg['Subject'] = 'TEST EMAIL'

server = smtplib.SMTP('smtp.qq.com', 587)
server.starttls()

# Login to the SMTP server
server.login(from_email_addr, from_email_pass)

# Send the message
server.send_message(msg)
print('Email sent')

#Disconnect from the server
server.quit()
