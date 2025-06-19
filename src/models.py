"""
Model initialization and configuration.
This file handles the setup of language models used in the application.
"""

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

# Import embedding models with fallback options
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None

# Import FakeEmbeddings for fallback
try:
    from langchain_community.embeddings import FakeEmbeddings
except ImportError:
    # Create a simple fake embeddings implementation if needed
    from langchain_core.embeddings import Embeddings
    import numpy as np
    
    class FakeEmbeddings(Embeddings):
        def __init__(self, size=384):
            self.size = size
            
        def embed_documents(self, texts):
            return [np.random.rand(self.size).tolist() for _ in texts]
            
        def embed_query(self, text):
            return np.random.rand(self.size).tolist()

# Load environment variables
load_dotenv()

def get_llm_model(repo_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0", temperature=0):
    """
    Initialize and return a Hugging Face language model.
    
    Args:
        repo_id: Repository ID of the Hugging Face model
        temperature: Temperature parameter for model output (0 = deterministic)
        
    Returns:
        A configured ChatHuggingFace model
    """
    # Use appropriate task based on model
    # Models that work well with the Inference API
    if "tinyllama" in repo_id.lower() or "bloom" in repo_id.lower():
        task = "text-generation"
    elif "flan" in repo_id.lower() or "bart" in repo_id.lower():
        task = "text2text-generation"
    else:
        # Default for most models
        task = "text-generation"
        
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        task=task,
        temperature=temperature,
    )
    
    return ChatHuggingFace(llm=llm)

def get_embeddings_model():
    """
    Initialize and return embeddings model for RAG.
    
    Returns:
        A configured embeddings model
    """
    try:
        # First try importing sentence_transformers to check if it's available
        import sentence_transformers
        
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
        )
    except ImportError:
        # If sentence_transformers is not available, fall back to a basic embedding model
        print("Warning: sentence_transformers not found. Using a basic embedding model instead.")
        print("For better performance, please run 'pip install sentence-transformers'")
        
        from langchain_community.embeddings import FakeEmbeddings
        
        # This is just a fallback for development/testing
        # It won't give meaningful results but will allow the app to start
        return FakeEmbeddings(size=384)

# Legacy function for compatibility - redirects to get_llm_model
def get_huggingface_model(repo_id="mistralai/Mistral-7B-Instruct-v0.2", temperature=0):
    """
    Initialize and return a Hugging Face language model.
    
    Args:
        repo_id: Repository ID of the Hugging Face model
        temperature: Temperature parameter for model output
        
    Returns:
        A configured ChatHuggingFace model
    """
    return get_llm_model(repo_id=repo_id, temperature=temperature)
