from reportlab.lib.pagesizes import legal, letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
# import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import pymongo
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta

# Connect to MongoDB (replace with your database connection details)
Prices_dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
Prices_db = Prices_dbclient["Prices"]
Differences = Prices_db["Differences"]

#Find data for 10 hours from previous minute
before1min = datetime.strftime(datetime.now()-timedelta(minutes=1),"%Y-%m-%dT%H:%M:00.000+00:00")
yyyy1 = int(before1min[0:4])
mm1 = int(before1min[5:7])
dd1 = int(before1min[8:10])
hh1 = int(before1min[11:13])
mts1 = int(before1min[14:16])
#print(yyyy, mm, dd, hh, mts)
search_to_time = datetime(yyyy1,mm1,dd1,hh1,mts1,0)
before10hours = datetime.strftime(datetime.now()-timedelta(hours=10),"%Y-%m-%dT%H:%M:00.000+00:00")
yyyy2 = int(before10hours[0:4])
mm2 = int(before10hours[5:7])
dd2 = int(before10hours[8:10])
hh2 = int(before10hours[11:13])
mts2 = int(before10hours[14:16])
search_from_time = datetime(yyyy2,mm2,dd2,hh2,mts2,0)
#print(search_from_time, search_to_time)
#s = input('...?')
data = list(Differences.find({'DifferenceTimeStamp': { '$gte': search_from_time, '$lte': search_to_time },'DifferenceIsAboveTolerance':'Yes'}).sort([('PriceTimeStamp', -1)]))
#print(data)
# ReportFrom = datetime.strftime(data[0].get('DifferenceTimeStamp'),"%Y-%m-%d:%H:%M")
ReportFrom = datetime.strftime(data[0].get('DifferenceTimeStamp'), "%Y-%m-%d:%H:%M")
lastelement = len(data) - 1
ReportTo = datetime.strftime(data[lastelement].get('DifferenceTimeStamp'), "%Y-%m-%d:%H:%M")
# ReportTo = datetime.strftime(data[].get('DifferenceTimeStamp'),"%Y-%m-%d:%H:%M")
# Query the database and retrieve data into a Pandas DataFrame

df = pd.DataFrame(data)
#print(df)

# Create a PDF document
pdf_filename = "report.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter))
#doc= canvas.Canvas(pdf_filename, pagesize=(landscape(letter)))


# Create a list to hold the table data
table_data = []

# Add table headers

table_data.append(["Difference Time Stamp", "Pair", "Difference With Exchange","Whether above Tolerance", "Actual Diff Bid", "Actual Diff Ask", "Actual Diff Last","Absolute Max Diff"])

# Extract data from the DataFrame and add it to the table
for _, row in df.iterrows():
    table_data.append([
        str(row["DifferenceTimeStamp"]),
        str(row["Pair"]),
        str(row["DifferenceWithExchange"]),
        str(row["DifferenceIsAboveTolerance"]),
        str(row["ActualDiffBid"]),
        str(row["ActualDiffAsk"]),
        str(row["ActualDiffLast"]),
        str(row["AbsMaxDiff"]),
       
    ])

# Create a table and style it
table = Table(table_data)
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
# table = Table(table_data, colWidths=[2*inch]*8)
# table.setStyle(TableStyle([
#     ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
#     ('FONTSIZE', (0, 0), (-1, 0), 8),
#     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#     ('GRID', (0, 0), (-1, -1), 1, colors.black),

# ]))

# Build the PDF document
elements = []

# Add a title to the PDF
title_style = getSampleStyleSheet()["Title"]
text_for_title = "<font size = '10'>UniCoinDCX Rate Differences Report  From "+ReportFrom+" To "+ReportTo+"</font>"
title = Paragraph(text_for_title, title_style)
elements.append(title)

# Add the table to the PDF
elements.append(table)

# Build the PDF document
doc.build(elements)

print(f"PDF report created: {pdf_filename}")

# Define the email subject and message text
mess_subject = "UniCoinDCX Rate Differences Report"+ " From "+ReportFrom+" To "+ReportTo
messtext = 'Please find attached the UniCoinDCX Rate Differences Report.'+ " From "+ReportFrom+" To "+ReportTo

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
