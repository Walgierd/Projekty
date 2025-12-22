# AI Agent Blueprint

This project is a blueprint for a Google Chat AI Agent integrated with various Google services like Gemini, Google Drive, and Google Sheets. It's designed to be a modular and extensible foundation for building sophisticated chat bots.

## Project Structure and Components

Below is a description of each file in the project:

-   **`AIAgent_Blueprint.py`**: The main application file. It contains the Flask web server that acts as the entry point for all incoming events from Google Chat. It routes `MESSAGE`, `CARD_CLICKED`, and other events to the appropriate handlers.

-   **`requirements.txt`**: Lists all the Python packages required to run the project.

-   **`README.md`**: This file, providing documentation and setup instructions.

### Configuration

-   **`api_config.py`**: A central place for configuring external APIs. It defines which AI models to use (e.g., a faster model for quick chats, a more powerful one for research) and contains the system instructions that give the AI its persona and behavioral guidelines.

-   **`mail_config.json.template`**: A template for email server configuration. To send emails, you should copy this file to `mail_config.json` and fill in your actual SMTP credentials.

### Core Handlers

-   **`chat_handler.py`**: Handles core chat functionalities. This includes the primary logic for generating responses from the AI model and a function for sending messages (both text and cards) back to the Google Chat space.

-   **`mail_handler.py`**: Manages all email-related tasks. It uses SMTP to send emails, can handle attachments downloaded from Google Drive, and is set up to enqueue long-running tasks in a background queue (using Redis and RQ) to prevent blocking.

-   **`json_builder.py`**: A utility module with helper functions to create the structured JSON payloads required by the Google Chat API for various response types, such as text messages, interactive cards, and dialogs.

### Slash Command Handlers

-   **`about_handler.py`**: A simple handler for the `/about` slash command. It returns a static, informational card that describes the bot and its main functions.

-   **`research_handler.py`**: Handles the `/research` command. It uses the more advanced AI model specified in `api_config.py` to perform in-depth queries and posts the results back to the chat. The research is run in a separate thread to avoid delaying the UI.

### Form Handlers (Examples)

The project includes two powerful, generic examples of how to handle complex, multi-step user interactions using interactive cards and dialogs.

-   **`form_handler_A.py`**: A comprehensive, anonymized example of a multi-step form. It demonstrates:
    -   Fetching data from a Google Sheet to populate dropdown menus.
    -   Opening dialogs to collect user input.
    -   Generating documents from a Google Slides template by filling placeholders.
    -   Sending email notifications with the generated documents as attachments.

-   **`form_handler_B.py`**: This handler acts as a **router** for another complex form that has multiple paths or "sub-types." It contains shared utility functions (e.g., for parsing time, interacting with Google Drive) that can be used by its sub-handlers.
    -   **`form_handler_B_sub_A.py`**: Implements the logic for one specific branch ("Sub-type A") of Form B.
    -   **`form_handler_B_sub_B.py`**: Implements the logic for the other branch ("Sub-type B") of Form B.

## Setup and Configuration

### 1. Install Dependencies

Install all the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Authentication

This application uses Google Cloud Application Default Credentials (ADC) for authentication.

-   **For local development:**
    1.  Install the Google Cloud CLI: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
    2.  Log in with your user account:
        ```bash
        gcloud auth application-default login
        ```
-   **For deployment on Google Cloud (e.g., Cloud Run, App Engine):**
    The service will automatically use the attached service account's credentials. No extra setup is needed.

Ensure the service account or your user account has the necessary IAM roles/permissions for the APIs being used (Google Drive, Google Sheets, Google Slides, Gmail, etc.).

### 3. Email Configuration (`mail_config.json`)

To enable the agent to send emails, you need to configure your SMTP server settings.

1.  Make a copy of the `mail_config.json.template` file and rename it to `mail_config.json`.
2.  Edit `mail_config.json` with your SMTP provider's details.

**File: `mail_config.json`**

```json
{
  "smtp_server": "smtp.your-domain.com", // e.g., "smtp.gmail.com"
  "smtp_port": 587, // Port for TLS, usually 587 or 465 for SSL
  "email": "your-email@your-domain.com", // The email address the agent will send from
  "password": "your-app-password" // An App Password for your email account (recommended over your main password)
}
```

**Note on Gmail:** If you are using a Gmail account, you will need to generate an "App Password" to use here. Using your regular Google account password will likely not work due to security settings.

### 4. Running the Application

You can run the Flask application directly:

```bash
python AIAgent_Blueprint.py
```

The agent will be available at the endpoint exposed by Flask, which you can then configure in your Google Chat API settings.

