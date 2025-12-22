# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file contains the handler for the /research slash command, which
# performs a more in-depth query using the advanced AI model.

# research_handler.py

from chat_handler import get_ai_response, send_message_to_chat

def handle_research(argument_text, space_name, thread_name):
    """
    Handles the /research command by running the query in a separate thread
    and sending the detailed response back to the chat.

    This function returns another function (`do_research_and_send`) which is
    the actual target for the threading.Thread call. This pattern is useful
    for encapsulating the logic that needs to run in the background.
    """
    def do_research_and_send():
        """
        The actual workhorse function that runs in the background.
        """
        # Call the AI with research_mode=True to use the more powerful model
        ai_response_text = get_ai_response(argument_text, research_mode=True)
        
        # Format the response for the chat
        full_response = f"**Detailed Research Results:**\n\n{ai_response_text}"
        
        # Send the final response back to the original thread
        send_message_to_chat(space_name, thread_name, full_response)

    return do_research_and_send
