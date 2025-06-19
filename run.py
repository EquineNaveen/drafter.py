"""
Entry point for the AI-Powered Document Drafting Assistant.
Run this script to launch the application.

Usage:
    python run.py    # Start the web interface (Streamlit)
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def ensure_dependencies():
    """Check and inform about missing dependencies."""
    try:
        import sentence_transformers
        print("✓ sentence_transformers is installed")
    except ImportError:
        print("\n⚠️ Warning: sentence_transformers package is not installed.")
        print("For better embedding performance, install it with:")
        print("pip install sentence-transformers\n")
    
    try:
        import chromadb
        print("✓ chromadb is installed")
    except ImportError:
        print("\n⚠️ Warning: chromadb package is not installed.")
        print("For vector storage, install it with:")
        print("pip install chromadb\n")
    
    try:
        import streamlit
        print("✓ streamlit is installed")
    except ImportError:
        print("\n⚠️ Warning: streamlit package is not installed.")
        print("For the web interface, install it with:")
        print("pip install streamlit\n")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check for API token
    if not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
        print("\n⚠️ Warning: HUGGINGFACEHUB_API_TOKEN not found in environment variables")
        print("Please add it to your .env file for the application to work correctly\n")
    
    # No need for command line arguments as we only support web interface now
    class WebArgs:
        """Simple class to simulate args with web mode only."""
        def __init__(self):
            self.mode = "web"
    
    args = WebArgs()
    
    # Ensure required packages are installed
    ensure_dependencies()
    
    from src.main import main
    main(args)


