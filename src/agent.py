"""
Agent-based assistant implementation.
This module defines the agent state, nodes, and workflow.
"""

from typing import Annotated, Sequence, TypedDict, Dict, List, Any, Optional, Union
from operator import add as add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from src.models import get_llm_model
from src.rag import RAGProcessor
from src.tools import update_document, save_document_tool, format_as_email, analyze_email_parts, generate_email_template

# Define agent state
class AgentState(TypedDict):
    """State definition for the document drafting agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    document: str

# Helper functions
def get_system_prompt(document_content):
    """Generate system prompt based on current document content."""
    return f"""
    You are an AI-powered document drafting assistant specialized in email composition.
    
    Your capabilities include:
    1. Writing and editing email drafts
    2. Retrieving relevant information from documents to include in emails
    3. Formatting emails appropriately
    4. Saving drafts for later use
    
    Always maintain a professional and helpful tone. When drafting emails, ensure they are:
    - Clear and concise
    - Well-structured with proper formatting
    - Free of grammatical errors
    - Tailored to the specific context and purpose
    
    The current document content is:
    {document_content if document_content else "[No content yet. Start drafting an email.]"}
    
    Use the available tools to help with document creation, formatting, and saving.
    """

class EmailDraftingAgent:
    """Agent for drafting emails with RAG capabilities."""
    
    def __init__(
        self, 
        rag_processor: Optional[RAGProcessor] = None,
        model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        temperature: float = 0.7,
        verbose: bool = True
    ):
        """
        Initialize the email drafting agent.
        
        Args:
            rag_processor: RAG system for document retrieval
            model_name: Repository ID of the Hugging Face model to use
            temperature: Temperature for model generation
            verbose: Whether to print detailed information
        """
        self.llm = get_llm_model(repo_id=model_name, temperature=temperature)
        self.verbose = verbose
        
        # Initialize or use provided RAG processor
        self.rag = rag_processor if rag_processor else RAGProcessor()
        
        # Get document retrieval tool
        self.retrieval_tool = self.rag.create_retrieval_tool(
            "This tool searches the document database for information relevant to email drafting."
        )
        
        # Collect all tools
        self.tools = [
            update_document,
            save_document_tool,
            format_as_email,
            analyze_email_parts,
            generate_email_template,
            self.retrieval_tool
        ]
        
        # Bind tools to the language model
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the agent graph
        self.graph = self._build_graph()
        self.agent = self.graph.compile()
    
    def _build_graph(self):
        """Build the state graph for the agent workflow."""
        # Create the state graph
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", ToolNode(self.tools))
        
        # Set the entry point
        graph.set_entry_point("agent")
        
        # Add edges
        graph.add_edge("agent", "tools")
        graph.add_conditional_edges(
            "tools",
            self._should_continue,
            {
                "continue": "agent",
                "end": END
            }
        )
        
        return graph
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent node for processing messages."""
        # Get current state
        document_content = state.get("document", "")
        messages = list(state.get("messages", []))
        
        # Create system message
        system_prompt = get_system_prompt(document_content)
        system_message = SystemMessage(content=system_prompt)
        
        # Prepare messages for the LLM
        all_messages = [system_message] + messages
        
        # Get response from LLM
        if self.verbose:
            print("🤖 Generating response...")
        
        response = self.llm_with_tools.invoke(all_messages)
        
        if self.verbose:
            print(f"🤖 AI: {response.content}")
            if hasattr(response, "tool_calls") and response.tool_calls:
                print(f"🔧 Using tools: {[tc['name'] for tc in response.tool_calls]}")
        
        # Update document content if needed
        new_document_content = document_content
        
        # Check if the update_document tool was used
        if hasattr(response, "tool_calls"):
            for tool_call in response.tool_calls:
                if tool_call["name"] == "update_document":
                    if "content" in tool_call["args"]:
                        new_document_content = tool_call["args"]["content"]
                        if self.verbose:
                            print("📝 Document content updated")
                    break
        
        # Return updated state
        return {
            "messages": messages + [response],
            "document": new_document_content
        }
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if the agent should continue or end."""
        messages = state.get("messages", [])
        
        if not messages:
            return "continue"
        
        # Check if save_document_tool was used successfully
        for message in reversed(messages):
            if (isinstance(message, ToolMessage) and 
                "Document has been saved successfully" in message.content):
                return "end"
        
        return "continue"
    
    def invoke(self, query: str, document_content: str = ""):
        """
        Invoke the agent with a user query.
        
        Args:
            query: User query or input
            document_content: Initial document content (if any)
            
        Returns:
            Final state after agent execution
        """
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "document": document_content
        }
        
        # Run the agent
        return self.agent.invoke(initial_state)
    
    def stream(self, query: str, document_content: str = ""):
        """
        Stream the agent's execution.
        
        Args:
            query: User query or input
            document_content: Initial document content (if any)
            
        Returns:
            Generator yielding states during execution
        """
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "document": document_content
        }
        
        # Stream the agent's execution
        return self.agent.stream(initial_state, stream_mode="values")


def create_email_drafting_agent(
    rag_processor: Optional[RAGProcessor] = None,
    model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", 
    temperature: float = 0.7,
    verbose: bool = True
) -> EmailDraftingAgent:
    """
    Create and configure an email drafting agent.
    
    Args:
        rag_processor: RAG processor for document retrieval
        model_name: Language model name
        temperature: Temperature for model generation
        verbose: Whether to print detailed information
        
    Returns:
        Configured EmailDraftingAgent
    """
    return EmailDraftingAgent(
        rag_processor=rag_processor,
        model_name=model_name,
        temperature=temperature,
        verbose=verbose
    )
