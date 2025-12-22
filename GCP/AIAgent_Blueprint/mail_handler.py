# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file handles sending emails, including with attachments downloaded from Google Drive.
# It also includes setup for background task processing with Redis and RQ.

# mail_handler.py

import os
import base64
import logging
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from chat_handler import send_message_to_chat
from rq import Queue
from redis import Redis

# --- Configuration ---
# It is strongly recommended to load credentials from environment variables or a secure secret manager,
# rather than a plain JSON file.
try:
    # Example of loading from a config file (not recommended for production)
    # with open('mail_config.json', 'r') as f:
    #     mail_config = json.load(f)
    # SMTP_SERVER = mail_config.get('smtp_server', 'smtp.your-domain.com')
    # SMTP_PORT = mail_config.get('smtp_port', 587)
    # SMTP_EMAIL = mail_config.get('email')
    # SMTP_PASSWORD = mail_config.get('password')
    
    # Example of loading from environment variables (recommended)
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.your-domain.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_EMAIL = os.environ.get('SMTP_EMAIL')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

except (FileNotFoundError, KeyError) as e:
    logging.error(f"Could not load mail configuration: {e}. Please set environment variables.")
    SMTP_EMAIL = None # Ensure the app can start but emailing will fail.

# --- Background Task Queue Setup ---
# This uses Redis and RQ to run long-running tasks (like document generation) in the background.
try:
    redis_conn = Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
    q = Queue(connection=redis_conn)
    logging.info("Successfully connected to Redis for background tasks.")
except Exception as e:
    logging.error(f"Could not connect to Redis: {e}. Background tasks will not work.")
    q = None

def download_drive_file_as(file_id, export_mime, filename):
    """
    Downloads a file from Google Drive, exporting it to a specified MIME type.
    Used for converting Google Docs/Slides to PDF/PPTX.
    """
    import google.auth
    from googleapiclient.discovery import build
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    try:
        credentials, _ = google.auth.default(scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=credentials)
        request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime)
        data = request.execute()
        return data, filename
    except Exception as e:
        logging.error(f"(mail_handler.py)[download_drive_file_as] Error downloading file: {e}", exc_info=True)
        return None, filename

def send_mail_with_attachments(
    to_email,
    subject,
    body_html,
    attachments=None,
    space_name=None,
    thread_name=None,
    chat_notify_text=None
):
    """
    Sends an email using SMTP with optional attachments and a chat notification.
    """
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        logging.error("SMTP credentials are not configured. Cannot send email.")
        return

    print(f"(mail_handler.py)[send_mail_with_attachments] Sending email to {to_email} with subject '{subject}'.")
    try:
        message = MIMEMultipart()
        message['To'] = to_email
        message['From'] = f"AI Agent <{SMTP_EMAIL}>" # Anonymized sender
        message['Subject'] = subject

        message.attach(MIMEText(body_html, 'html'))

        if attachments:
            for att in attachments:
                if not att.get('content') or not att.get('mime'):
                    continue
                part = MIMEBase(*att['mime'].split('/'))
                part.set_payload(att['content'])
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{att["filename"]}"')
                message.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, message.as_string())
        logging.info(f"(mail_handler.py)[send_mail_with_attachments] Message sent to {to_email}")

        # Send a notification to Google Chat if requested
        if space_name and thread_name:
            notify_text = chat_notify_text or f"An email has been sent to {to_email}."
            send_message_to_chat(space_name, thread_name, notify_text)

    except Exception as e:
        logging.error(f"(mail_handler.py)[send_mail_with_attachments] SMTP Error: {e}", exc_info=True)

def enqueue_generation_task(form_data):
    """
    Enqueues a long-running document generation task to be processed by a background worker.
    """
    if q:
        # The function to be executed in the background and its arguments are passed here.
        # 'generate_and_send' would be a function defined in the form handler.
        # q.enqueue(generate_and_send, form_data)
        logging.info("Task enqueued for background processing.")
        return {
            'actionResponse': {'type': "NEW_MESSAGE"},
            'text': "Your request is being processed in the background. You will be notified upon completion."
        }
    else:
        logging.error("Redis queue is not available. Cannot enqueue task.")
        return {
            'actionResponse': {'type': "NEW_MESSAGE"},
            'text': "Error: Could not connect to the background task processor."
        }
