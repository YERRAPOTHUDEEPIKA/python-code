digits = "0123456789"
OTP = ""

for i in range(6):
    OTP += digits[math.floor(random.random() * 10)]

otp_message = OTP + " is your OTP"

s = smtplib.SMTP('mail.kappmedia.com', 587)
s.starttls()

# Replace with your Gmail email and password or use environment variables for better security
email_address = "keerthana@kappsoft.com"
email_password = "KeerthiLalitha@123"

try:
    s.login(email_address, email_password)
    email_id = input("Enter your email: ")
    s.sendmail(email_address, email_id, otp_message)
    print("OTP has been sent to your email.")

    a = input("Enter Your OTP >>: ")
    if a == OTP:
        print("Verified")
    else:
        print("Please Check your OTP again")
except smtplib.SMTPAuthenticationError:
    print("Authentication failed. Make sure to enable 'Less secure apps' in your Gmail settings.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    s.quit()
