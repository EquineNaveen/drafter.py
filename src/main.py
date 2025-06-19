"""
Main entry point for the AI-Powered Document Drafting Assistant.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the parent directory to the Python path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def main(parsed_args=None):
    """
    Main function to start the application.
    
    Args:
        parsed_args: Pre-parsed command line arguments (optional)
    """
    if parsed_args is None:
        # Parse arguments if not provided
        parser = argparse.ArgumentParser(
            description="AI-Powered Document Drafting Assistant"
        )
        
        parser.add_argument(
            "--mode", 
            type=str,
            choices=["web", "cli"],
            default="web",
            help="Run mode: 'web' for Streamlit interface, 'cli' for command line"
        )
        
        args = parser.parse_args()
    else:        args = parsed_args
    
    # Always run the Streamlit app since CLI mode is removed
    print("Starting web interface...")
    os.system("streamlit run src/app.py")

# CLI mode has been removed to keep the application simpler
if __name__ == "__main__":
    main()
