import textbase
from textbase.message import Message
from textbase import models
import os
from typing import List
from textbase.message import Message
import os
import sys
import logging
from typing import List
import importlib

# Load your OpenAI API key
# models.OpenAI.api_key = "Open_A_key"
# or from environment variable:
models.OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Prompt for GPT-3.5 Turbo
SYSTEM_PROMPT = (
    "You are chatting with an AI. There are no specific prefixes for responses, so you can ask or talk about anything you like. The AI will respond in a natural, conversational manner. Feel free to start the conversation with any question or topic, and let's have a pleasant chat!"
    )
# Options for interview preparation assistance
INTERVIEW_OPTIONS = [
    "1. Interview Tips",
    "2. Resume Review",
    "3. Common Interview Questions",
    "4. Behavioral Interviews",
    "5. Technical Interviews",
]

INTERVIEW_OPTIONS_FILE = [
     "interviewtips.py",
     "resumereview.py",
     "commoninterviewquestoins.py",
     "behavinterviews.py",
     "techinterviews.py"
]
    

def get_module_from_file_path(file_path: str):
    """
    The function `get_module_from_file_path` takes a file path as input, loads the module from the file,
    and returns the module.

    :param file_path: The file path is the path to the Python file that you want to import as a module.
    It should be a string representing the absolute or relative path to the file
    :type file_path: str
    :return: the module that is loaded from the given file path.
    """
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

@textbase.chatbot("talking-bot")
def on_message(message_history: List[Message], state: dict = None):
    """Your chatbot logic here
    message_history: List of user messages
    state: A dictionary to store any stateful information

    Return a string with the bot_response or a tuple of (bot_response: str, new_state: dict)
    """
    
    if state is None or "counter" not in state:
        state = {"counter": 0}

    #Display the initial prompt at the begining of the message
    if not message_history:
        bot_response = SYSTEM_PROMPT
        return bot_response,state
    
    latest_message = message_history[-1]

    if latest_message.content.strip().lower() in ["hi", "hello"]:
        bot_response = "Hello! I am your Interview Coach. How can I assist you with your interview preparation today?"+"\n".join(INTERVIEW_OPTIONS)
        return bot_response , state

      # Check if the user has selected an option from the list
    selected_option = latest_message.content.strip()
    if selected_option.isdigit() and 1 <= int(selected_option) <= len(INTERVIEW_OPTIONS):
        # Load the corresponding logic file for the selected option
        option_index = int(selected_option) - 1
        
        logic_file = f"{INTERVIEW_OPTIONS_FILE[option_index]}"  # Replace this with your logic file naming convention
        module = get_module_from_file_path(logic_file)

        # Call the on_message function from the loaded module
        response = module.on_message(message_history, state)
        return response


    state["counter"]+=1

    # # Generate GPT-3.5 Turbo response
    bot_response = models.OpenAI.generate(
        system_prompt=SYSTEM_PROMPT,
        message_history=message_history,
        model="gpt-3.5-turbo",
    )

    return bot_response, state
