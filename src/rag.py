"""
RAG (Retrieval Augmented Generation) implementation.
This module handles document processing, embedding, and retrieval functionality.
"""

import os
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool

from src.models import get_embeddings_model
from src.utils import ensure_directory_exists

# Default storage location for vector database
PERSIST_DIRECTORY = os.environ.get("VECTOR_DB_PATH", os.path.join(os.getcwd(), "vector_db"))
DEFAULT_COLLECTION = "email_drafting_assistant"

class RAGProcessor:
    """
    Handles document processing and retrieval for the RAG system.
    """
    
    def __init__(
        self, 
        persist_directory: str = PERSIST_DIRECTORY,
        collection_name: str = DEFAULT_COLLECTION,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the RAG processor.
        
        Args:
            persist_directory: Directory to persist the vector database
            collection_name: Name for the vector collection
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between text chunks
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings model
        self.embeddings = get_embeddings_model()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Create directory if it doesn't exist
        ensure_directory_exists(self.persist_directory)
        
        # Initialize vector database
        self._init_vectorstore()
    
    def _init_vectorstore(self):
        """Initialize or load existing vector database."""
        try:
            # Try to load existing database
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            print(f"Loaded existing ChromaDB vector store from {self.persist_directory}")
        except Exception as e:
            # Create new database if loading fails
            print(f"Creating new ChromaDB vector store: {str(e)}")
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory
            )
    
    def process_document(self, file_path: str) -> List[Document]:
        """
        Process a document and add it to the vector database.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of processed document chunks
        """
        # Determine document type and load accordingly
        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            # Default to text loader for other file types
            loader = TextLoader(file_path)
        
        # Load the document
        documents = loader.load()
        
        # Split the document into chunks
        document_chunks = self.text_splitter.split_documents(documents)
        
        # Add to vector database
        self.vectorstore.add_documents(document_chunks)
        
        # Persist the vector database
        try:
            if hasattr(self.vectorstore, 'persist'):
                self.vectorstore.persist()
        except Exception as e:
            print(f"Warning: Failed to persist vector store: {str(e)}")
        
        return document_chunks
    
    def process_multiple_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Process multiple documents and add them to the vector database.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            Combined list of processed document chunks
        """
        all_chunks = []
        for file_path in file_paths:
            chunks = self.process_document(file_path)
            all_chunks.extend(chunks)
        return all_chunks
    
    def process_directory(self, directory_path: str, glob_pattern: str = "**/*") -> List[Document]:
        """
        Process all supported documents in a directory.
        
        Args:
            directory_path: Path to directory containing documents
            glob_pattern: Pattern to match files
            
        Returns:
            List of processed document chunks
        """
        if not os.path.exists(directory_path):
            print(f"Directory does not exist: {directory_path}")
            return []
        
        loader = DirectoryLoader(
            directory_path,
            glob=glob_pattern,
            show_progress=True
        )
        
        documents = loader.load()
        document_chunks = self.text_splitter.split_documents(documents)
        
        # Add to vector database
        self.vectorstore.add_documents(document_chunks)
        
        # Persist the vector database
        try:
            if hasattr(self.vectorstore, 'persist'):
                self.vectorstore.persist()
        except Exception as e:
            print(f"Warning: Failed to persist vector store: {str(e)}")
        
        return document_chunks
    
    def get_retriever(self, search_type: str = "similarity", k: int = 5):
        """
        Get a retriever for querying the vector database.
        
        Args:
            search_type: Type of search to perform
            k: Number of results to retrieve
            
        Returns:
            Configured retriever
        """
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )
    
    def query(self, query_text: str, k: int = 5) -> List[Document]:
        """
        Query the vector database for similar documents.
        
        Args:
            query_text: Text to search for
            k: Number of results to retrieve
            
        Returns:
            List of relevant documents
        """
        retriever = self.get_retriever(k=k)
        return retriever.invoke(query_text)
    
    def create_retrieval_tool(self, description: str = None):
        """
        Create a tool for retrieving information from the vector database.
        
        Args:
            description: Custom description for the tool
            
        Returns:
            A tool function for document retrieval
        """
        if description is None:
            description = f"""
            This tool searches and returns information from the document database.
            Use this tool to find information relevant to drafting emails.
            """
        
        @tool
        def retrieval_tool(query: str) -> str:
            """
            Search the document database for information.
            
            Args:
                query: Search query
                
            Returns:
                Retrieved information as a string
            """
            docs = self.query(query)
            
            if not docs:
                return "No relevant information found in the document database."
            
            results = []
            for i, doc in enumerate(docs):
                # Include metadata if available
                metadata_str = ""
                if hasattr(doc, "metadata") and doc.metadata:
                    source = doc.metadata.get("source", "Unknown")
                    page = doc.metadata.get("page", "")
                    metadata_str = f" [Source: {source}, Page: {page}]" if page else f" [Source: {source}]"
                
                results.append(f"Document {i+1}{metadata_str}:\n{doc.page_content}")
            
            return "\n\n".join(results)
        
        # Update the tool's docstring
        retrieval_tool.__doc__ = description
        
        return retrieval_tool
