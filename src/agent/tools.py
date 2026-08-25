from .logger import TrajectoryLogger

class SandboxedTools:
    def __init__(self, logger: TrajectoryLogger):
        self.logger = logger

    def execute_consequential_action(self, action_description: str) -> str:
        """Sandboxed tool requiring human approval."""
        self.logger.log_thought(f"Proposing consequential action: {action_description}")
        self.logger.log_tool_call("execute_consequential_action", {"action": action_description})

        approval = input(f"\n[⚠️ HUMAN CHECKPOINT] Agent wants to: {action_description}\nApprove? (yes/no): ").strip().lower()

        self.logger.log_human_checkpoint(action_description, approval)

        if approval == "yes":
            self.logger.log_tool_result("execute_consequential_action", "Action approved and executed.", True)
            return "Success: Action executed safely in sandbox."
        else:
            self.logger.log_tool_result("execute_consequential_action", "Action denied by human.", False)
            return "Error: Human denied the action."