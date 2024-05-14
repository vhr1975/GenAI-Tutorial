---
title: 'OpenAI Chat Bot'
tags: ['openai', 'chainlit', 'qa']
---

# OpenAI Q&A Bot

This repository contains a Chainlit application that provides a question-answering service using documents stored in a Chroma vector store. It allows users to upload PDF documents, which are then chunked, embedded, and indexed for efficient retrieval. When a user asks a question, the application retrieves relevant document chunks and uses OpenAI's language model to generate an answer, citing the sources it used.

## High-Level Description

The `app.py` script performs the following functions:

1. **Question Answering (`on_message`)**: When a user asks a question, the application retrieves relevant document chunks and generates an answer using OpenAI's language model, providing the sources for transparency.

## Quickstart

### Prerequisites

- Python 3.11 or higher
- Chainlit installed

### Setup and Run

1. **Install Dependencies:**

Install the required Python packages specified in `requirements.txt`.

```shell
pip install -r requirements.txt
```

2. **Run the Application:**


## Code Definitions

- `on_chat_start`: Event handler that sets up the Chainlit session with the necessary components for question answering.
- `on_message`: Event handler that processes user messages, retrieves relevant information, and sends back an answer.
- `PostMessageHandler`: Callback handler that posts the sources of the retrieved documents as a Chainlit element.


## See Also
