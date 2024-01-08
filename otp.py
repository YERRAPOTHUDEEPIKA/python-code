import os
import random
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendotp(emailid):
    receiver = emailid
    digits = "0123456789"
    OTP = ""
    for i in range(5):
        OTP += random.choice(digits)  # Generate a random digit
    otpgentime = time.time()
    print("Generated OTP:", OTP)

    message = MIMEMultipart()
    message['From'] = "deepika@kappsoft.com"
    message['To'] = receiver
    message['Subject'] = " OTP for Work Invoice Reset Password "
    message.attach(MIMEText(OTP, 'plain'))
    mailsession = smtplib.SMTP('mail.kappmedia.com', 587, timeout=360)
    mailsession.starttls()
    sender = "deepika@kappsoft.com"
    empassword = "Deepik@2117"
    try:
        print("Attempting to log in...")
        mailsession.login(sender, empassword)
        print("Logged in successfully.")
        text = message.as_string()
        print("Sending email...")
        print("From:", sender)
        print("To:", receiver)
        print("Email content:\n", text)
        mailsession.sendmail(sender, receiver, text)
        print("Email sent successfully.")
        mailsession.quit()
        return OTP, otpgentime
    except Exception as e:
        print("Email sending failed:", str(e))
        return None, None

# Test the function
otp, otpgen_time = sendotp("madhana@kappsoft.com")
if otp is not None:
    print("OTP sent:", otp)
    print("OTP generation time:", otpgen_time)
else:
    print("OTP sending failed.")
