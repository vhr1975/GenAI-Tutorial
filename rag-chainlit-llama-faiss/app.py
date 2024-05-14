# Import necessary libraries and modules
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import CTransformers
import chainlit as cl

# Define the path to the FAISS database
DB_FAISS_PATH = "vectorstore/db_faiss"

############################################################################################
# TODO Define the custom prompt template
custom_prompt_template = ...
############################################################################################

# Function to set the custom prompt
def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(
        template=custom_prompt_template, input_variables=["context", "question"]
    )
    return prompt

# Function to set up the retrieval QA chain
def retrieval_qa_chain(llm, prompt, db):
    
    ##############################################################################################
    # TODO Set up the retrieval QA chain
    qa_chain = ...
    ##############################################################################################
    
    return qa_chain

# Function to load the model
def load_llm():
    
    ############################################################################
    # TODO Load the locally downloaded model here
    llm = ...
    ############################################################################

    return llm

# Function to set up the QA bot
def qa_bot():

    ############################################################################
    # TODO Set up the embedding model here
    embeddings = ...
    ############################################################################
    
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)

    return qa

# Function to get the final result
def final_result(query):
    qa_result = qa_bot()
    response = qa_result({"query": query})
    return response

# Function to be called when a chat starts
@cl.on_chat_start
async def start():
    chain = qa_bot()
    msg = cl.Message(content="Starting the bot...")
    await msg.send()
    msg.content = "Hi, Welcome to the Camino Santiago Bot. What is your query?"
    await msg.update()

    cl.user_session.set("chain", chain)

# Function to be called when a message is received
@cl.on_message
async def main(message):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True
    res = await chain.acall(message, callbacks=[cb])
    answer = res["result"]
    sources = res["source_documents"]

    if sources:
        answer += f"\nSources:" + str(sources)
    else:
        answer += "\nNo sources found"

    await cl.Message(content=answer).send()