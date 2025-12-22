# author: Olivier "Walgierd" Trela
# version 1.0
# Last edited: 22.12.2025 r.
# This file contains configuration details for external APIs, such as the AI model.

# api_config.py

import os
import google.generativeai as genai

# It's recommended to use environment variables for credential paths.
# For local development, you can set GOOGLE_APPLICATION_CREDENTIALS.
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"

def configure_external_apis():
    """Configures the generative AI API."""
    print("(api_config.py)[configure_external_apis] Configuring external APIs")
    try:
        # The genai.configure() call might not be necessary if credentials are
        # set via environment variables, but it's good practice to have an explicit setup function.
        # If an API key is used, it would be configured here, e.g., genai.configure(api_key="YOUR_API_KEY")
        print("(api_config.py)[configure_external_apis] External APIs configured successfully.")
    except Exception as e:
        print(f"(api_config.py)[configure_external_apis] Error configuring APIs: {e}")

# Generic model names, mapping to specific versions can be done here.
AI_MODEL_FAST = 'gemini-1.5-flash' # A fast, general-purpose model
AI_MODEL_PRO = 'gemini-1.5-pro'    # A more advanced model for complex tasks

# System instructions define the AI's persona and response guidelines.
SYSTEM_INSTRUCTION_FAST = (
    "You are an AI assistant. Your task is to provide helpful and factual answers to questions "
    "on business and general knowledge topics. Respond in a professional but approachable tone. "
    "Keep your answers concise and quick. Respond as if in a chat message, not a scientific article. "
    "Do not use bolding, headers, lists, Markdown, or HTML. Respond only with plain text."
)

SYSTEM_INSTRUCTION_PRO = (
    "You are an advanced AI assistant. Your task is to conduct detailed research and provide "
    "comprehensive, in-depth answers to complex questions on business and specialized topics. "
    "Use a professional, analytical tone. Your answers can be longer but should not be extensive essays. "
    "Act like a top-tier consultant, always ready to help. "
    "Respond as if in a chat message, not a scientific article. "
    "Do not use bolding, headers, lists, Markdown, or HTML. Respond only with plain text."
)
