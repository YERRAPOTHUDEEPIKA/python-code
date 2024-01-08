import imaplib
import email
from email.header import decode_header
from pymongo import MongoClient

# Function to decode email subjects
def decode_subject(encoded_subject):
    if isinstance(encoded_subject, bytes):
        decoded, encoding = decode_header(encoded_subject)[0]
        if encoding:
            return decoded.decode(encoding)
        else:
            return str(decoded)
    else:
        return encoded_subject

# MongoDB credentials
mongo_uri = "mongodb+srv://yerrapothudeepika:Deepika2117@cluster0.8n3ryuc.mongodb.net"
client = MongoClient(mongo_uri)
maildb = client.mail  # Replace 'your_database' with your actual database name
mailcollection = maildb.emails  # Collection to store emails

# Email credentials
email_address = "deepika@kappsoft.com"
email_password = "Deepik@2117"

# Connect to the IMAP server
mail = imaplib.IMAP4_SSL("mail.kappmedia.com")  # Update with your email provider's IMAP server

# Login to the email account
mail.login(email_address, email_password)

# Select the mailbox you want to read emails from (e.g., "inbox")
mail.select("inbox")

# Search for all emails with the specified subject
status, messages = mail.search(None, '(SUBJECT "KAPPSOFT ATTENDANCE")')

# Get the list of email IDs
email_ids = messages[0].split()

# Loop through the email IDs in reverse order to get the latest emails first
for email_id in reversed(email_ids):
    # Fetch the email based on its ID
    status, msg_data = mail.fetch(email_id, "(RFC822)")

    # Get the email content
    raw_email = msg_data[0][1]
    email_message = email.message_from_bytes(raw_email)

    # Get the subject and sender of the email
    subject = decode_subject(email_message.get("Subject", ""))
    sender = email.utils.parseaddr(email_message.get("From", ""))[1]

    # If the email is a multipart message, extract the text part
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8")
                break
    else:
        # If the email is not multipart, simply extract the body
        body = email_message.get_payload(decode=True).decode("utf-8")

    # Create a document to be inserted into MongoDB
    email_document = {
        "subject": subject,
        "sender": sender,
        "body": body
    }

    # Insert the document into the MongoDB collection
    mailcollection.insert_one(email_document)

# Logout from the email account
mail.logout()
