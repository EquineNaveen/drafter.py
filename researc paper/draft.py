from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv 
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint 
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    task="text-generation",
)



document_content = ""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def update(content: str) -> str:
    """Updates the document with the provided content."""
    global document_content
    document_content = content
    return "Document has been updated successfully!"


@tool
def save(filename: str) -> str:
    """Save the current document to a text file and finish the process.
    
    Args:
        filename: Name for the text file.
    """

    global document_content

    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"


    try:
        with open(filename, 'w') as file:
            file.write(document_content)
        print(f"\n💾 Document has been saved to: {filename}")
        return f"Document has been saved successfully to '{filename}'."
    
    except Exception as e:
        return f"Error saving document: {str(e)}"
    

tools = [update, save]

model = ChatHuggingFace(llm=llm).bind_tools(tools)


def our_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.

    - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
    - If the user wants to save and finish, you need to use the 'save' tool.
    - Make sure to always show the current document state after modifications.
    """)

    if not state["messages"]:
        # If there are no messages, return a welcome message.
        response = AIMessage(content="I'm ready to help you update a document. What would you like to create?")
        return {"messages": [response]}

    all_messages = [system_prompt] + list(state["messages"])

    response = model.invoke(all_messages)

    # The print statements are for the console version.
    # print(f"\n🤖 AI: {response.content}")
    # if hasattr(response, "tool_calls") and response.tool_calls:
    #     print(f"🔧 USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end the conversation."""

    messages = state["messages"]
    
    if not messages:
        return "continue"
    
   
    for message in reversed(messages):
       
        if (isinstance(message, ToolMessage) and 
            "saved" in message.content.lower() and
            "document" in message.content.lower()):
            return "end" # goes to the end edge which leads to the endpoint
        
    return "continue"

def print_messages(messages):
    """Function to print the messages in a more readable format"""
    if not messages:
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n🛠️ TOOL RESULT: {message.content}")


graph = StateGraph(AgentState)

graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")

graph.add_edge("agent", "tools")


graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "agent",
        "end": END,
    },
)

app = graph.compile()

def run_document_agent():
    print("\n ===== DRAFTER =====")
    
    messages = []

    # Start with an initial empty state to get the welcome message
    initial_state = app.invoke({"messages": []})
    messages.extend(initial_state['messages'])
    
    # Print the initial welcome message
    for message in initial_state['messages']:
        if isinstance(message, AIMessage):
            print(f"\n🤖 AI: {message.content}")

    while True:
        user_input = input("\nWhat would you like to do with the document? ")
        print(f"\n👤 USER: {user_input}")
        
        messages.append(HumanMessage(content=user_input))
        
        result = app.invoke({"messages": messages})
        
        new_messages = result['messages'][len(messages):]
        messages.extend(new_messages)
        
        for message in new_messages:
            if isinstance(message, AIMessage):
                print(f"\n🤖 AI: {message.content}")
                if hasattr(message, "tool_calls") and message.tool_calls:
                    print(f"🔧 USING TOOLS: {[tc['name'] for tc in message.tool_calls]}")
            elif isinstance(message, ToolMessage):
                print(f"\n🛠️ TOOL RESULT: {message.content}")

        if should_continue(result) == "end":
            break
    
    print("\n ===== DRAFTER FINISHED =====")

if __name__ == "__main__":
    run_document_agent()