import streamlit as st
from google import genai
import apikey

st.title("Florida SVI Chatbot")

st.warning("Note: To use this feature, you must upload your own API key for Google Gemini. \
           This information is not stored anywhere locally or within the app.")

st.link_button('Get a Gemini API Key', 'https://ai.google.dev/gemini-api/docs/api-key')

key = apikey.key

# Initialize the Gemini client
client = genai.Client(api_key=key)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history in a chat-like format
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# User input for the chatbot
if prompt := st.chat_input("Send a message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash", contents=prompt
                )
                assistant_response = response.text
                st.markdown(assistant_response)
            except Exception as e:
                assistant_response = f"An error occurred: {e}"
                st.error(assistant_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})