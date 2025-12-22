# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file contains the main application logic for the AI Agent,
# including a Flask web server to handle incoming events from a chat platform.

#AIAgent_Blueprint.py

import os
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Mapping
from flask import Flask, request, jsonify

from api_config import configure_external_apis
from chat_handler import get_ai_response, handle_added_to_space_event, send_message_to_chat
from research_handler import handle_research
from about_handler import handle_about

# Google Cloud authentication
from google.auth import default
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging

# The following imports are for specific handlers for different slash commands and card actions.
# They are named generically here (e.g., form_handler_A) and should be renamed to reflect their actual purpose.
from form_handler_A import (
    get_data_from_sheet,
    open_form_A_dialog,
    open_confirmation_dialog,
    submit_form_A
)
from form_handler_B import (
    open_form_B_dialog,
    route_form_B_step2
)
from form_handler_B_sub_A import build_form_B_step3_ai as build_sub_A_step3, openConfirmation as open_sub_A_confirmation, submitForm as submit_sub_A_form
from form_handler_B_sub_B import build_form_B_step3_ai as build_sub_B_step3, openConfirmation as open_sub_B_confirmation, submitForm as submit_sub_B_form

# Configure external APIs (e.g., Gemini) on startup.
# Keys and credentials should be handled securely, for example via environment variables.

configure_external_apis()

app = Flask(__name__)

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

@app.route('/', methods=['POST'])
def post(request):
    """Main endpoint to receive and route all incoming events."""
    logging.info("Received a request")
    try:
        if not request.is_json:
            logging.error("Request is not in JSON format")
            return jsonify({"error": "Content-Type must be application/json"}), 415

        event = request.get_json()
        event_type = event.get('type')
        logging.info(f"Event type: {event_type}")

        # Route event based on its type
        if event_type == 'MESSAGE':
            body = on_message(event)
        elif event_type == 'CARD_CLICKED':
            body = on_card_click(event)
        elif event_type == 'ADDED_TO_SPACE':
            body = handle_added_to_space_event(event)
        else:
            body = {}

        logging.info(f"Responding with body: {body}")
        return jsonify(body)
    except Exception as e:
        logging.error(f"Error in post handler: {e}", exc_info=True)
        return jsonify({"error": str(e)})

def on_message(event: dict) -> dict:
    """Handles 'MESSAGE' events, including slash commands and direct messages."""
    logging.info("Handling a 'MESSAGE' event")
    try:
        slash_cmd = event.get('message', {}).get('slashCommand')
        if slash_cmd:
            command_id = slash_cmd.get('commandId')
            logging.info(f"Slash command ID: {command_id}")
            # Route based on slash command ID
            if command_id == "1": # /about
                return handle_about()
            elif command_id == "2": # /research
                argument_text = event.get('message', {}).get('argumentText', '').strip()
                logging.info(f"Research argument: {argument_text}")
                if not argument_text:
                    return {'text': "Please provide a topic for research, e.g., /research Impact of AI on the job market."}
                space_name = event.get('space', {}).get('name')
                thread_name = event.get('thread', {}).get('name')
                # Run research in a separate thread to avoid blocking
                threading.Thread(target=handle_research, args=(argument_text, space_name, thread_name)).start()
                return {'text': "Research in progress. The results will be posted shortly..."}
            elif command_id == "3": # /form_a
                return open_form_A_dialog()
            elif command_id == "4": # /form_b
                return open_form_B_dialog()

        # Handle plain text messages
        user_message_text = event.get('message', {}).get('text', '').strip()
        logging.info(f"User message: {user_message_text}")
        if not user_message_text:
            return {'text': "Sorry, I could not understand your message. The text is empty."}

        # Differentiate between a standard chat and a research query
        if user_message_text.lower().startswith('/research'):
            query = user_message_text[len('/research'):].strip()
            if not query:
                return {'text': "Please provide a topic for research, e.g., /research Impact of AI on the job market."}
            ai_response_text = get_ai_response(query, research_mode=True)
            return {'text': f"**Detailed Research Results:**\n\n{ai_response_text}"}
        else:
            ai_response_text = get_ai_response(user_message_text, research_mode=False)
            return {'text': ai_response_text}

    except Exception as e:
        logging.error(f"Error in on_message handler: {e}", exc_info=True)
        return {'text': f"An error occurred: {e}"}

def on_card_click(event: dict) -> dict:
    """Handles 'CARD_CLICKED' events from interactive cards."""
    logging.info("Handling a 'CARD_CLICKED' event")
    try:
        invoked_function = event.get('common', {}).get('invokedFunction')
        logging.info(f"Invoked function: {invoked_function}")

        # Route based on the invoked function from the card
        action_handlers = {
            "openFormADialog": open_form_A_dialog,
            "openConfirmationDialog": lambda: open_confirmation_dialog(event),
            "submitFormA": lambda: submit_form_A(event, send_message_to_chat),
            "routeFormBStep2": lambda: route_form_B_step2(event, send_message_to_chat),
            "form_handler_B_sub_A.build_form_B_step3_ai": lambda: build_sub_A_step3(event, send_message_to_chat),
            "form_handler_B_sub_A.openConfirmation": lambda: open_sub_A_confirmation(event),
            "form_handler_B_sub_A.submitForm": lambda: submit_sub_A_form(event, send_message_to_chat),
            "form_handler_B_sub_B.build_form_B_step3_ai": lambda: build_sub_B_step3(event, send_message_to_chat),
            "form_handler_B_sub_B.openConfirmation": lambda: open_sub_B_confirmation(event),
            "form_handler_B_sub_B.submitForm": lambda: submit_sub_B_form(event, send_message_to_chat),
        }

        handler = action_handlers.get(invoked_function)
        if handler:
            return handler()
        else:
            logging.warning(f"No handler found for invoked function: {invoked_function}")
            return {}

    except Exception as e:
        logging.error(f"Error in on_card_click handler: {e}", exc_info=True)
        return {}

# Initialize Google API clients.
# Ensure that the service account has the necessary permissions (e.g., Gmail API).
# The credentials will be automatically discovered if the application is running
# in a Google Cloud environment. For local development, set up Application Default Credentials.
try:
    credentials, project_id = default()
    gmail_service = build("gmail", "v1", credentials=credentials)
    # You can initialize other services here, e.g., Google Sheets
    # sheets_service = build("sheets", "v4", credentials=credentials)
except Exception as e:
    logging.error(f"Failed to initialize Google API services: {e}", exc_info=True)
    gmail_service = None
    # sheets_service = None

# To run this locally, you can use:
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
