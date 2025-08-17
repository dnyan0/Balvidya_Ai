

import streamlit as st
import os
from rag import generate_answer

# Define class-subject mapping
CLASS_SUBJECTS = {
    "5th": ["Mathematics", "English"],
    "6th": ["Mathematics", "Science", "English"],
    "7th": ["Mathematics", "Science", "English"],
    "8th": ["Mathematics", "Science", "English"],
    "9th": ["Mathematics-1", "Mathematics-2", "Science", "English"],
    "10th": ["Mathematics-1", "Mathematics-2", "Science-1", "Science-2", "English"],
    "11th": ["Mathematics", "Physics", "Chemistry", "Biology", "English"],
    "12th": ["Mathematics", "Physics", "Chemistry", "Biology", "English"]
}

def render_sidebar():
    st.sidebar.title("Subject-based Q&A")
    st.sidebar.markdown("Select class and subject to begin")
    
    # Class selection
    selected_class = st.sidebar.selectbox(
        "Select Class",
        options=list(CLASS_SUBJECTS.keys()),
        index=None,
        placeholder="Choose a class"
    )
    
    # Subject selection
    if selected_class:
        subjects = CLASS_SUBJECTS.get(selected_class, [])
        selected_subject = st.sidebar.selectbox(
            "Select Subject",
            options=subjects,
            index=None,
            placeholder="Choose a subject"
        )
        
        if selected_subject:
            # Initialize chat history for this subject if it doesn't exist
            key = (selected_class, selected_subject)
            if key not in st.session_state.chat_histories:
                st.session_state.chat_histories[key] = []
            
            # Update current class/subject if changed
            if (selected_class != st.session_state.current_class or 
                selected_subject != st.session_state.current_subject):
                st.session_state.current_class = selected_class
                st.session_state.current_subject = selected_subject
                st.rerun()
    
    # Clear chat button
    if st.session_state.get('current_class') and st.session_state.get('current_subject'):
        key = (st.session_state.current_class, st.session_state.current_subject)
        if st.session_state.chat_histories.get(key):
            st.sidebar.markdown("---")
            if st.sidebar.button("Clear Chat"):
                st.session_state.chat_histories[key] = []
                st.rerun()

def render_chat_interface():
    if not st.session_state.get('current_class') or not st.session_state.get('current_subject'):
        st.info("Please select a class and subject to start asking questions.")
        return
    
    key = (st.session_state.current_class, st.session_state.current_subject)
    st.title(f"Q&A: {st.session_state.current_subject} for Class {st.session_state.current_class}")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_histories.get(key, []):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask a question...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_histories[key].append({"role": "user", "content": user_input})
        
        # Generate and display response
        with st.spinner("Generating response..."):
            response = generate_answer(
                user_input, 
                st.session_state.current_class, 
                st.session_state.current_subject
            )
        
        # Add assistant response to chat history
        st.session_state.chat_histories[key].append({"role": "assistant", "content": response})
        
        # Rerun to update the chat interface
        st.rerun()

