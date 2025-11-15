import asyncio
import os
from dotenv import load_dotenv
from holistic_ai_bedrock import HolisticAIBedrockChat, get_chat_model
from langchain.tools import tool
from langchain.agents import create_agent

load_dotenv()

HOLISTIC_AI_TEAM_ID = os.getenv("HOLISTIC_AI_TEAM_ID")
HOLISTIC_AI_KEY = os.getenv("HOLISTIC_AI_API_TOKEN")

os.environ["USER_AGENT"] = "my-langchain-agent/1.0"

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    result = a + b
    print(f"  Computing: {a} + {b} = {result}")
    return result


@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b
    """
    result = a * b
    print(f"  Computing: {a} × {b} = {result}")
    return result

async def main():
    tools = [add_numbers, multiply_numbers]
    llm = get_chat_model("claude-3-5-sonnet")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="You are a helpful research assistant."
    )

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "Research AI safety trends"}
        ]
    })

    print(result)

if __name__ == "__main__":
    asyncio.run(main())