# Import necessary libraries
import chainlit as cl
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI()

# Instrument the OpenAI client with Chainlit
cl.instrument_openai()

# Define settings for OpenAI model
settings = {
    "model": "gpt-3.5-turbo",  # Model to use
    "temperature": 0,  # Controls randomness of the model's output
    # ... more settings
}

@cl.step
def tool():
    """
    This function is a step in the Chainlit application.
    It returns a string message.

    Returns:
        str: A message from the tool.
    """
    return "Response from the tool!"

@cl.on_message
async def on_message(message: cl.Message):
    """
    This function is called every time a user sends a message.
    It generates a response using the OpenAI model and sends it back to the user.

    Args:
        message (cl.Message): The user's message.

    Returns:
        None.
    """
    # Call the tool
    tool()

    # Generate a response using the OpenAI model
    response = await client.chat.completions.create(
        messages=[
            {
                "content": "You are a helpful bot, you always reply in Spanish",
                "role": "system"
            },
            {
                "content": message.content,
                "role": "user"
            }
        ],
        **settings
    )

    # Send the response back to the user
    await cl.Message(content=response.choices[0].message.content).send()