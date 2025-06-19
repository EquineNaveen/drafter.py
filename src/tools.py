"""
Custom tools for the drafting agent to use.
"""

import os
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool

from src.utils import save_document, format_email_draft, parse_email_parts

@tool
def update_document(content: str) -> str:
    """
    Update the current document with provided content.
    
    Args:
        content: New document content
        
    Returns:
        Confirmation message with updated content
    """
    # This will be handled by the agent state
    return f"Document has been updated successfully! The current content is:\n{content}"

@tool
def save_document_tool(filename: str, content: str) -> str:
    """
    Save the current document to a text file.
    
    Args:
        filename: Name for the text file
        content: Content to save
        
    Returns:
        Confirmation message
    """
    try:
        file_path = save_document(content, filename)
        return f"Document has been saved successfully to '{file_path}'."
    except Exception as e:
        return f"Error saving document: {str(e)}"

@tool
def format_as_email(subject: str, recipient: str, sender: str, content: str, signature: Optional[str] = None) -> str:
    """
    Format content as an email.
    
    Args:
        subject: Email subject
        recipient: Email recipient
        sender: Email sender
        content: Email content
        signature: Optional signature
        
    Returns:
        Formatted email text
    """
    email = format_email_draft(
        subject=subject,
        recipient=recipient,
        sender=sender,
        content=content,
        signature=signature
    )
    
    return email

@tool
def analyze_email_parts(email_content: str) -> str:
    """
    Analyze and extract parts from an email.
    
    Args:
        email_content: Raw email content
        
    Returns:
        JSON string with parsed email parts
    """
    parts = parse_email_parts(email_content)
    
    return f"""Email parts analysis:
    
Subject: {parts.get('subject', 'Not found')}
To: {parts.get('recipient', 'Not found')}
From: {parts.get('sender', 'Not found')}
Body: {parts.get('body', 'Not found')}
"""

@tool
def generate_email_template(template_type: str) -> str:
    """
    Generate a template for a specific type of email.
    
    Args:
        template_type: Type of email template to generate 
                     (options: formal, informal, request, follow_up, thank_you)
        
    Returns:
        Template text for the specified email type
    """
    templates = {
        "formal": """
Subject: [Formal Subject]

To: [Recipient]
From: [Your Name]

Dear [Recipient Name],

I hope this email finds you well. I am writing to [purpose of email].

[Main content paragraph 1]

[Main content paragraph 2]

Thank you for your time and consideration.

Best regards,
[Your Name]
[Your Title]
[Contact Information]
""",
        
        "informal": """
Subject: [Informal Subject]

To: [Recipient]
From: [Your Name]

Hi [Recipient First Name],

Hope you're doing well! I wanted to [purpose of email].

[Main content paragraph]

Let me know what you think!

Cheers,
[Your Name]
""",
        
        "request": """
Subject: Request: [Request Topic]

To: [Recipient]
From: [Your Name]

Dear [Recipient Name],

I hope this email finds you well. I am writing to request [specific request].

[Details of request]

[Reason for request]

[Timeline or deadline if applicable]

Thank you for considering my request. I look forward to your response.

Best regards,
[Your Name]
[Contact Information]
""",
        
        "follow_up": """
Subject: Follow-up: [Previous Topic]

To: [Recipient]
From: [Your Name]

Dear [Recipient Name],

I hope you're doing well. I'm writing to follow up on [previous discussion/email/meeting].

[Reference to previous communication]

[Follow-up questions or comments]

[Next steps or action items]

Thank you for your attention to this matter.

Best regards,
[Your Name]
""",
        
        "thank_you": """
Subject: Thank You for [Reason]

To: [Recipient]
From: [Your Name]

Dear [Recipient Name],

I wanted to take a moment to express my sincere gratitude for [reason for thanks].

[Additional details about what you're thankful for]

[Impact of their actions]

Thank you again for [brief restatement].

Warm regards,
[Your Name]
"""
    }
    
    template = templates.get(template_type.lower())
    
    if not template:
        available_templates = ", ".join(templates.keys())
        return f"Template type '{template_type}' not found. Available templates: {available_templates}"
    
    return template
