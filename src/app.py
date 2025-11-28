import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader




# simulate we already have the logic behind the chatbot
def get_response(user_input):
    return "I don't know"

#
def get_vectorstore_from_url(url):
    # get the text in document form
    loader = WebBaseLoader(url)
    documents = loader.load()
    return documents

# Shows in the tab of the browser (app config)
st.set_page_config(page_title="Chat with Website", page_icon="🤖")
st.title("Chat with Websites")

# chat history
if "chat_history" not in st.session_state: # Session state allows streamlit to recover past messages and not reload the whole script every time an event occurs
    st.session_state.chat_history = [
    AIMessage(content="Hello, I am a bot. How can I help you?") # Init message
    ]


# Has a side bar on the web page
with st.sidebar:
    st.header("Settings")
    web_url = st.text_input("Website URL") # takes in the website url

if web_url is None or web_url =="":
    st.info("Please Enter any Website URL to Start")

else:
    documents = get_vectorstore_from_url(web_url)
    with st.sidebar:
        st.write(documents)

    # Input bar for dialogs (user inputs)
    user_query = st.chat_input("Type your message here...")

    if user_query is not None and user_query != "":
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)

    # Debugg
    # with st.sidebar:
    #     st.write(st.session_state.chat_history)
