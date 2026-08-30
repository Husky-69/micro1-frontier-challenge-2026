# src/agent/logger.py
import json
from pathlib import Path


class TrajectoryLogger:
    def __init__(self, run_id: str):
        self.run_id = None
        self.log_file = None
        self.set_run(run_id)

    def set_run(self, run_id: str):
        """Point the logger at a fresh trajectory file for a new run."""
        self.run_id = run_id
        self.log_file = Path(f"trajectories/{run_id}_trajectory.md")
        self.log_file.parent.mkdir(exist_ok=True)
        self._write("# Agent Execution Trajectory\n")

    def _write(self, content: str):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(content + "\n")

    def log_thought(self, thought: str):
        self._write(f"### Thought\n*{thought}*\n")

    def log_tool_call(self, tool_name: str, args: dict):
        self._write(f"### Tool Call: `{tool_name}`\n```json\n{json.dumps(args, indent=2)}\n```\n")

    def log_tool_result(self, tool_name: str, result: str, success: bool):
        status = "Success" if success else "Failed"
        self._write(f"### {status} Result: `{tool_name}`\n```\n{result}\n```\n")

    def log_human_checkpoint(self, action: str, decision: str):
        self._write(
            f"### Human-in-the-Loop Checkpoint\n**Proposed Action:** {action}\n**Human Decision:** {decision}\n"
        )
