# Add a title to the PDF
text_for_title = f"<font size={custom_style.fontSize}>UniCoinDCX Rate Differences Report  From {ReportFrom} To {ReportTo}</font>"
title = Paragraph(text_for_title, custom_style)
elements.append(title)
table_data = [
    ["Difference Time Stamp", "Pair", "Difference With Exchange", "Whether above Tolerance", "Actual Diff Bid", "Actual Diff Ask", "Actual Diff Last", "Absolute Max Diff"]
]

# Add the table to the PDF
elements.append(table)

# Build the PDF document
doc.build(elements)

print(f"PDF report created: {pdf_filename}")

# Define the email subject and message text
mess_subject = f"UniCoinDCX Rate Differences Report From {ReportFrom} To {ReportTo}"
messtext = f"Please find attached the UniCoinDCX Rate Differences Report. From {ReportFrom} To {ReportTo}"

# Send the email with the PDF attachment
def send_the_mail():
    global messtext, mess_subject
    receiver = "ramadas@kappsoft.com"
    sender = "idle_trigger@kappsoft.com"
    empassword = "dR7*CPcJ2DZ=<bJX"

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = mess_subject

    # Attach the PDF report to the email
    pdf_attachment = open(pdf_filename, 'rb')
    pdf_base = MIMEBase('application', 'octet-stream')
    pdf_base.set_payload(pdf_attachment.read())
    encoders.encode_base64(pdf_base)
    pdf_base.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
    message.attach(pdf_base)

    # Attach the text message
    message.attach(MIMEText(messtext, 'plain'))

    # Connect to the SMTP server and send the email
    try:
        mailsession = smtplib.SMTP('your_email_server_here', EMAIL_PORT, timeout=EMAIL_TIMEOUT)
        mailsession.starttls()
        mailsession.login(sender, empassword)
        mailsession.sendmail(sender, receiver, message.as_string())
        mailsession.quit()
        print(f"Email sent successfully at {str(datetime.now())}")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")

# Call the send_the_mail function to send the email with the PDF attachment
send_the_mail()