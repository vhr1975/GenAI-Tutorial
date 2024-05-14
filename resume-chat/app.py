# Import necessary libraries and modules
from operator import itemgetter
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableLambda
from langchain.schema.runnable.config import RunnableConfig
from langchain.memory import ConversationBufferMemory
from chainlit.types import ThreadDict
import chainlit as cl
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get your OpenAI API key
openai_api_key="your-openai-api-key"

# Function to set up the runnable pipeline
def setup_runnable():
    # Get the memory from the user session
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    # Initialize ChatOpenAI with your API key
    model = ChatOpenAI(streaming=True, api_key=openai_api_key)
    # Set up the chat prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful chatbot"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    # Set up the runnable pipeline
    runnable = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | model
        | StrOutputParser()
    )
    # Store the runnable in the user session
    cl.user_session.set("runnable", runnable)

# Function to be called for password authentication
@cl.password_auth_callback
def auth():
    return cl.User(identifier="test")

# Function to be called when a chat starts
@cl.on_chat_start
async def on_chat_start():
    # Set up the memory and runnable in the user session
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    setup_runnable()

# Function to be called when a chat resumes
@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    # Initialize the memory and load previous messages
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])

    # Set up the memory and runnable in the user session
    cl.user_session.set("memory", memory)
    setup_runnable()

# Function to be called when a message is received
@cl.on_message
async def on_message(message: cl.Message):
    # Get the memory and runnable from the user session
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    runnable = cl.user_session.get("runnable")  # type: Runnable

    # Initialize a message to send the response
    res = cl.Message(content="")

    # Run the runnable pipeline and send the result
    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await res.stream_token(chunk)

    await res.send()

    # Add the user message and AI response to the memory
    memory.chat_memory.add_user_message(message.content)
    memory.chat_memory.add_ai_message(res.content)