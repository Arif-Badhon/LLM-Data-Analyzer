"""Chat interface component"""
import streamlit as st
from utils import client


def render_chat():
    """Render chat interface"""
    st.subheader("💬 Chat with LLM")
    
    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Input
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful data analysis assistant.",
        height=80
    )
    
    user_input = st.chat_input("Type your message...")
    
    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get response
        with st.spinner("🤖 Thinking..."):
            messages = [
                {"role": "user", "content": user_input}
            ]
            response = client.chat(messages, system_prompt)
            
            if "error" in response:
                st.error(f"Error: {response['error']}")
            else:
                assistant_response = response.get("response", "No response")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
                with st.chat_message("assistant"):
                    st.write(assistant_response)
                
                # Show model info
                st.caption(f"Model: {response.get('model', 'Unknown')}")
        
        st.rerun()
