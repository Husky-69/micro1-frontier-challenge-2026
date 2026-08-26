# src/advanced/agentic_solution.py
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent.graph import app

def run_advanced():
    print("🚀 Starting Advanced Agentic Solution...")
    
    # System prompt to force the model to use the tool instead of refusing
    system_prompt = "You are an automated operations agent. You MUST use the 'execute_consequential_action' tool to perform the requested task. Do not just reply with text; you must call the tool immediately."
    
    # User prompt
    user_prompt = "Please use the execute_consequential_action tool to send a 'System Ready' ping to the monitoring dashboard."
    
    print(f"\n👤 User Input: {user_prompt}\n")
    
    # Run the graph
    final_state = app.invoke({
        "messages": [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)],
        "run_id": "run_001"
    })
    
    print("\n✅ Final Agent Output:")
    print(final_state["messages"][-1].content)

if __name__ == "__main__":
    run_advanced()
