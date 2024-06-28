# Chainlit and OpenAI Integration Example

This project demonstrates how to integrate OpenAI's GPT models with Chainlit, a framework for building interactive tools and applications. The example provided in `app.py` showcases the setup and basic usage of OpenAI's API within a Chainlit application.

## Features

- **OpenAI API Integration:** Utilizes the OpenAI API to access powerful language models like GPT-3.5-turbo.
- **Chainlit Framework:** Leverages Chainlit to create interactive steps and handle messages within the application.
- **Environment Variable Management:** Uses a `.env` file to securely manage the OpenAI API key.

## Setup

1. **Install Dependencies:** Ensure you have Python installed, then install the required libraries using pip:
   ```bash
   pip install chainlit openai python-dotenv
   ```

2. **Environment Variables:** Create a `.env` file in the root directory and add your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY=your-api-key
   ```

3. **Running the Application:** Use the following command to run the application:
   ```bash
   chainit run app.py
   ```

## How It Works

- **Initialization:** The application starts by importing necessary libraries and loading the OpenAI API key from the `.env` file.
- **OpenAI Client:** An `AsyncOpenAI` client is initialized with the API key, allowing asynchronous communication with OpenAI's servers.
- **Chainlit Instrumentation:** The OpenAI client is instrumented with Chainlit, enabling the integration of OpenAI's capabilities within Chainlit's interactive steps.
- **Model Settings:** Settings for the OpenAI model are defined, including the model version (`gpt-3.5-turbo`) and the temperature, which controls the randomness of the model's output.
- **Chainlit Steps and Message Handling:** The application defines a Chainlit step (`tool`) that returns a simple message, and an asynchronous message handler (`on_message`) that can process incoming messages.

## Conclusion

This example serves as a starting point for integrating OpenAI's GPT models with Chainlit applications. By following the setup and structure provided, developers can build interactive tools that leverage the capabilities of advanced language models.
