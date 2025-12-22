# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file contains the specific logic for "Sub-type A" of Form B.
# It defines the dialogs, AI prompts, and submission logic for this branch of the form.

# form_handler_B_sub_A.py

import logging
import threading
import json
from chat_handler import get_ai_response, send_message_to_chat
# Import shared utility functions from the main Form B handler
import form_handler_B as utils 

# --- Configuration for Sub-type A ---
# ANONYMIZED: Replace with your actual template and folder IDs.
TEMPLATE_ID = "YOUR_SUBTYPE_A_TEMPLATE_ID"
TARGET_FOLDER_ID = "YOUR_SUBTYPE_A_TARGET_FOLDER_ID"

def open_subtype_A_dialog(event, send_message_to_chat):
    """
    Step 2 (Sub-type A): Displays a form with fields specific to this sub-type.
    """
    print("(form_handler_B_sub_A.py)[open_subtype_A_dialog] Opening dialog.")
    notes_value = utils.fetch_form_value(event, "notes")

    # These fields are specific to the original project's "PSE" offer.
    # They should be replaced with fields relevant to your "Sub-type A".
    widgets = [
        {"textInput": {"name": "notes", "label": "Notes (editable)", "type": "MULTIPLE_LINE", "value": notes_value}},
        {"divider": {}},
        {"textParagraph": {"text": "<b>Time Data (Sub-type A):</b>"}},
        {"textInput": {"name": "time_field_1", "label": "Time for Task 1 (e.g., 2+4)"}},
        {"textInput": {"name": "time_field_2", "label": "Time for Task 2 (e.g., 1 day)"}},
        {"divider": {}},
        {"textParagraph": {"text": "<b>Pricing and Discount:</b>"}},
        {"textInput": {"name": "price_phase1_before", "label": "Price Phase 1 (Net)"}},
        {"textInput": {"name": "price_phase2_before", "label": "Price Phase 2 (Net)"}},
        {"textInput": {"name": "discount", "label": "Discount (%)"}},
        {"divider": {}},
        {"buttonList": {"buttons": [{
            "text": "Process with AI",
            "onClick": {"action": {"function": "form_handler_B_sub_A.build_form_B_step3_ai", "interaction": "OPEN_DIALOG"}}
        }]}}
    ]
    return {
        "actionResponse": {
            "type": "DIALOG",
            "dialogAction": {
                "dialog": {
                    "body": {
                        "sections": [{
                            "header": "Details for Sub-type A (Step 2/4)",
                            "widgets": widgets
                        }]
                    }
                }
            }
        }
    }

def call_ai_to_extract_data(notes: str, raw_time1: str, raw_time2: str) -> dict:
    """
    Calls the AI model with a specific prompt to extract and structure data for Sub-type A.
    """
    # ANONYMIZED: This prompt is highly specific to the original project.
    # It needs to be completely rewritten to match your data structure and requirements.
    prompt = f"""
    You are an AI assistant. Your task is to process raw notes and convert them
    into a structured JSON object for generating a "Sub-type A" document.

    RAW NOTES:
    \"\"\"{notes}\"\"\"

    RAW TIME INPUTS:
    time_field_1="{raw_time1}"
    time_field_2="{raw_time2}"

    EXPECTED JSON STRUCTURE:
    - "client_name": The name of the client.
    - "project_title": A title for the project.
    - "situation_summary": A professional summary of the client's situation.
    - "project_goals": The goals of the project.
    - "phase1_description": Description of the first phase.
    - "phase1_time": Standardized time for the first phase.
    - "phase2_description": Description of the second phase.
    - "phase2_time": Standardized time for the second phase.

    Return ONLY the JSON object.
    """
    try:
        response_text = get_ai_response(prompt, research_mode=False)
        # Basic JSON cleaning
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start == -1: return {}
        extracted_data = json.loads(response_text[start:end+1])
        
        # Post-process time fields using the shared utility
        if "phase1_time" in extracted_data:
            extracted_data["phase1_time"] = utils.sum_time_fields(extracted_data["phase1_time"])
        if "phase2_time" in extracted_data:
            extracted_data["phase2_time"] = utils.sum_time_fields(extracted_data["phase2_time"])
            
        return extracted_data
    except Exception as e:
        logging.error(f"Error processing AI response for Sub-type A: {e}")
        return {}

def build_form_B_step3_ai(event, send_message_to_chat):
    """
    Step 3 (Sub-type A): Displays a verification dialog with data extracted by the AI.
    The user can edit the fields before final submission.
    """
    print("(form_handler_B_sub_A.py)[build_form_B_step3_ai] Building verification dialog.")
    try:
        # Fetch data from the previous form step
        notes = utils.fetch_form_value(event, "notes")
        raw_time1 = utils.fetch_form_value(event, "time_field_1")
        raw_time2 = utils.fetch_form_value(event, "time_field_2")
        price1 = utils.fetch_form_value(event, "price_phase1_before")
        price2 = utils.fetch_form_value(event, "price_phase2_before")
        discount = utils.fetch_form_value(event, "discount")

        space_name = event.get('space', {}).get('name')
        thread_name = event.get('thread', {}).get('name')

        def process_and_display():
            # Call the AI in a background thread
            extracted = call_ai_to_extract_data(notes, raw_time1, raw_time2)
            
            # Add pricing info to the data
            extracted["price_phase1_before"] = price1
            extracted["price_phase2_before"] = price2
            extracted["discount"] = discount
            
            # ANONYMIZED: Build a card with input fields pre-filled with AI-extracted data.
            # The field names here should match the keys from your AI prompt's JSON structure.
            widgets = [
                {"textInput": {"name": "client_name", "label": "Client Name", "value": extracted.get("client_name", "")}},
                {"textInput": {"name": "project_title", "label": "Project Title", "value": extracted.get("project_title", "")}},
                # ... more fields for situation_summary, project_goals, etc.
                {"divider": {}},
                {"textInput": {"name": "price_phase1_before", "label": "Price Phase 1", "value": extracted.get("price_phase1_before", "")}},
                {"textInput": {"name": "price_phase2_before", "label": "Price Phase 2", "value": extracted.get("price_phase2_before", "")}},
                {"textInput": {"name": "discount", "label": "Discount (%)", "value": extracted.get("discount", "")}},
                {"buttonList": {"buttons": [{
                    "text": "Confirm Data",
                    "onClick": {"action": {"function": "form_handler_B_sub_A.openConfirmation", "interaction": "OPEN_DIALOG"}}
                }]}}
            ]
            card = {'header': {'title': 'Verify Extracted Data (Sub-type A)'}, 'sections': [{'widgets': widgets}]}
            send_message_to_chat(space_name, thread_name, "Please verify the data extracted by the AI.", card)

        threading.Thread(target=process_and_display).start()
        return {'actionResponse': {'type': "NEW_MESSAGE"}, 'text': "Processing with AI..."}
    except Exception as e:
        return {'text': f"Error: {e}"}

def openConfirmation(event):
    """
    Step 4 (Sub-type A): Displays a final confirmation summary before generating the document.
    """
    logging.info("(form_handler_B_sub_A.py)[openConfirmation] Opening final confirmation.")
    try:
        # ANONYMIZED: List all the fields from your Step 3 form.
        fields = ["client_name", "project_title", "price_phase1_before", "price_phase2_before", "discount"]
        vals = {key: utils.fetch_form_value(event, key) for key in fields}

        # Calculate final prices after discount
        try:
            discount_val = float(vals.get('discount', '0').replace(',', '.'))
        except ValueError:
            discount_val = 0

        def calc_price(price_str):
            try:
                p = float(price_str.replace(',', '.'))
                return f"{p * (1 - discount_val / 100):.2f}".replace('.', ',')
            except (ValueError, TypeError):
                return "N/A"

        price1_after = calc_price(vals['price_phase1_before'])
        price2_after = calc_price(vals['price_phase2_before'])

        # Prepare parameters for the final submission function
        submit_params = [{'key': k, 'value': v} for k, v in vals.items()]
        submit_params.extend([
            {'key': 'price_phase1_after', 'value': price1_after},
            {'key': 'price_phase2_after', 'value': price2_after},
            {'key': 'space_name', 'value': event.get('space', {}).get('name')},
            {'key': 'thread_name', 'value': event.get('thread', {}).get('name')}
        ])

        # Build the summary card
        card_body = {
            "header": {"title": "Final Confirmation (Sub-type A)"},
            "sections": [{"widgets": [
                {'textParagraph': {'text': f"<b>Client:</b> {vals['client_name']}"}},
                {'textParagraph': {'text': f"<b>Project:</b> {vals['project_title']}"}},
                {'divider': {}},
                {'textParagraph': {'text': f"<b>Phase 1 Price (after discount):</b> {price1_after}"}},
                {'textParagraph': {'text': f"<b>Phase 2 Price (after discount):</b> {price2_after}"}},
                {'buttonList': {'buttons': [{'text': "Generate Document", 'onClick': {'action': {
                    'function': "form_handler_B_sub_A.submitForm",
                    'parameters': submit_params
                }}}]}}
            ]}]
        }
        
        return {"actionResponse": {"type": "DIALOG", "dialogAction": {"dialog": {"body": card_body}}}}
    except Exception as e:
        logging.error(f"Error in Sub-type A confirmation: {e}", exc_info=True)
        return {"text": f"An error occurred: {e}"}

def submitForm(event, send_message_to_chat):
    """
    Step 5 (Sub-type A): Generates the document and notifies the user.
    """
    logging.info("(form_handler_B_sub_A.py)[submitForm] Submitting form.")
    try:
        params = event.get('common', {}).get('parameters', {})
        user_email = event.get('user', {}).get('email')
        space_name = params.get('space_name')
        thread_name = params.get('thread_name')

        def generate_and_notify():
            try:
                client_name = params.get('client_name', 'Unknown Client')
                logging.info(f"Generating document for: {client_name}")

                # Create a dictionary of placeholders for the template
                replacements = {f"{{{{{key}}}}}": value for key, value in params.items()}
                
                # Use the shared utility functions to handle Google Drive/Slides operations
                new_file_id = utils.copy_presentation(TEMPLATE_ID, client_name, TARGET_FOLDER_ID)
                utils.fill_placeholders_in_presentation(new_file_id, replacements)
                
                if user_email:
                    utils.share_presentation_with_user(new_file_id, user_email)

                presentation_url = f"https://docs.google.com/presentation/d/{new_file_id}/edit"
                send_message_to_chat(
                    space_name, 
                    thread_name,
                    f"Done! The document for **{client_name}** has been generated.\n\nEdit here: {presentation_url}"
                )
            except Exception as e:
                logging.error(f"Error in generation thread (Sub-type A): {e}", exc_info=True)
                send_message_to_chat(space_name, thread_name, f"A critical error occurred: {e}")

        threading.Thread(target=generate_and_notify).start()
        
        return {
            "actionResponse": {"type": "NEW_MESSAGE"},
            "text": "Starting document generation for Sub-type A. You'll be notified when it's ready."
        }
    except Exception as e:
        logging.error(f"Error in submitForm (Sub-type A): {e}", exc_info=True)
        return {"text": f"An error occurred: {e}"}
