from typing import Any
from app.agent.state import AgentState
from app.agent.planner import create_plan
from app.agent.executor import AgentExecutor
from app.tools.tool_manager import ToolManager


class EvoAgent:

    def __init__(
        self,
        tool_manager: ToolManager,
        runtime_arguments: dict[str, dict[str, Any]] | None = None,
    ):
        self.tool_manager = tool_manager
        self.executor = AgentExecutor(tool_manager)
        self.runtime_arguments = runtime_arguments or {}

    async def run(self, task: str) -> dict[str, Any]:

        if not task or not task.strip():
            raise ValueError("Task cannot be empty.")

        # 1. Initialize agent state
        state = AgentState(task=task)
        state.add_message("user", {"task": task})

        # 2. Get available tools
        available_tools = self.tool_manager.list_tools()

        # 3. Generate execution plan
        plan = await create_plan(
            task=task,
            available_tools=available_tools,
        )

        state.add_message("assistant", {"plan": plan})

        # 4. Execute planned steps
        for step in plan["steps"]:

            tool_name = step["tool"]
            arguments = step["arguments"]

            # Skip steps that don't require a tool
            if tool_name == "none":
                continue

            # 5. Inject trusted runtime arguments
            trusted_arguments = self.runtime_arguments.get(
                tool_name, {}
            )

            if set(arguments) & set(trusted_arguments):
                raise ValueError(
                    f"Planner attempted towverride trusted "
                    f"arguments for tool: {tool_name}"
                )

            execution_arguments = {
                **arguments,
                **trusted_arguments,
            }

            # 6. Execute tool
            observation = self.executor.execute_action(
                state=state,
                tool_name=tool_name,
                arguments=execution_arguments,
            )

            state.add_message(
                "assistant",
                {"observation": observation},
            )

            # Stop if a tool fails
            if not observation["success"]:
                break

        # 7. Determine completion status
        failed = any(
            not observation["results"]["success"]
            for observation in state.observations
        )

        state.completed = not failed

        # 8. Return execution result
        return {
            "task": state.task,
            "plan": plan,
            "actions": state.actions,
            "observations": state.observations,
            "iterations": state.iterations,
            "completed": state.completed,
        }
