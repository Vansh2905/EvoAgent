from typing import Any
from app.agent.state import AgentState
from app.tools.tool_manager import ToolManager

class AgentExecutor:
    def __init__(self,tool_manager:ToolManager):
        self.tool_manager = tool_manager

    def execute_action(self,state:AgentState,tool_name:str,arguments:dict[str,Any])->dict[str,Any]:
        """Execute one registered tool and record its outcome."""
        state.iterations+=1
        state.add_actions(tool_name,arguments)

        try:
            result=self.tool_manager.execute_tool(tool_name,arguments)
            observation={
                "tool":tool_name,
                "success":True,
                "result":result
            }
        except Exception as exc:
            observation={
                "tool":tool_name,
                "success":False,
                "error":str(exc)
            }

        state.add_observations(tool_name,observation)

        return observation