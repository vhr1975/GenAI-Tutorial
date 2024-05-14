# Import necessary libraries and modules
from typing import List
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain.indexes import SQLRecordManager, index
from langchain.schema import Document
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableConfig
from langchain.callbacks.base import BaseCallbackHandler
import chainlit as cl
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai_api_key="your-openai-api-key" 

# Set chunk size and overlap for text splitting
chunk_size = 1024
chunk_overlap = 50

# Initialize OpenAIEmbeddings with your API key
embeddings_model = OpenAIEmbeddings(api_key=openai_api_key)

# Set the path to the directory containing PDFs
PDF_STORAGE_PATH = "./pdfs"

# Function to process PDFs and return a Chroma object for document search
def process_pdfs(pdf_storage_path: str):
    # Convert the path to a Path object and initialize an empty list for documents
    pdf_directory = Path(pdf_storage_path)
    docs = []  # type: List[Document]
    # Initialize a text splitter with the specified chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    # Loop through all PDF files in the directory
    for pdf_path in pdf_directory.glob("*.pdf"):
        # Load the PDF and split it into chunks
        loader = PyMuPDFLoader(str(pdf_path))
        documents = loader.load()
        docs += text_splitter.split_documents(documents)

    # Create a Chroma object from the documents
    doc_search = Chroma.from_documents(docs, embeddings_model)

    # Set up a SQLRecordManager for indexing
    namespace = "chromadb/my_documents"
    record_manager = SQLRecordManager(
        namespace, db_url="sqlite:///record_manager_cache.sql"
    )
    record_manager.create_schema()

    # Index the documents
    index_result = index(
        docs,
        record_manager,
        doc_search,
        cleanup="incremental",
        source_id_key="source",
    )

    print(f"Indexing stats: {index_result}")

    return doc_search

# Process the PDFs and initialize the ChatOpenAI model
doc_search = process_pdfs(PDF_STORAGE_PATH)
model = ChatOpenAI(model_name="gpt-4", streaming=True, api_key=openai_api_key)

# Function to be called when a chat starts
@cl.on_chat_start
async def on_chat_start():
    # Set up the chat prompt template
    template = """Answer the question based only on the following context:

    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # Function to format the documents
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    # Get the retriever from the Chroma object
    retriever = doc_search.as_retriever()

    # Set up the runnable pipeline
    runnable = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    # Store the runnable in the user session
    cl.user_session.set("runnable", runnable)

# Function to be called when a message is received
@cl.on_message
async def on_message(message: cl.Message):
    # Get the runnable from the user session
    runnable = cl.user_session.get("runnable")  # type: Runnable
    msg = cl.Message(content="")

    # Callback handler for handling the retriever and LLM processes
    class PostMessageHandler(BaseCallbackHandler):
        """
        Used to post the sources of the retrieved documents as a Chainlit element.
        """

        def __init__(self, msg: cl.Message):
            BaseCallbackHandler.__init__(self)
            self.msg = msg
            self.sources = set()  # To store unique pairs

        # Function to be called when the retriever ends
        def on_retriever_end(self, documents, *, run_id, parent_run_id, **kwargs):
            for d in documents:
                source_page_pair = (d.metadata['source'], d.metadata['page'])
                self.sources.add(source_page_pair)  # Add unique pairs to the set

        # Function to be called when the LLM ends
        def on_llm_end(self, response, *, run_id, parent_run_id, **kwargs):
            if len(self.sources):
                sources_text = "\n".join([f"{source}#page={page}" for source, page in self.sources])
                self.msg.elements.append(
                    cl.Text(name="Sources", content=sources_text, display="inline")
                )

    # Run the runnable pipeline and send the result
    async with cl.Step(type="run", name="QA Assistant"):
        async for chunk in runnable.astream(
            message.content,
            config=RunnableConfig(callbacks=[
                cl.LangchainCallbackHandler(),
                PostMessageHandler(msg)
            ]),
        ):
            await msg.stream_token(chunk)

    await msg.send()