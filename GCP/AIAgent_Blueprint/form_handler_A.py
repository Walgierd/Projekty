# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file handles the logic for a multi-step form (Form A), including fetching data,
# displaying dialogs, and processing submissions.

# form_handler_A.py

import logging
import threading
import time
from datetime import datetime, timedelta
import google.auth
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
# The mail handler is abstracted. In a real scenario, this would import a module
# responsible for downloading files and sending emails.
# from mail_handler import download_drive_file_as, send_mail_with_attachments

# --- Mock/Abstracted Mail Handler Functions ---
# These functions stand in for a real mail handler to keep this module self-contained for the blueprint.
def download_drive_file_as(file_id, mime_type, filename):
    print(f"Mock download: file_id={file_id}, mime_type={mime_type}, filename={filename}")
    return (b"mock file content", filename)

def send_mail_with_attachments(to_email, subject, body_html, attachments):
    print(f"Mock email sent to {to_email} with subject '{subject}' and {len(attachments)} attachments.")
# --- End Mock ---

def get_data_from_sheet():
    """Fetches data from a predefined Google Sheet to populate form dropdowns."""
    print("(form_handler_A.py)[get_data_from_sheet] Fetching data from Google Sheets")
    # ANONYMIZED: Replace with your actual Spreadsheet ID and range.
    SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE'
    RANGE = 'Sheet1!A2:J'

    try:
        credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        sheets_service = build('sheets', 'v4', credentials=credentials)
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=RANGE
        ).execute()
        rows = result.get('values', [])
        
        # ANONYMIZED: The structure of the data is specific to the original project.
        # This should be adapted to your data schema.
        data_items = []
        for row in rows:
            item = {
                'name': row[1] if len(row) > 1 else '',
                'position': row[5] if len(row) > 5 else '',
                'phone': row[6] if len(row) > 6 else '',
                'email': row[7] if len(row) > 7 else '',
                'description': row[8] if len(row) > 8 else '',
                'photo_url': row[9] if len(row) > 9 else '',
            }
            data_items.append(item)
        print(f"(form_handler_A.py)[get_data_from_sheet] Data items: {data_items}")
        return data_items
    except Exception as e:
        logging.error(f"Error fetching from sheet: {e}", exc_info=True)
        return []


def open_form_A_dialog():
    """Opens the first step of Form A as a dialog in the chat."""
    print("(form_handler_A.py)[open_form_A_dialog] Function called")
    try:
        now_ms = int(datetime.now().timestamp() * 1000)
        sheet_data = get_data_from_sheet()
        dropdown_items = [
            {"text": item['name'], "value": item['name']}
            for item in sheet_data if item['name']
        ]
        
        # This dialog is highly customized. The fields (firma, lokalizacja, etc.)
        # should be replaced with fields relevant to your use case.
        return {
            'actionResponse': {
                'type': "DIALOG",
                'dialogAction': {
                    'dialog': {
                        'body': {
                            'sections': [{
                                'header': "Form A",
                                'widgets': [
                                    {"textInput": {"name": "field1", "label": "Field 1 (e.g., Company)"}},
                                    {"textInput": {"name": "field2", "label": "Field 2 (e.g., Location)"}},
                                    {"dateTimePicker": {"name": "date1", "label": "Date 1", "type": "DATE_ONLY", "valueMsEpoch": now_ms}},
                                    {"dateTimePicker": {"name": "time1", "label": "Time 1", "type": "TIME_ONLY"}},
                                    {"selectionInput": {
                                        "name": "dropdown1", "label": "Dropdown 1", "type": "DROPDOWN",
                                        "items": dropdown_items
                                    }},
                                    {"buttonList": {"buttons": [{
                                        "text": "Next",
                                        "onClick": {"action": {"function": "openConfirmationDialog", "interaction": "OPEN_DIALOG"}}
                                    }]}},
                                ]
                            }]
                        }
                    }
                }
            }
        }
    except Exception as e:
        logging.error(f"Error in open_form_A_dialog: {e}", exc_info=True)
        return {}

def open_confirmation_dialog(event):
    """Opens a confirmation dialog showing the data entered in the first step."""
    logging.info("Opening confirmation dialog for Form A")
    try:
        # Helper to safely extract form values
        def fetch_form_value(event, field):
            # This logic extracts values from different input types.
            # It's complex due to the chat platform's event structure.
            form_inputs = event.get('common', {}).get('formInputs', {})
            item = form_inputs.get(field, {})
            if 'stringInputs' in item:
                return item['stringInputs'].get('value', [''])[0]
            # ... (add extraction for date, time, etc. as needed)
            return ""

        # ANONYMIZED: Extract values for the fields you defined in open_form_A_dialog
        field1_val = fetch_form_value(event, "field1")
        field2_val = fetch_form_value(event, "field2")
        # ... and so on for other fields

        space_name = event.get('space', {}).get('name')
        thread_name = event.get('thread', {}).get('name')

        # The confirmation card displays the entered data.
        card_confirmation = {
            'header': "Confirm Form A Data",
            'widgets': [
                {'textParagraph': {'text': f"<b>Field 1:</b> {field1_val}"}},
                {'textParagraph': {'text': f"<b>Field 2:</b> {field2_val}"}},
                # ... display other fields
                {'buttonList': {'buttons': [{
                    'text': "Submit",
                    'onClick': {'action': {
                        'function': "submitFormA",
                        # Pass all data to the final submission function
                        'parameters': [
                            {'key': "field1", 'value': field1_val},
                            {'key': "field2", 'value': field2_val},
                            # ... other parameters
                            {'key': "space_name", 'value': space_name},
                            {'key': "thread_name", 'value': thread_name}
                        ]
                    }}
                }]}}
            ]
        }
        return {
            'actionResponse': {
                'type': "DIALOG",
                'dialogAction': {'dialog': {'body': {'sections': [card_confirmation]}}}
            }
        }
    except Exception as e:
        logging.error(f"Error in open_confirmation_dialog: {e}", exc_info=True)
        return {}

def submit_form_A(event, send_message_to_chat_func):
    """
    Final step: processes the confirmed data, generates documents, and sends notifications.
    This function runs in a background thread to avoid blocking the UI.
    """
    logging.info("Submitting Form A")
    try:
        params = event.get('common', {}).get('parameters', {})
        logging.info(f"Form parameters: {params}")
        
        # ANONYMIZED: Extract all your parameters
        field1 = params.get('field1', '')
        # ... and so on

        requester_email = event.get('user', {}).get('email', '')
        requester_name = event.get('user', {}).get('displayName', '')

        # This is a placeholder for the complex document generation logic.
        def generate_and_send():
            try:
                # 1. Define placeholders and their values from the form
                replacements = {
                    "{{Placeholder1}}": field1,
                    # ... more replacements
                }

                # 2. ANONYMIZED: IDs for templates and target folders
                template_id = "YOUR_PRESENTATION_TEMPLATE_ID"
                target_folder_id = "YOUR_TARGET_DRIVE_FOLDER_ID"
                checklist_file_id = "YOUR_CHECKLIST_FILE_ID"

                # 3. Copy and fill the template
                logging.info("Starting document generation...")
                new_file_id = copy_and_fill_template(template_id, f"{field1} - Generated Document", target_folder_id, replacements)
                presentation_url = f"https://docs.google.com/presentation/d/{new_file_id}/edit"
                logging.info(f"Document URL: {presentation_url}")

                # 4. Share files with the relevant user
                share_file(new_file_id, requester_email)
                checklist_link = get_sharable_link(checklist_file_id, requester_email)

                # 5. Send a confirmation message back to the chat
                space_name = params.get('space_name')
                thread_name = params.get('thread_name')
                if space_name and thread_name:
                    send_message_to_chat_func(
                        space_name,
                        thread_name,
                        f"🎉 Done! The document for {field1} has been generated.\n"
                        f"👉 Presentation: {presentation_url}\n"
                        f"📋 Checklist: {checklist_link}\n"
                    )
                
                # 6. (Optional) Email the documents as attachments
                send_documents_by_email(
                    presentation_id=new_file_id,
                    checklist_id=checklist_file_id,
                    recipient_email=requester_email,
                    recipient_name=requester_name,
                    title=field1
                )

            except Exception as e:
                logging.error(f"Error in generation thread: {e}", exc_info=True)

        # Run the generation process in the background
        threading.Thread(target=generate_and_send).start()
        
        # Return an immediate response to the user
        return {
            'actionResponse': {'type': "NEW_MESSAGE"},
            'text': "Processing your request... The document will be ready in about 2 minutes."
        }
    except Exception as e:
        logging.error(f"Error in submit_form_A: {e}", exc_info=True)
        return {
            'actionResponse': {'type': "NEW_MESSAGE"},
            'text': f"❌ An error occurred: {e}"
        }

# --- Google Drive/Slides Helper Functions (Abstracted) ---
# These functions contain the core logic for interacting with Google APIs.

def copy_and_fill_template(template_id, new_title, folder_id, replacements):
    """Copies a Google Slides template, fills placeholders, and returns the new file ID."""
    logging.info("Copying and filling template")
    # This would involve calls to Google Drive API to copy and Google Slides API to update text/images.
    # This is a highly complex part of the original code and is abstracted here.
    # Step 1: drive_service.files().copy(...)
    # Step 2: slides_service.presentations().batchUpdate(...)
    new_file_id = "mock_new_file_id" # Placeholder
    print(f"Created and filled new file: {new_file_id}")
    return new_file_id

def share_file(file_id, email):
    """Shares a Google Drive file with a user."""
    logging.info(f"Sharing {file_id} with {email}")
    # This would involve a call to drive_service.permissions().create(...)
    print("Mock share complete.")

def get_sharable_link(file_id, email):
    """Shares a file and returns its web link."""
    share_file(file_id, email)
    return f"https://docs.google.com/file/d/{file_id}/view"

def send_documents_by_email(presentation_id, checklist_id, recipient_email, recipient_name, title):
    """Downloads documents and emails them as attachments."""
    logging.info(f"Sending documents for '{title}' to {recipient_email}")
    
    # 1. Download files from Drive
    checklist_bytes, checklist_filename = download_drive_file_as(checklist_id, 'application/pdf', "Checklist.pdf")
    ppt_bytes, ppt_filename = download_drive_file_as(presentation_id, 'application/vnd.openxmlformats-officedocument.presentationml.presentation', f"{title}.pptx")

    # 2. Prepare attachments
    attachments = []
    if ppt_bytes: attachments.append({'content': ppt_bytes, 'filename': ppt_filename, 'mime': '...'})
    if checklist_bytes: attachments.append({'content': checklist_bytes, 'filename': checklist_filename, 'mime': 'application/pdf'})

    # 3. Send email
    subject = f"Your generated documents for {title}"
    body = f"Hello {recipient_name},<br><br>Please find your documents attached."
    send_mail_with_attachments(recipient_email, subject, body, attachments)
    print("Email with documents sent.")
