import json 
from app.models.llm_provider import generate_response

system_prompt="""
You are the planning engine of EvoAgent, an autonomous AI agent.

Your job is to break a user's task into clear, actionable steps.

Return ONLY valid JSON using this structure:

{
    "task": "The user's task",
    "reasoning": "Brief explanation of the approach",
    "steps": [
        {
            "step": 1,
            "description": "What needs to be done",
            "tool": "none",
            "arguments": {}
        }
    ],
    "success_criteria": [
        "How to determine whether the task succeeded"
    ]
}

Rules:
- Use "none" when a step requires no tool.
- Do not invent tools.
- Available tools are currently: none.
- Do not claim that a task has been executed.
- Keep plans specific, practical, and concise.
- Return valid JSON only.
"""


async def create_plan(task: str,available_tools:list[dict]) -> dict:
    if not task or not task.strip():
        raise ValueError("Task cannot be empty.")
    available_tools=available_tools or []

    tool_names = []

    for tool in available_tools:
        if not isinstance(tool, dict):
            raise ValueError("Each tool definition must be a dictionary.")

        name = tool.get("name")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Each tool must have a valid name.")

        if name in tool_names:
            raise ValueError(f"Duplicate tool definition: {name}")

        tool_names.append(name)

    prompt = (
        f"USER TASK:\n{task}\n\n"
        f"AVAILABLE TOOLS:\n"
        f"{json.dumps(available_tools, indent=2)}"
    )

    response = await generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
    )
    try:
        plan = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON: {response!r}"
        ) from exc

    if not isinstance(plan, dict):
        raise ValueError(
            f"Expected a JSON object, got {type(plan).__name__}: "
            f"{plan!r}"
        )

    if not isinstance(plan.get("steps"), list):
        raise ValueError("The plan must contain a steps list.")

    if not isinstance(plan.get("success_criteria"), list):
        raise ValueError("The plan must contain success_criteria.")

    for step in plan["steps"]:
        if not isinstance(step, dict):
            raise ValueError("Each step must be a JSON object.")

        if not isinstance(step.get("description"), str):
            raise ValueError("Each step needs a description.")

        tool_name = step.get('tool')

        if tool_name != "none" and tool_name not in tool_names:
            raise ValueError(
                f"Planner requested an unavailable tool: {tool_name}"
            )

        arguments = step.get("arguments")
        
        if not isinstance(step.get("arguments"), dict):
            raise ValueError("Step arguments must be an object.")

        if tool_name == "none" and arguments:
            raise ValueError(
                "A step without a tool cannot have tool arguments."
            )

    return plan
