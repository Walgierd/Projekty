# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file handles chat interactions, including AI response generation and event handling.

# chat_handler.py

import json
import google.generativeai as genai
from api_config import AI_MODEL_FAST, AI_MODEL_PRO, SYSTEM_INSTRUCTION_FAST, SYSTEM_INSTRUCTION_PRO
import requests
import os
from google.oauth2 import service_account
import google.auth
import google.auth.transport.requests

def get_access_token_from_service_account():
    """
    Retrieves an OAuth2 access token for the service account.
    This token is required to authenticate with Google Chat API.
    """
    try:
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/chat.bot"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def get_ai_response(user_query: str, research_mode: bool = False) -> str:
    """
    Generates a response from the AI model based on the user's query.
    It selects a model and system instruction based on whether it's in research mode.
    """
    if research_mode:
        model_name = AI_MODEL_PRO
        system_instruction = SYSTEM_INSTRUCTION_PRO
    else:
        model_name = AI_MODEL_FAST
        system_instruction = SYSTEM_INSTRUCTION_FAST

    try:
        model = genai.GenerativeModel(model_name)
        prompt_parts = [
            system_instruction,
            f"\nUser Query: {user_query}\n\nResponse:",
        ]
        print(f"Sending prompt to AI ({model_name}): {prompt_parts}")
        response = model.generate_content(prompt_parts)
        print(f"Received response from AI: {response.text}")
        return response.text
    except Exception as e:
        print(f"Error during AI response generation: {e}")
        return "Sorry, there was a problem with the AI. Please try again later."

def handle_added_to_space_event(event: dict):
    """
    Handles the event when the bot is added to a new space (room or DM).
    It sends a welcome message with a card.
    """
    print("Bot was added to a space.")
    space_data = event.get('space', {})

    if space_data.get('type') == 'ROOM':
        welcome_text = "Thank you for adding me to the room! I'm ready to assist. Just ask me a question."
    else:
        welcome_text = "Hello! I am your personal AI assistant. How can I help you today?"

    welcome_card_content = [{
        "cardId": "welcomeCard",
        "card": {
            "header": {
                "title": "AI Assistant",
                "subtitle": "An AI agent to help with your tasks. Use / to see available commands.",
                "imageUrl": "https://your-company-logo-url.com/logo.png", # Anonymized URL
                "imageType": "CIRCLE"
            },
            "sections": [{
                "widgets": [
                    {
                        "textParagraph": {
                            "text": welcome_text
                        }
                    },
                    {
                        "buttonList": {
                            "buttons": [{
                                "text": "How to use me?",
                                "onClick": {
                                    "openLink": {
                                        "url": "https://your-internal-documentation-link.com" # Anonymized URL
                                    }
                                }
                            }]
                        }
                    }
                ]
            }]
        }
    }]

    response_body = {
        "cardsV2": welcome_card_content,
        "text": welcome_text
    }

    print(f"Sending response to ADDED_TO_SPACE event: {json.dumps(response_body, indent=2)}")
    return response_body

def send_message_to_chat(space_name, thread_name, text, card=None):
    """
    Sends a message (text or card) to a Google Chat space via the REST API.
    """
    access_token = get_access_token_from_service_account()
    if not access_token:
        print("Missing bot token to send messages.")
        return

    url = f"https://chat.googleapis.com/v1/{space_name}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "text": text
    }
    if thread_name:
        body["thread"] = {"name": thread_name}
    if card:
        body["cardsV2"] = [{
            "cardId": "interactiveCard", # Generic card ID
            "card": card
        }]

    response = requests.post(url, headers=headers, json=body)
    print(f"Message sending status: {response.status_code}, {response.text}")
