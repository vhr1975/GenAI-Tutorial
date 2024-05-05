# chainlit run demo.py -w
# demo.py
import chainlit as cl
from openai import AsyncOpenAI


# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI()

cl.instrument_openai()

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    # ... more settings
}

@cl.step
def tool():
    return "Response from the tool!"

@cl.on_message
async def on_message(message: cl.Message):
    # Call the tool
    tool()

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
    await cl.Message(content=response.choices[0].message.content).send()
    
# Run it!
