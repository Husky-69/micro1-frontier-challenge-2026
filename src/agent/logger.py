import json
import datetime
from pathlib import Path

class TrajectoryLogger:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.log_file = Path(f"trajectories/{run_id}_trajectory.md")
        self.log_file.parent.mkdir(exist_ok=True)
        # Clear previous run
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"# Agent Execution Trajectory\n**Run ID:** {run_id}\n**Started:** {datetime.datetime.now().isoformat()}\n\n---\n\n")

    def _write(self, content: str):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(content + "\n")

    def log_thought(self, thought: str):
        self._write(f"### 🧠 Thought\n*{thought}*\n")

    def log_tool_call(self, tool_name: str, args: dict):
        self._write(f"### 🛠️ Tool Call: `{tool_name}`\n```json\n{json.dumps(args, indent=2)}\n```\n")

    def log_tool_result(self, tool_name: str, result: str, success: bool):
        status = "✅ Success" if success else "❌ Failed"
        self._write(f"### {status} Result: `{tool_name}`\n```\n{result}\n```\n")

    def log_human_checkpoint(self, action: str, decision: str):
        self._write(f"### 🛑 Human-in-the-Loop Checkpoint\n**Proposed Action:** {action}\n**Human Decision:** {decision}\n")