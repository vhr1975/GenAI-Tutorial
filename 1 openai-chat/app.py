# Import necessary libraries
import chainlit as cl
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get your OpenAI API key
openai_api_key="your-api-key"


# Initialize OpenAI client with your API key
client = AsyncOpenAI(api_key=openai_api_key)

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

    # This line starts an asynchronous operation using 'await'. It means the code waits for the operation to complete before moving on.
    response = await client.chat.completions.create(
        # 'messages' is a list of dictionaries, each representing a message.
        messages=[
            {
                # The first message is from the system, setting the context that the bot replies in Spanish.
                "content": "You are a helpful bot, you always reply in Spanish",
                "role": "system"
            },
            {
                # The second message is from the user. 'message.content' contains the user's message.
                "content": message.content,
                "role": "user"
            }
        ],
        # '**settings' unpacks additional settings for the 'create' method, which could include language, temperature, etc.
        # using **settings in the function call is equivalent to directly passing these as keyword arguments like:
        # model="text-davinci-003", temperature=0.7.
        **settings
    )

    # Send the response back to the user
    await cl.Message(content=response.choices[0].message.content).send()
