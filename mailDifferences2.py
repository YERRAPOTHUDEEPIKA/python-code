from reportlab.lib.pagesizes import letter,A4,landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageTemplate, PageBreak
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

# Create a custom page template
def create_custom_page_template(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    page_num_text = "Page %d" % doc.page
    canvas.drawString(20, 10, page_num_text)
    canvas.restoreState()
    
    return template
# Create a PDF document
pdf_filename = "report.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter), rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

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
        str(row["DifferenceAboveTolerance"])
    ])

# Create a table and style it
table = Table(table_data, repeatRows=1)
table_style = [
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 8),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]

# Apply text color to the "Pair" column (index 1)
pair_text_color = colors.blue  # Change to the desired color
for i in range(1, len(table_data)):
    table_style.extend([
        ('TEXTCOLOR', (1, i), (1, i), pair_text_color),
        ('FONTSIZE', (0, i), (-1, i), 8)
    ])

table.setStyle(TableStyle(table_style))


# # Create a table and style it
# table = Table(table_data)
# table.setStyle(TableStyle([
#     ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#     ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ('TEXTCOLOR', (0, 1), (-1, -1), colors.black)

# ]))

# Build the PDF document
elements = []

# Add a title to the PDF
title_style = getSampleStyleSheet()["Title"]
title_style.fontsize = 10
title = Paragraph("<font size='10' color='blue'> UniCoinDCX Rate Differences Report</font>", title_style)
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
