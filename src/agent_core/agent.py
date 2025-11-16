import asyncio
import os
from dotenv import load_dotenv
from holistic_ai_bedrock import HolisticAIBedrockChat, get_chat_model
from langchain.agents import create_agent


load_dotenv()

HOLISTIC_AI_TEAM_ID = os.getenv("HOLISTIC_AI_TEAM_ID")
HOLISTIC_AI_KEY = os.getenv("HOLISTIC_AI_API_TOKEN")

os.environ["USER_AGENT"] = "my-langchain-agent/1.0"

system_prompt = """
You are the project Supervisor Agent.
Your responsibilities:

1. If project_state is empty, parse assignment brief, create tasks and use ask_user tool to ask the user about their skills and preferences, allocate tasks, and store it via set_state tool.
2. If project_state exists, compare current progress with expected timeline.
3. If deviation detected, call corrective_action tool.
4. You MUST either call a tool or return 'NO_ACTION'

You operate autonomously and maintain a persistent project state.
"""

async def main():
    tools = []
    llm = get_chat_model("claude-3-5-sonnet")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "read my assignement file"}
        ]
    })

    print(result)

if __name__ == "__main__":
    asyncio.run(main())