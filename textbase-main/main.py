import textbase
from textbase.message import Message
from textbase import models
import os
from typing import List
from textbase.message import Message
import os
import sys
import logging
import difflib
from typing import List
import importlib

# Load your OpenAI API key
# models.OpenAI.api_key = "Open_A_key"
# or from environment variable:
models.OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Prompt for GPT-3.5 Turbo
SYSTEM_PROMPT = (
    "Welcome to the Interview Coach! I am here to help you with interview preparation. "
    "Feel free to ask any interview-related questions or share your concerns. "
    "Whether it's interview tips, common questions, or behavioral interviews, I've got you covered. "
    "Ask away, and let's make sure you shine in your next interview!"
)

def read_help():
    file_path = os.path.join(os.path.dirname(__file__), "chatbot_help.txt")
    with open(file_path, "r") as file:
        help_text = file.read()
    return help_text

def read_interview_conversation():
    file_path = os.path.join(os.path.dirname(__file__), "interview_tips.txt")
    with open(file_path, "r") as file:
        conversation_data = file.read()
    return conversation_data

def prepare_conversation_list(conversation_data):
    pairs = conversation_data.strip().split("\n\n")
    conversation_list = []
    for pair in pairs:
        user, bot = pair.split("\n")
        conversation_list.append((user.replace("User: ", ""), bot.replace("Bot: ", "")))
    return conversation_list

def get_most_similar_response(user_input, conversation_list):
    max_similarity = 0
    most_similar_response = None

    for user_msg, bot_msg in conversation_list:
        similarity = difflib.SequenceMatcher(None, user_input.lower(), user_msg.lower()).ratio()
        if similarity > max_similarity and similarity > 0.8:  # You can adjust this threshold based on your requirement
            max_similarity = similarity
            most_similar_response = bot_msg

    return most_similar_response

@textbase.chatbot("talking-bot")
def on_message(message_history: List[Message], state: dict = None):

    conversation_data = read_interview_conversation()
    conversation_list = prepare_conversation_list(conversation_data)
    
    if state is None or "counter" not in state:
        state = {"counter": 0}

    if not message_history:
        bot_response = SYSTEM_PROMPT
        return bot_response,state
    
    latest_message = message_history[-1]

    if latest_message.content.strip().lower() in ["help", "commands", "info"]:
        help_text = read_help()
        bot_response = help_text
        return bot_response, state

    if latest_message.content.strip().lower() in ["hi", "hello","hey"]:
        bot_response = "Hello! I am your Interview Coach. How can I assist you with your interview preparation today?\n"
        return bot_response , state
    
    else:
        # Search for the most similar user message from the conversation list
        user_input = latest_message.content.lower()  # Convert user input to lowercase
        similar_response = get_most_similar_response(user_input, conversation_list)

        if similar_response:
           return similar_response, state

    state["counter"]+=1

    try:
        bot_response = models.OpenAI.generate(
            system_prompt=SYSTEM_PROMPT,
            message_history=message_history,
            model="gpt-3.5-turbo",
        )
        return bot_response, state
    except Exception as e:
        bot_response = "Sorry, there was a problem processing your request. Please try again later."
        return bot_response, state

