import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
import cloudscraper
from bs4 import BeautifulSoup

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")


def get_vectorstore_from_url(url, google_api_key):
    if not google_api_key:
        st.error("Please provide a Google API key.")
        return None
    try:
        # Create embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=google_api_key)

        # Use cloudscraper to bypass Cloudflare
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )

        # Fetch the webpage
        response = scraper.get(url)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text content
        text_content = soup.get_text(separator='\n', strip=True)

        # Create a Document object
        documents = [Document(page_content=text_content, metadata={"source": url})]

        # Split documents into chunks and create vector store
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        document_chunks = text_splitter.split_documents(documents)
        vector_store = Chroma.from_documents(document_chunks, embeddings)

        return vector_store

    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return None

def get_context_retriever_chain(vector_store, google_api_key):
    # Create retriever chain with history awareness
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)
    retriever = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation.")
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain

def get_conversational_rag_chain(retriever_chain, google_api_key):
    # Create conversational RAG chain
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)

    # Define prompt for combining documents
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the below context:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    # Create stuff documents chain
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

# App configuration
st.set_page_config(page_title="Chat with Website", page_icon="🤖")
st.title("Chat with Websites")

# side bar for inputs
with st.sidebar:
    st.header("Settings")

    # if forget to input API key in .env file, can place within the website on the sidebar
    if not google_api_key:
        google_api_key = st.text_input("Google API Key", type="password")
    web_url = st.text_input("Website URL")

# Checks for API key if not provided
if not google_api_key:
    st.info("Please enter your Google API Key to continue.")
elif not web_url:
    st.info("Please enter a Website URL to start.")

# Main chat interface
else:
    # Session state to store chat history and vector store
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [AIMessage(content="Hello, I am a bot. How can I help you?")]
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vectorstore_from_url(web_url, google_api_key)

    # Create retriever chain and conversational RAG chain
    if st.session_state.vector_store:
        retriever_chain = get_context_retriever_chain(st.session_state.vector_store, google_api_key)
        conversation_rag_chain = get_conversational_rag_chain(retriever_chain, google_api_key)

        user_query = st.chat_input("Type your message here...")
        if user_query is not None and user_query != "":
            st.session_state.chat_history.append(HumanMessage(content=user_query))

            response = conversation_rag_chain.invoke({
                "chat_history": st.session_state.chat_history,
                "input": user_query
            })

            st.session_state.chat_history.append(AIMessage(content=response['answer']))

    # Display chat history
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)