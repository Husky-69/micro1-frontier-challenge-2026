# src/advanced/agentic_solution.py
import sys
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent.graph import app


def run_advanced(repo_to_evaluate: str, run_id: str):
    print("🚀 Starting Advanced Agentic Code Quality Evaluation...\n")

    system_prompt = """You are an expert Code Quality Analyst. Your job is to evaluate Python repositories. 
    You MUST use the provided tools (`analyze_code_complexity`, `check_test_coverage`, `check_dependency_health`, `check_maintenance_health`) to gather evidence. 
    Do not guess. Run the tools on the provided repo path, synthesize the results, and output a final Quality Score (1-10) with a clear, evidence-based justification."""

    user_prompt = f"Evaluate the code quality of the repository located at: {repo_to_evaluate}"

    print(f"👤 Evaluating: {repo_to_evaluate}  (run_id={run_id})\n")

    final_state = app.invoke({
        "messages": [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)],
        "run_id": run_id
    })

    print("\n✅ Final Agent Assessment:")
    print(final_state["messages"][-1].content)


if __name__ == "__main__":
    # Usage: python -m src.advanced.agentic_solution <repo_path> <run_id>
    if len(sys.argv) < 3:
        print("Usage: python -m src.advanced.agentic_solution <repo_path> <run_id>")
        sys.exit(1)
    run_advanced(sys.argv[1], sys.argv[2])
