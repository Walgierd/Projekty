# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file provides utility functions for creating JSON payloads
# for various Google Chat API responses, such as text messages, cards, and dialogs.

# json_builder.py

import json

def create_text_message(text_content=None, thread_name=None):
    """
    Creates a simple text message payload for the Google Chat API.
    """
    print("(json_builder.py)[create_text_message] Creating text message")
    message = {}
    if text_content:
        message["text"] = text_content
    if thread_name:
        message["thread"] = {"name": thread_name}
    return message

def create_card_message(card_content_list=None, text_content=None, thread_name=None):
    """
    Creates a message payload containing one or more cards (v2).
    """
    print("(json_builder.py)[create_card_message] Creating card message")
    message = {}
    if card_content_list:
        # The API expects a list of card objects
        message["cardsV2"] = card_content_list
    if text_content:
        # Fallback text for notifications
        message["text"] = text_content
    if thread_name:
        message["thread"] = {"name": thread_name}
    return message

def create_dialog_action(dialog_body_sections):
    """
    Creates a response that opens a new dialog window in the chat interface.
    """
    print("(json_builder.py)[create_dialog_action] Creating dialog action")
    return {
        "actionResponse": {
            "type": "DIALOG",
            "dialogAction": {
                "dialog": {
                    "body": {
                        "sections": dialog_body_sections
                    }
                }
            }
        }
    }

def create_update_message_action(card_body_sections, text_content=None):
    """
    Creates a response that updates the message from which a card action was triggered.
    """
    print("(json_builder.py)[create_update_message_action] Creating update message action")
    action = {
        "actionResponse": {
            "type": "UPDATE_MESSAGE"
        },
        "cardsV2": [{
            "card": {
                "sections": card_body_sections
            }
        }]
    }
    if text_content:
        action["text"] = text_content
    return action
