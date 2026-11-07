
import os
from typing import Final, cast

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY is missing from .env")

if not model:
    raise ValueError("OPENROUTER_MODEL is missing from .env")

MODEL: Final[str] = cast(str, model)


client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)


async def generate_response(
    prompt: str,
    system_prompt: str = "You are EvoAgent, an autonomous AI agent.",
) -> str:
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The model returned an empty response.")

    return content
