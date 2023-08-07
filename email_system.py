import imaplib
import email
from email.header import decode_header

def get_text_plain_part(msg):
    text_plain = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                text_plain = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                break
    else:
        if msg.get_content_type() == "text/plain":
            text_plain = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
    return text_plain

def format_email_headers(headers):
    decoded_headers = []
    for header, value in headers:
        decoded_header = decode_header(value)
        if decoded_header[0][1]:
            decoded_value = decoded_header[0][0].decode(decoded_header[0][1])
        else:
            decoded_value = decoded_header[0][0]
        decoded_headers.append((header, decoded_value))
    return decoded_headers

def read_email_content_by_uid(imap_server, username, password, email_uid):
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)

    # Log in with your credentials
    mail.login(username, password)

    # Select the mailbox from which you want to read emails
    mailbox = "INBOX"  # Change this to the desired mailbox if needed
    mail.select(mailbox)

    # Fetch the email content using its UID
    status, data = mail.uid('fetch', email_uid, '(BODY.PEEK[])')
    
    email_content = None
    if status == 'OK':
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract email headers and format them
       

        # Get and display plain text part of the email
        text_plain = get_text_plain_part(msg)

    mail.close()
    mail.logout()

    return text_plain






def get_last_email_uid(imap_server, username, password):
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)

    # Log in with your credentials
    mail.login(username, password)

    # Select the mailbox from which you want to get emails
    mailbox = "INBOX"  # Change this to the desired mailbox if needed
    mail.select(mailbox)

    # Use the SEARCH command with the HEADER criteria to fetch the UID of the most recent email
    status, data = mail.uid('search', None, '(HEADER Subject ".*")')

    last_email_uid = None
    if status == 'OK':
        # Get a list of UIDs (if any)
        uid_list = data[0].split()
        if uid_list:
            # Select the last UID, which represents the most recent email
            last_email_uid = uid_list[-1]

    # Close the mailbox and log out
    mail.close()
    mail.logout()

    return last_email_uid

def delete_email_by_uid(imap_server, username, password, email_uid):
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)

    # Log in with your credentials
    mail.login(username, password)

    # Select the mailbox from which you want to delete emails
    mailbox = "INBOX"  # Change this to the desired mailbox if needed
    mail.select(mailbox)

    # Mark the email for deletion using the UID
    if email_uid:
        # Mark the email for deletion without generating server responses
        mail.uid('store', email_uid, '+FLAGS', '(\\Deleted)')

        # Expunge the mailbox to permanently delete the marked email
        mail.expunge()

    # Close the mailbox and log out
    mail.close()
    mail.logout()
