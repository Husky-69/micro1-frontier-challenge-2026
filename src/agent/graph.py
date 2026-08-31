# src/agent/graph.py
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END
from src.agent.logger import TrajectoryLogger
from src.agent.tools import SandboxedTools

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[List[Any], lambda x, y: x + y]
    run_id: str


llm = ChatOpenAI(
    model="qwen/qwen3.8-27b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

logger = TrajectoryLogger(run_id="competition_run_01")
tools = SandboxedTools(logger)

# Bind ALL FOUR tools now, not just one
llm_with_tools = llm.bind_tools([
    tools.execute_consequential_action,
    tools.analyze_code_complexity,
    tools.check_test_coverage,
    tools.check_dependency_health,
    tools.check_maintenance_health,
])

# Map tool names to their real callables, for correct dispatch
TOOL_MAP = {
    "analyze_code_complexity": tools.analyze_code_complexity,
    "check_test_coverage": tools.check_test_coverage,
    "check_dependency_health": tools.check_dependency_health,
    "check_maintenance_health": tools.check_maintenance_health,
}


def call_model(state: AgentState):
    messages = state["messages"]
    if logger.run_id != state.get("run_id"):
        logger.set_run(state["run_id"])
    logger.log_thought("Calling LLM to decide next action...")
    response = llm_with_tools.invoke(messages)
    logger.log_thought(
        f"LLM Response: {response.content if response.content else 'Tool call requested'}"
    )
    return {"messages": [response]}


def human_review_node(state: AgentState):
    """Runs read-only analysis tools directly. Only pauses for human
    approval on the consequential-action tool."""
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        tool_name = tool_call["name"]
        logger.log_thought(f"Tool call requested: {tool_name} with args: {tool_call['args']}")

        if tool_name == "execute_consequential_action":
            action_desc = tool_call["args"].get("action_description", "Unknown action")
            approval = input(
                f"\n[⚠️ HUMAN CHECKPOINT] Agent wants to: {action_desc}\nApprove? (yes/no): "
            ).strip().lower()
            logger.log_human_checkpoint(action_desc, approval)

            if approval == "yes":
                result = tools.execute_consequential_action(action_desc)
            else:
                result = "Human denied this action. Please propose a different, safer approach."

            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

        elif tool_name in TOOL_MAP:
            result = TOOL_MAP[tool_name](**tool_call["args"])
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

        else:
            error_msg = f"Unknown tool requested: {tool_name}"
            return {"messages": [ToolMessage(content=error_msg, tool_call_id=tool_call["id"])]}

    return {"messages": []}


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


workflow.add_conditional_edges(
    "agent", should_continue, {"human_review": "human_review", "end": END}
)
workflow.add_edge("human_review", "agent")
app = workflow.compile()
