import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import draft
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.draft import run_document_agent, process_user_input, document_content

def init_session_state():
    """Initialize all session state variables"""
    # Initialize app and state if they don't exist
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        app, state = run_document_agent()
        st.session_state.app = app
        st.session_state.state = state
    
    # Initialize message history if it doesn't exist
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        # Add initial welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": "I'm ready to help you update a document. What would you like to create?"
        })
    
    # Initialize processing flag if it doesn't exist
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def handle_message(content):
    """Add assistant messages to the session state"""
    if content.startswith("🛠️ TOOL RESULT:"):
        st.session_state.messages.append({"role": "tool", "content": content})
    elif content.startswith("🔧 USING TOOLS:"):
        st.session_state.messages.append({"role": "system", "content": content})
    else:
        st.session_state.messages.append({"role": "assistant", "content": content})

def process_input(user_input):
    """Process user input and update the UI"""
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.clear_input = True
        new_state, should_end = process_user_input(
            user_input, 
            st.session_state.state,
            handle_message
        )
        st.session_state.state = new_state
        if should_end:
            st.session_state.messages.append({
                "role": "system", 
                "content": "Document has been saved. You can start a new session."
            })
        # Rerun after response is appended
        st.rerun()

def reset_session():
    """Reset the session state for a new conversation"""
    # Reset the app and state
    app, state = run_document_agent()
    st.session_state.app = app
    st.session_state.state = state
    # Reset messages
    st.session_state.messages = [{
        "role": "assistant",
        "content": "I'm ready to help you update a document. What would you like to create?"
    }]
    # Reset processing flag
    st.session_state.processing = False

def main():
    st.set_page_config(
        page_title="Drafter - AI Writing Assistant",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("📝 Drafter - AI Writing Assistant")
    
    # Initialize session state
    init_session_state()

    # Create two columns: chat and document previews
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Document preview section
        st.subheader("Document Preview")
        
        # Import document_content here to get the current value
        from src.draft import document_content
        
        # Preview the document content
        preview = document_content if document_content else "No content yet"
        st.text_area("Current Document", value=preview, height=400, disabled=True)
        
        # New session button
        if st.button("New Session"):
            reset_session()
            st.rerun()
    
    with col1:
        # Chat interface section
        st.subheader("Chat with Drafter")
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"**👤 You:** {message['content']}")
                elif message["role"] == "assistant":
                    st.markdown(f"**🤖 Drafter:** {message['content']}")
                elif message["role"] == "tool":
                    st.markdown(f"**{message['content']}**")
                elif message["role"] == "system":
                    st.markdown(f"*{message['content']}*")
                st.markdown("---")
        
        # Input area for new messages
        # Generate a new key for the text area if we need to clear it
        input_key = f"user_input_{len(st.session_state.messages)}" if st.session_state.get('clear_input', False) else "user_input"
        
        # Reset the clear flag
        if st.session_state.get('clear_input', False):
            st.session_state.clear_input = False
            
        user_input = st.text_area("Your message", height=100, key=input_key)
        
        # Submit button
        col1, col2 = st.columns([4, 1])
        with col2:
            submit_button = st.button("Send", use_container_width=True)
        
        # Process the input when the button is clicked
        if submit_button and user_input:
            process_input(user_input)
            # No need to rerun here, handled in process_input

if __name__ == "__main__":
    main()
