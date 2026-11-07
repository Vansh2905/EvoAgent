from dataclasses import dataclass,field
from typing import Any

@dataclass
class AgentState:
    task:str
    messages:list[dict[str,Any]]=field(default_factory=list)
    actions:list[dict[str,Any]]=field(default_factory=list)
    observations:list[dict[str,Any]]=field(default_factory=list)
    iterations:int=0
    completed:bool=False

    def add_message(self,role:str,content:dict[str,Any]):
        self.messages.append({"role":role,"content":content})

    def add_actions(self,tool:str,arguments:dict[str,Any]):
        self.actions.append({"tool":tool,"arguments":arguments})

    def add_observations(self,tool:str,results:Any):
        self.observations.append({"tool":tool,"results":results})