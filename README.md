# Chat with Website

This project is a Streamlit application that allows users to chat with any website. You provide a URL, and the application will load the website's content, allowing you to ask questions about it.

## How it Works

The application is built with Python using the following libraries:

-   **Streamlit:** For creating the web interface.
-   **Langchain:** For loading the website content.

When you enter a URL, the application uses `langchain`'s `WebBaseLoader` to fetch the content of the website. The content is then displayed in the sidebar.

The chat functionality is currently a placeholder. The `get_response` function is not yet implemented, so the chatbot will always respond with "I don't know".

## How to Run

1.  **Prerequisites:**
    *   Python 3.7+
    *   pip

2.  **Installation:**

    Install the required Python libraries:

    ```bash
    pip install streamlit langchain-community
    ```

3.  **Running the Application:**

    To start the application, run the following command in your terminal:

    ```bash
    streamlit run src/app.py
    ```

    The application will open in your web browser.

## Future Improvements

-   **Implement a RAG model:** The current chatbot is a placeholder. The next step is to implement a Retrieval-Augmented Generation (RAG) model to provide intelligent answers based on the website's content.
-   **Create a vector store:** To make the RAG model more efficient, a vector store can be created from the website's content. This will allow for faster retrieval of relevant information.
-   **Improve the UI:** The user interface can be improved to provide a better user experience.