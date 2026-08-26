# src/agent/graph.py
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END

from src.agent.logger import TrajectoryLogger
from src.agent.tools import SandboxedTools

# Load environment variables
load_dotenv()

# 1. Define the State
class AgentState(TypedDict):
    messages: Annotated[List[Any], lambda x, y: x + y]
    run_id: str


# 2. Initialize the LLM (Using Groq's OpenAI-compatible endpoint)
llm = ChatOpenAI(
    model="qwen/qwen3.8-27b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),  # Explicitly pass the Groq key
    base_url="https://api.groq.com/openai/v1"
)

logger = TrajectoryLogger(run_id="competition_run_01")
tools = SandboxedTools(logger)

# Bind the tool to the LLM
llm_with_tools = llm.bind_tools([tools.execute_consequential_action])

# 3. Define the Nodes
def call_model(state: AgentState):
    """The brain: decides what to do next."""
    messages = state["messages"]
    logger.log_thought("Calling LLM to decide next action...")
    
    response = llm_with_tools.invoke(messages)
    logger.log_thought(f"LLM Response: {response.content if response.content else 'Tool call requested'}")
    
    return {"messages": [response]}

def human_review_node(state: AgentState):
    """The Checkpoint: Pauses for human approval."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        action_desc = tool_call['args'].get('action_description', 'Unknown action')
        
        logger.log_thought(f"Tool call requested: {tool_call['name']} with args: {tool_call['args']}")
        
        # Simulate human-in-the-loop
        approval = input(f"\n[⚠️ HUMAN CHECKPOINT] Agent wants to: {action_desc}\nApprove? (yes/no): ").strip().lower()
        logger.log_human_checkpoint(action_desc, approval)
        
        if approval == "yes":
            result = tools.execute_consequential_action(action_desc)
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call['id'])]}
        else:
            error_msg = "Human denied this action. Please propose a different, safer approach."
            return {"messages": [ToolMessage(content=error_msg, tool_call_id=tool_call['id'])]}
            
    return {"messages": []}

# 4. Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("human_review", human_review_node)
workflow.set_entry_point("agent")

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "human_review"
    return "end"

workflow.add_conditional_edges("agent", should_continue, {"human_review": "human_review", "end": END})
workflow.add_edge("human_review", "agent")

app = workflow.compile()
