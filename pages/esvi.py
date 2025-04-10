import streamlit as st
from google import genai

# The majority of this code is built upon Streamlit's amazing article on LLM Apps:
# https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps

# Page configuration
st.set_page_config(
    page_title="Esvi - Hurricane Safety Education Assistant",
    page_icon="🌀",
    layout="centered"
)

st.title("🌀 Esvi - Hurricane Safety Education Assistant")
st.markdown("Ask questions about hurricane damage prevention and get educational information.")

# User inputs API Key, below code will not run until it works
key = st.text_input("Enter your Google Gemini API key:", type="password")
if not key:
    st.info("Please enter your Google Gemini API key to start chatting with Esvi.")
    st.link_button('Get a Gemini API Key', 'https://aistudio.google.com/')
    st.stop()

# Initialize Gemini client
try:
    client = genai.Client(api_key=key)
except Exception as e:
    st.error(f"Error initializing Gemini client: {str(e)}")
    st.stop()

INITIAL_PROMPT = "Hi! I'm Esvi, your assistant for hurricane safety and disaster preparedness. How can I help you today?"

SYSTEM_PROMPT = """You are Esvi, a friendly and educational AI assistant focused on hurricane safety, disaster preparedness, and social vulnerability education. Your main goals are:
• Educate users about hurricane safety measures and disaster preparedness.
• Provide insights into social vulnerability and how it impacts disaster response.
• Share reliable, evidence-based information about disaster preparedness and recovery.
• Help users understand risk factors such as proximity to hurricane paths, social vulnerability indices, and critical facilities.

Key guidelines:
• Keep responses concise and easy to understand.
• Respond in bulleted lists when convenient
• Provide actionable advice for hurricane preparedness and safety.
• Redirect users to hurricane-related topics if they ask about unrelated subjects.
• Remind users that this is for educational purposes only and they should consult local authorities or experts for personalized advice.

Example redirection: "While I understand your interest in [unrelated topic], I'm specialized in hurricane safety and disaster preparedness. Would you like to learn about:
• Hurricane safety tips
• How to prepare for a hurricane
• Understanding social vulnerability
• Risk factors for coastal communities"

Remember: Always encourage consulting local authorities or experts for personalized advice."""

# SIDEBAR
with st.sidebar:
    model = st.selectbox(
        "How would you like to be contacted?",
        ("gemini-1.5-flash", "gemini-2.0-flash"),
    )

if st.sidebar.button("Start New Chat"):
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": INITIAL_PROMPT}
    ]
    try:
        client.models.generate_content(model=model, contents=SYSTEM_PROMPT)
    except Exception as e:
        error_message = str(e)
        if "API key not valid" in error_message:
            st.error("Error initializing model: Invalid API key. Please provide a valid API key.")
        else:
            st.error(f"Error resetting chat: {error_message}")

with st.sidebar:
    st.markdown("---")
    st.markdown("""
    ### About Esvi
    Esvi is your educational assistant focused on:
    - Hurricane safety and disaster preparedness
    - Social vulnerability education
    - Evidence-based insights for resilience
    
    *For educational purposes only. Always consult local authorities or experts for personalized advice.*
    """)

# Initialize the model with system prompt
try:
    client.models.generate_content(model=model, contents=SYSTEM_PROMPT)
except Exception as e:
    error_message = str(e)
    if "API key not valid" in error_message:
        st.error("Error initializing model: Invalid API key. Please provide a valid API key.")
    else:
        st.error(f"Error initializing model: {error_message}")
    st.stop()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": INITIAL_PROMPT}
    ]

# Display chat history in a chat-like format (exclude system messages)
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# User input for the chatbot
if prompt := st.chat_input("Ask about hurricane safety or disaster preparedness..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                # Include the full conversation history for context
                conversation_history = "\n".join([msg["content"] for msg in st.session_state.messages])
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=conversation_history
                )
                
                # Format response
                assistant_response = (
                    response.text
                    .replace("\n* ", "\n• ")  # Convert single asterisks used for bullet points to proper bullets
                    .replace("**", "**")      # Preserve existing bold syntax
                    .replace("\n", "\n\n")    # Add spacing between paragraphs
                )
                st.markdown(assistant_response)
            except Exception as e:
                error_message = str(e)
                if "API key not valid" in error_message:
                    st.error("Error: Invalid API key. Please provide a valid API key.")
                else:
                    st.error(f"An error occurred: {error_message}")
                assistant_response = "I encountered an error. Please try again."
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})