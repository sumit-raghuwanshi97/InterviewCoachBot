
import textbase
from textbase.message import Message
from textbase import models
import os
from typing import List


# System prompt to instruct GPT-3.5 Turbo and set context
SYSTEM_PROMPT = """You are an AI Interview Coach. 
You are here to provide valuable tips and advice for interview preparation. 
Please feel free to ask any questions or share your concerns related to interviews, 
and I will do my best to assist you throughout the preparation process."""

# Function to read interview tips from the text file
def print_interview_tips():
    file_path = os.path.join(os.path.dirname(__file__), "interview_tips.txt")
    with open(file_path, "r") as file:
        interview_tips = file.read()
    return interview_tips

# Function to handle the on_message logic for interview tips
def on_message(message_history: List[Message], state: dict = None):
    """Your interviewtips.py chatbot logic here
    message_history: List of user messages
    state: A dictionary to store any stateful information

    Return a string with the bot_response or a tuple of (bot_response: str, new_state: dict)
    """

    # Get the latest user message
    latest_message = message_history[-1]

    if "1" in latest_message.content.strip().lower():
        # Print interview tips from the text file
        print_interview_tips()
        bot_response = "Do you want to proceed with interview tips ? Type Yes or NO"
        return bot_response, state

    # Check if the user starts the conversation with "hi" or "hello" and asks for help
    if "hi" in latest_message.content.strip().lower() and "help" in latest_message.content.strip().lower():
        bot_response = "Hello! I am your Interview Tips Assistant. How can I assist you with interview tips today?"
        return bot_response, state

    if "yes" in latest_message.content.strip().lower():
        bot_response = models.OpenAI.generate(
        system_prompt="Provide interview tips each in one line to the user and complete the further queries , provide easily readable response",
        message_history=message_history,
        model="gpt-3.5-turbo",
    )
        return bot_response , state 
    
    # Use GPT-3.5 Turbo to generate a response for other user inputs
    bot_response = models.OpenAI.generate(
        system_prompt=latest_message.content,
        message_history=message_history,
        model="gpt-3.5-turbo",
    )

    return bot_response, state
