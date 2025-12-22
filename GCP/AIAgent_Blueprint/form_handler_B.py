# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file contains the logic for handling a multi-step form (Form B), which includes
# routing to different sub-handlers based on user selection.

# form_handler_B.py

import logging
import threading
import re
import google.auth
from datetime import datetime
from googleapiclient.discovery import build
from chat_handler import get_ai_response

# Import sub-handlers for different branches of Form B
import form_handler_B_sub_A
import form_handler_B_sub_B

# --- SHARED UTILITY FUNCTIONS ---

def fetch_form_value(event, field):
    """Safely extracts a value from a form submission event."""
    form_inputs = event.get('common', {}).get('formInputs', {})
    item = form_inputs.get(field, {})
    if 'stringInputs' in item:
        return item['stringInputs'].get('value', [''])[0]
    return ""

def sum_time_fields(*fields):
    """
    Parses and sums time strings (e.g., "2 dni", "4h", "1+6") into a standardized format.
    Example: sum_time_fields("2 dni", "4h") -> "2 dni + 4 godzin zdalnie"
    """
    total_days = 0
    total_hours = 0
    for field in fields:
        if not field: continue
        # Regex to find days and hours
        d_match = re.search(r'(\d+)\s*(?:dni|d)\b', field, re.I)
        h_match = re.search(r'(\d+)\s*(?:godzin|h|g)\b', field, re.I)
        
        if d_match: total_days += int(d_match.group(1))
        if h_match: total_hours += int(h_match.group(1))
        
        # Handle compact format like "2+4"
        if not d_match and not h_match and '+' in field:
            parts = field.replace(' ', '').split('+')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                total_days += int(parts[0])
                total_hours += int(parts[1])

    parts = []
    if total_days > 0: parts.append(f"{total_days} {'dzień' if total_days == 1 else 'dni'}")
    if total_hours > 0: parts.append(f"{total_hours} {'godzina' if total_hours == 1 else 'godzin'}")
    
    return " + ".join(parts) if parts else ""

def copy_presentation(template_id, client_name, target_folder_id):
    """Copies a Google Slides presentation to a new file."""
    logging.info("Copying presentation template.")
    # This is an abstraction. The actual implementation requires Google Drive API calls.
    print(f"Mock copy: template '{template_id}' to new file for '{client_name}' in folder '{target_folder_id}'.")
    return "new_mock_file_id"

def fill_placeholders_in_presentation(presentation_id, replacements):
    """Fills placeholders in a Google Slides presentation."""
    logging.info(f"Filling placeholders for presentation {presentation_id}.")
    # This is an abstraction. The actual implementation requires Google Slides API calls.
    print(f"Mock fill: {len(replacements)} replacements applied.")

def share_presentation_with_user(file_id, user_email):
    """Shares a Google Drive file with a specific user."""
    logging.info(f"Sharing file {file_id} with {user_email}.")
    # This is an abstraction. The actual implementation requires Google Drive API calls.
    print("Mock share complete.")

# --- FORM B: STEP 1 (Initial Dialog) ---

def open_form_B_dialog():
    """
    Step 1: Displays the initial dialog for Form B, allowing the user to choose a sub-type
    and enter initial notes.
    """
    print("(form_handler_B.py)[open_form_B_dialog] Opening dialog.")
    try:
        widgets = [
            {"textParagraph": {"text": "<b>Choose a sub-type for Form B:</b>"}},
            {"selectionInput": {
                "name": "form_b_subtype",
                "label": "Sub-type",
                "type": "DROPDOWN",
                "items": [
                    {"text": "Sub-type A", "value": "SUB_A", "selected": True},
                    {"text": "Sub-type B", "value": "SUB_B"}
                ]
            }},
            {"divider": {}},
            {"textInput": { 
                "name": "notes", 
                "label": "Paste notes from the client meeting", 
                "type": "MULTIPLE_LINE" 
            }},
            {"divider": {}},
            {"buttonList": {"buttons": [{
                "text": "Next (Fill Details)",
                "onClick": {"action": {"function": "route_form_B_step2", "interaction": "OPEN_DIALOG"}}
            }]}}
        ]
        return {
            "actionResponse": {
                "type": "DIALOG",
                "dialogAction": {
                    "dialog": {
                        "body": {
                            "sections": [{
                                "header": "Form B Generator (Step 1: Choice)",
                                "widgets": widgets
                            }]
                        }
                    }
                }
            }
        }
    except Exception as e:
        logging.error(f"Error in open_form_B_dialog: {e}", exc_info=True)
        return {}

# --- FORM B: STEP 2 (Router) ---

def route_form_B_step2(event, send_message_to_chat):
    """
    Router: Checks the selected sub-type and forwards the event to the
    appropriate sub-handler to display the next step of the form.
    """
    subtype = fetch_form_value(event, "form_b_subtype")
    logging.info(f"Selected Form B sub-type: {subtype}")

    if subtype == "SUB_B":
        # Delegate to the handler for Sub-type B
        return form_handler_B_sub_B.open_subtype_B_dialog(event, send_message_to_chat)
    else:
        # Default to the handler for Sub-type A
        return form_handler_B_sub_A.open_subtype_A_dialog(event, send_message_to_chat)
