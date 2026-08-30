# src/agent/tools.py
import os
from radon.complexity import cc_visit
from src.agent.logger import TrajectoryLogger

class SandboxedTools:
    def __init__(self, logger: TrajectoryLogger):
        self.logger = logger

    def execute_consequential_action(self, action_description: str) -> str:
        """A sandboxed tool that requires human approval before executing."""
        self.logger.log_thought(f"I need to perform a consequential action: {action_description}")
        self.logger.log_tool_call("execute_consequential_action", {"action": action_description})
        
        approval = input(f"\n[⚠️ HUMAN CHECKPOINT] Agent wants to: {action_description}\nApprove? (yes/no): ").strip().lower()
        self.logger.log_human_checkpoint(action_description, approval)
        
        if approval == "yes":
            self.logger.log_tool_result("execute_consequential_action", "Action approved and executed.", True)
            return "Success: Action executed safely in sandbox."
        else:
            self.logger.log_tool_result("execute_consequential_action", "Action denied by human.", False)
            return "Error: Human denied the action. Please revise your approach."

    def analyze_code_complexity(self, repo_path: str) -> str:
        """Analyzes cyclomatic complexity of Python files. Lower average = simpler, more maintainable code."""
        self.logger.log_tool_call("analyze_code_complexity", {"repo_path": repo_path})
        py_files = []
        for root, _, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
                    
        if not py_files:
            result = "No Python files found in this repository."
            self.logger.log_tool_result("analyze_code_complexity", result, True)
            return result
            
        total_complexity = 0
        blocks_counted = 0
        # Sample up to 15 files to keep execution fast and avoid token limits
        for f in py_files[:15]:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as file:
                    blocks = cc_visit(file.read())
                    total_complexity += sum(b.complexity for b in blocks)
                    blocks_counted += len(blocks)
            except Exception:
                pass
                
        avg = (total_complexity / blocks_counted) if blocks_counted > 0 else 0
        result = f"Analyzed {len(py_files)} Python files (sampled {min(15, len(py_files))}). Average cyclomatic complexity per function/block: {avg:.2f}. (Under 10 is good, 10-20 is moderate, 20+ is high risk.)"
        self.logger.log_tool_result("analyze_code_complexity", result, True)
        return result

    def check_test_coverage(self, repo_path: str) -> str:
        """Checks whether a tests directory exists and how many test files it contains."""
        self.logger.log_tool_call("check_test_coverage", {"repo_path": repo_path})
        candidates = ["tests", "test"]
        found_dir = None
        for c in candidates:
            p = os.path.join(repo_path, c)
            if os.path.isdir(p):
                found_dir = p
                break
                
        if not found_dir:
            result = "No 'tests/' or 'test/' directory found. Major red flag for code quality."
        else:
            test_files = [f for f in os.listdir(found_dir) if f.endswith(".py")]
            result = f"Found '{os.path.basename(found_dir)}/' directory with {len(test_files)} test files."
            
        self.logger.log_tool_result("check_test_coverage", result, True)
        return result

    def check_dependency_health(self, repo_path: str) -> str:
        """Checks for requirements.txt or pyproject.toml and reports dependency count."""
        self.logger.log_tool_call("check_dependency_health", {"repo_path": repo_path})
        req_file = os.path.join(repo_path, "requirements.txt")
        pyproject = os.path.join(repo_path, "pyproject.toml")
        
        if os.path.exists(req_file):
            with open(req_file, "r", encoding="utf-8", errors="ignore") as f:
                deps = [line for line in f if line.strip() and not line.startswith("#")]
            result = f"Found requirements.txt with {len(deps)} dependencies listed."
        elif os.path.exists(pyproject):
            result = "Found pyproject.toml (indicates modern dependency management)."
        else:
            result = "No requirements.txt or pyproject.toml found. Dependency management is unclear."
            
        self.logger.log_tool_result("check_dependency_health", result, True)
        return result 
