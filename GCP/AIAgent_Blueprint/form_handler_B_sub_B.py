# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file contains the specific logic for "Sub-type B" of Form B.
# It defines the dialogs, AI prompts, and submission logic for this branch of the form.

# form_handler_B_sub_B.py

import logging
import threading
import json
from chat_handler import get_ai_response, send_message_to_chat
# Import shared utility functions from the main Form B handler
import form_handler_B as utils

# --- Configuration for Sub-type B ---
# ANONYMIZED: Replace with your actual template and folder IDs.
TEMPLATE_ID = "YOUR_SUBTYPE_B_TEMPLATE_ID"
TARGET_FOLDER_ID = "YOUR_SUBTYPE_B_TARGET_FOLDER_ID"

def open_subtype_B_dialog(event, send_message_to_chat):
    """
    Step 2 (Sub-type B): Displays a form with fields specific to this sub-type.
    """
    print("(form_handler_B_sub_B.py)[open_subtype_B_dialog] Opening dialog.")
    notes_value = utils.fetch_form_value(event, "notes")

    # These fields are specific to the original project's "WS" offer.
    # They should be replaced with fields relevant to your "Sub-type B".
    widgets = [
        {"textInput": {"name": "notes", "label": "Notes (editable)", "type": "MULTIPLE_LINE", "value": notes_value}},
        {"divider": {}},
        {"textParagraph": {"text": "<b>Time Data (Sub-type B):</b>"}},
        {"textInput": {"name": "time_field_A", "label": "Time for Activity A (e.g., 2+4)"}},
        {"textInput": {"name": "time_field_B", "label": "Time for Activity B (e.g., 1 day)"}},
        {"divider": {}},
        {"textParagraph": {"text": "<b>Pricing and Discount:</b>"}},
        {"textInput": {"name": "price_phase1_before", "label": "Price Phase 1 (Net)"}},
        {"textInput": {"name": "price_phase2_before", "label": "Price Phase 2 (Net/month)"}},
        {"textInput": {"name": "discount", "label": "Discount (%)"}},
        {"divider": {}},
        {"buttonList": {"buttons": [{
            "text": "Process with AI",
            "onClick": {"action": {"function": "form_handler_B_sub_B.build_form_B_step3_ai", "interaction": "OPEN_DIALOG"}}
        }]}}
    ]
    return {
        "actionResponse": {
            "type": "DIALOG",
            "dialogAction": {
                "dialog": {
                    "body": {
                        "sections": [{
                            "header": "Details for Sub-type B (Step 2/4)",
                            "widgets": widgets
                        }]
                    }
                }
            }
        }
    }

def call_ai_to_extract_data(notes: str) -> dict:
    """
    Calls the AI model with a specific prompt to extract and structure data for Sub-type B.
    """
    # ANONYMIZED: This prompt is highly specific to the original project.
    # It needs to be completely rewritten to match your data structure and requirements.
    prompt = f"""
    You are an AI assistant. Your task is to process raw notes and convert them
    into a structured JSON object for generating a "Sub-type B" document.

    RAW NOTES:
    \"\"\"{notes}\"\"\"

    EXPECTED JSON STRUCTURE:
    - "client_name": The name of the client.
    - "situation_summary": A professional summary of the client's situation in bullet points (use \\n).
    - "project_goals": The goals of the project in bullet points (use \\n).

    Return ONLY the JSON object.
    """
    try:
        response_text = get_ai_response(prompt, research_mode=False)
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start == -1: return {}
        return json.loads(response_text[start:end+1])
    except Exception as e:
        logging.error(f"Error processing AI response for Sub-type B: {e}", exc_info=True)
        return {}

def build_form_B_step3_ai(event, send_message_to_chat):
    """
    Step 3 (Sub-type B): Displays a verification dialog with data extracted by the AI.
    """
    logging.info("(form_handler_B_sub_B.py)[build_form_B_step3_ai] Building verification dialog.")
    try:
        notes = utils.fetch_form_value(event, "notes")
        raw_time_A = utils.fetch_form_value(event, "time_field_A")
        raw_time_B = utils.fetch_form_value(event, "time_field_B")
        price1 = utils.fetch_form_value(event, "price_phase1_before")
        price2 = utils.fetch_form_value(event, "price_phase2_before")
        discount = utils.fetch_form_value(event, "discount")

        space_name = event.get('space', {}).get('name')
        thread_name = event.get('thread', {}).get('name')

        def process_and_display():
            extracted = call_ai_to_extract_data(notes)
            
            # Add time and price data, processed by the server
            extracted["time_A"] = utils.sum_time_fields(raw_time_A)
            extracted["time_B"] = utils.sum_time_fields(raw_time_B)
            extracted["total_time_phase1"] = utils.sum_time_fields(raw_time_A, raw_time_B)
            extracted["price_phase1_before"] = price1
            extracted["price_phase2_before"] = price2
            extracted["discount"] = discount
            
            # ANONYMIZED: Build a card with input fields pre-filled with AI-extracted data.
            widgets = [
                {"textInput": {"name": "client_name", "label": "Client Name", "value": extracted.get("client_name", "")}},
                {"textInput": {"name": "situation_summary", "label": "Situation Summary", "type": "MULTIPLE_LINE", "value": extracted.get("situation_summary", "")}},
                {"textInput": {"name": "project_goals", "label": "Project Goals", "type": "MULTIPLE_LINE", "value": extracted.get("project_goals", "")}},
                {"divider": {}},
                {"textInput": {"name": "time_A", "label": "Time Activity A", "value": extracted.get("time_A", "")}},
                {"textInput": {"name": "time_B", "label": "Time Activity B", "value": extracted.get("time_B", "")}},
                {"divider": {}},
                {"textInput": {"name": "price_phase1_before", "label": "Price Phase 1", "value": extracted.get("price_phase1_before", "")}},
                {"textInput": {"name": "price_phase2_before", "label": "Price Phase 2", "value": extracted.get("price_phase2_before", "")}},
                {"textInput": {"name": "discount", "label": "Discount (%)", "value": extracted.get("discount", "")}},
                {"buttonList": {"buttons": [{
                    "text": "Confirm Data",
                    "onClick": {"action": {"function": "form_handler_B_sub_B.openConfirmation", "interaction": "OPEN_DIALOG"}}
                }]}}
            ]
            card = {'header': {'title': 'Verify Extracted Data (Sub-type B)'}, 'sections': [{'widgets': widgets}]}
            send_message_to_chat(space_name, thread_name, "Please verify the data extracted by the AI.", card)

        threading.Thread(target=process_and_display).start()
        return {'actionResponse': {'type': "NEW_MESSAGE"}, 'text': "Processing with AI..."}
    except Exception as e:
        logging.error(f"Error in build_form_B_step3_ai (Sub-type B): {e}", exc_info=True)
        return {'text': f"Error: {e}"}

def openConfirmation(event):
    """
    Step 4 (Sub-type B): Displays a final confirmation summary.
    """
    logging.info("(form_handler_B_sub_B.py)[openConfirmation] Opening final confirmation.")
    try:
        # ANONYMIZED: List all fields from your Step 3 form.
        fields = ["client_name", "situation_summary", "project_goals", "time_A", "time_B", "price_phase1_before", "price_phase2_before", "discount"]
        vals = {key: utils.fetch_form_value(event, key) for key in fields}

        # Calculate final prices
        try:
            discount_val = float(vals.get('discount', '0').replace(',', '.'))
        except (ValueError, TypeError):
            discount_val = 0

        def calc_price(price_str):
            try:
                p = float(price_str.replace(',', '.'))
                return f"{p * (1 - discount_val / 100):.2f}".replace('.', ',')
            except (ValueError, TypeError):
                return "N/A"

        price1_after = calc_price(vals['price_phase1_before'])
        price2_after = calc_price(vals['price_phase2_before'])

        # Prepare parameters for the final submission
        submit_params = [{'key': k, 'value': v} for k, v in vals.items()]
        submit_params.extend([
            {'key': 'price_phase1_after', 'value': price1_after},
            {'key': 'price_phase2_after', 'value': price2_after},
            {'key': 'space_name', 'value': event.get('space', {}).get('name')},
            {'key': 'thread_name', 'value': event.get('thread', {}).get('name')}
        ])

        card_body = {
            "header": {"title": "Final Confirmation (Sub-type B)"},
            "sections": [{"widgets": [
                {'textParagraph': {'text': f"<b>Client:</b> {vals['client_name']}"}},
                {'divider': {}},
                {'textParagraph': {'text': f"<b>Phase 1 Price (after discount):</b> {price1_after}"}},
                {'textParagraph': {'text': f"<b>Phase 2 Price (after discount):</b> {price2_after}"}},
                {'buttonList': {'buttons': [{'text': "Generate Document", 'onClick': {'action': {
                    'function': "form_handler_B_sub_B.submitForm",
                    'parameters': submit_params
                }}}]}}
            ]}]
        }
        
        return {"actionResponse": {"type": "DIALOG", "dialogAction": {"dialog": {"body": card_body}}}}
    except Exception as e:
        logging.error(f"Error in Sub-type B confirmation: {e}", exc_info=True)
        return {"text": f"An error occurred: {e}"}

def submitForm(event, send_message_to_chat):
    """
    Step 5 (Sub-type B): Generates the document and notifies the user.
    """
    logging.info("(form_handler_B_sub_B.py)[submitForm] Submitting form.")
    try:
        params = event.get('common', {}).get('parameters', {})
        user_email = event.get('user', {}).get('email')
        space_name = params.get('space_name')
        thread_name = params.get('thread_name')

        def generate_and_notify():
            try:
                client_name = params.get('client_name', 'Unknown Client')
                logging.info(f"Generating document for: {client_name}")

                replacements = {f"{{{{{key}}}}}": value for key, value in params.items()}
                
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
                logging.error(f"Error in generation thread (Sub-type B): {e}", exc_info=True)
                send_message_to_chat(space_name, thread_name, f"A critical error occurred: {e}")

        threading.Thread(target=generate_and_notify).start()
        
        return {
            "actionResponse": {"type": "NEW_MESSAGE"},
            "text": "Starting document generation for Sub-type B. You'll be notified when it's ready."
        }
    except Exception as e:
        logging.error(f"Error in submitForm (Sub-type B): {e}", exc_info=True)
        return {"text": f"An error occurred: {e}"}
