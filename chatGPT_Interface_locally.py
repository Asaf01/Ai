import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'

# Initialize OpenAI client
openai_client = OpenAI(api_key=api_key)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = [{"role": "system", "content": "You are a helpful assistant. You can format your responses using Markdown."}]

def send_message(user_message):
    st.session_state.conversation_history.append({"role": "user", "content": user_message})
    
    try:
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=st.session_state.conversation_history
        )
        assistant_message = response.choices[0].message.content.strip()
        st.session_state.conversation_history.append({"role": "assistant", "content": assistant_message})
        return assistant_message
    except Exception as e:
        return f"Error: {str(e)}"

st.title("ChatGPT Interface")

# Display chat history
for message in st.session_state.conversation_history:
    if message["role"] != "system":
        role = "You" if message["role"] == "user" else "ChatGPT"
        st.markdown(f"**{role}:**")
        st.markdown(message["content"])
        st.markdown("---")

# Input area
user_input = st.text_input("Your message:", key="user_input")
col1, col2 = st.columns([1, 5])

with col1:
    if st.button("Send"):
        if user_input.strip():
            assistant_response = send_message(user_input)
            st.rerun()  # Updated from experimental_rerun()

with col2:
    if st.button("Clear Chat"):
        st.session_state.conversation_history = [{"role": "system", "content": "You are a helpful assistant. You can format your responses using Markdown."}]
        st.rerun()  # Updated from experimental_rerun()
