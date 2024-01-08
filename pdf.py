from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import pymongo
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Connect to MongoDB (replace with your database connection details)
Prices_dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
Prices_db = Prices_dbclient["Prices"]
Differences = Prices_db["Differences"]

# Query the database and retrieve data into a Pandas DataFrame
data = list(Differences.find())  # Retrieve all documents from the collection
df = pd.DataFrame(data)

# Create a PDF document
pdf_filename = "report.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

# Create a list to hold the table data
table_data = []

# Add table headers
table_data.append(["DifferenceTimeStamp", "Pair", "DifferenceWithExchange", "DifferenceAboveTolerance"])

# Extract data from the DataFrame and add it to the table
for _, row in df.iterrows():
    table_data.append([
        str(row["DifferenceTimeStamp"]),
        str(row["Pair"]),
        str(row["DifferenceWithExchange"]),
        str(row["DifferenceAboveTolerance"]),
    ])

# Create a table and style it
table = Table(table_data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),

]))

# Build the PDF document
elements = []

# Add a title to the PDF
title_style = getSampleStyleSheet()["Title"]
title = Paragraph("UniCoinDCX Rate Differences Report", title_style)
elements.append(title)

# Add the table to the PDF
elements.append(table)

# Build the PDF document
doc.build(elements)

print(f"PDF report created: {pdf_filename}")

# Define the email subject and message text
mess_subject = "UniCoinDCX Rate Differences Report"
messtext = 'Please find attached the UniCoinDCX Rate Differences Report.'

# Send the email with the PDF attachment
def send_the_mail():
    global messtext, mess_subject
    receiver = "madhana@kappsoft.com"
    sender = "deepika@kappsoft.com"
    empassword = "Deepik@2117"

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
        mailsession = smtplib.SMTP('mail.kappmedia.com', 587, timeout=360)
        mailsession.starttls()
        mailsession.login(sender, empassword)
        mailsession.sendmail(sender, receiver, message.as_string())
        mailsession.quit()
        print(f"Email sent successfully at {str(datetime.now())}")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")

# Call the send_the_mail function to send the email with the PDF attachment
send_the_mail()
