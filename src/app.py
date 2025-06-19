"""
Streamlit web application for the AI-Powered Document Drafting Assistant.
"""

import os
import streamlit as st
import tempfile
import sys
from typing import Dict, List, Any

# Add the parent directory to the Python path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_email_drafting_agent
from src.rag import RAGProcessor
from src.utils import save_document

# Configure Streamlit page
st.set_page_config(
    page_title="AI Email Drafting Assistant",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "document_content" not in st.session_state:
    st.session_state.document_content = ""
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "rag_processor" not in st.session_state:
    st.session_state.rag_processor = RAGProcessor()
if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []

# Helper functions
def process_uploaded_file(uploaded_file):
    """Process an uploaded file and add it to the RAG system."""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name
        
        # Process the document
        st.session_state.rag_processor.process_document(temp_path)
        
        # Add to the list of uploaded documents
        st.session_state.uploaded_documents.append(uploaded_file.name)
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return True
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return False

def create_agent():
    """Create an email drafting agent with the current RAG processor."""
    return create_email_drafting_agent(
        rag_processor=st.session_state.rag_processor,
        model_name=st.session_state.model_name,
        temperature=st.session_state.temperature,
        verbose=False
    )

def handle_user_input(user_input):
    """Handle user input and update the conversation history."""
    if not user_input:
        return
    
    # Add user message to conversation
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Create agent and get response
    with st.spinner("Thinking..."):
        agent = create_agent()
        result = agent.invoke(user_input, st.session_state.document_content)
        
        # Extract document content
        st.session_state.document_content = result.get("document", st.session_state.document_content)
        
        # Extract AI messages from the result
        for message in result.get("messages", []):
            if message.type == "ai":
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": message.content
                })
            elif message.type == "tool" and "Document has been saved successfully" in message.content:
                st.session_state.conversation_history.append({
                    "role": "system",
                    "content": message.content
                })

# Sidebar for configuration
with st.sidebar:
    st.title("📧 Email Drafting Assistant")    # Model selection
    st.subheader("Model Settings")
    st.session_state.model_name = st.selectbox(
        "Select Model",
        ["TinyLlama/TinyLlama-1.1B-Chat-v1.0", "google/flan-t5-base", "google/flan-t5-small", "facebook/bart-large-cnn"],
        index=0
    )
    
    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )
    
    # Document upload section
    st.subheader("Upload Documents")
    uploaded_file = st.file_uploader(
        "Upload documents for context",
        type=["pdf", "txt", "docx"],
        help="Upload documents to provide context for email drafting"
    )
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                success = process_uploaded_file(uploaded_file)
                if success:
                    st.success(f"Successfully processed: {uploaded_file.name}")
    
    # Display uploaded documents
    if st.session_state.uploaded_documents:
        st.subheader("Uploaded Documents")
        for doc in st.session_state.uploaded_documents:
            st.text(f"• {doc}")
    
    # Reset button
    if st.button("Start New Draft"):
        st.session_state.document_content = ""
        st.session_state.conversation_history = []

# Main content area - split into chat and document sections
col1, col2 = st.columns([1, 1])

# Document editing area
with col2:
    st.header("Email Draft")
    
    # Document display and editing
    document_content = st.text_area(
        "Current Draft",
        value=st.session_state.document_content,
        height=400,
        key="document_editor"
    )
    
    # Update document content if manually edited
    if document_content != st.session_state.document_content:
        st.session_state.document_content = document_content
    
    # Save document button
    col2_1, col2_2 = st.columns([1, 1])
    
    with col2_1:
        save_filename = st.text_input("Filename", value="email_draft.txt")
    
    with col2_2:
        if st.button("Save Draft") and st.session_state.document_content:
            try:
                file_path = save_document(st.session_state.document_content, save_filename)
                st.success(f"Draft saved to {file_path}")
                
                st.session_state.conversation_history.append({
                    "role": "system",
                    "content": f"Document has been saved successfully to '{file_path}'."
                })
            except Exception as e:
                st.error(f"Error saving draft: {str(e)}")

# Chat interface
with col1:
    st.header("Chat with Assistant")
    
    # Display conversation history
    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.conversation_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.chat_message("user").write(content)
            elif role == "assistant":
                st.chat_message("assistant").write(content)
            elif role == "system":
                st.info(content)
    
    # User input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        handle_user_input(user_input)
        st.rerun()

# Footer
st.markdown("---")
st.caption("AI-Powered Email Drafting Assistant © 2025")
