# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file contains the handler for the /about slash command.

#about_handler.py

def handle_about():
    """
    Returns a dialog response for the /about command in the chat.
    This card provides a brief description of the agent and its commands.
    """
    print("(about_handler.py)[handle_about] Function called")
    return {
        "actionResponse": {
            "type": "DIALOG",
            "dialogAction": {
                "dialog": {
                    "body": {
                        "sections": [{
                            "header": "About the AI Agent",
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": "AI Agent - Your assistant. Use /research for advanced questions, /form_a for one form, or /form_b for another."
                                    }
                                },
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Open Form A",
                                                "onClick": {
                                                    "action": {
                                                        "function": "openFormADialog",
                                                        "interaction": "OPEN_DIALOG"
                                                    }
                                                }
                                            },
                                            {
                                                "text": "Open Form B",
                                                "onClick": {
                                                    "action": {
                                                        "function": "openFormBDialog",
                                                        "interaction": "OPEN_DIALOG"
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }]
                    }
                }
            }
        }
    }
