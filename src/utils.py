"""
Utility functions for the AI-Powered Document Drafting Assistant.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any

def ensure_directory_exists(directory_path: str):
    """
    Create directory if it doesn't exist.
    
    Args:
        directory_path: Path to check/create
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def save_document(content: str, filename: str = None, directory: str = "generated_documents"):
    """
    Save document content to a file.
    
    Args:
        content: Document content to save
        filename: Name for the saved file
        directory: Directory to save the document in
        
    Returns:
        Path to the saved file
    """
    # Create directory if it doesn't exist
    ensure_directory_exists(directory)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"document_{timestamp}.txt"
    
    # Add .txt extension if not present
    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"
    
    # Full path to save the document
    file_path = os.path.join(directory, filename)
    
    # Save the content
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return file_path

def load_document(file_path: str) -> str:
    """
    Load document content from a file.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        Content of the loaded file
    """
    if not os.path.exists(file_path):
        return ""
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def format_email_draft(
    subject: str, 
    recipient: str, 
    sender: str, 
    content: str,
    signature: str = None
) -> str:
    """
    Format content as an email draft.
    
    Args:
        subject: Email subject
        recipient: Email recipient
        sender: Email sender
        content: Email body content
        signature: Optional signature
        
    Returns:
        Formatted email text
    """
    email_template = f"""
Subject: {subject}

To: {recipient}
From: {sender}

{content}

"""
    
    if signature:
        email_template += f"\n{signature}"
    
    return email_template.strip()

def parse_email_parts(email_content: str) -> Dict[str, str]:
    """
    Parse parts from an email content string.
    
    Args:
        email_content: Raw email content
        
    Returns:
        Dictionary with parsed email parts
    """
    parts = {}
    
    # Try to extract subject
    if "Subject:" in email_content:
        subject_line = email_content.split("Subject:", 1)[1].split("\n", 1)[0].strip()
        parts["subject"] = subject_line
    
    # Try to extract recipient
    if "To:" in email_content:
        recipient_line = email_content.split("To:", 1)[1].split("\n", 1)[0].strip()
        parts["recipient"] = recipient_line
    
    # Try to extract sender
    if "From:" in email_content:
        sender_line = email_content.split("From:", 1)[1].split("\n", 1)[0].strip()
        parts["sender"] = sender_line
    
    # Extract body (everything after From: line)
    if "From:" in email_content:
        body = email_content.split("From:", 1)[1]
        # Remove first line (sender info)
        body = "\n".join(body.split("\n")[1:]).strip()
        parts["body"] = body
    else:
        # If no From: line, just use everything
        parts["body"] = email_content
    
    return parts
