import os
from dotenv import load_dotenv
from holistic_ai_bedrock import HolisticAIBedrockChat, get_chat_model

load_dotenv()

HOLISTIC_AI_TEAM_ID = os.getenv("HOLISTIC_AI_TEAM_ID")
HOLISTIC_AI_KEY = os.getenv("HOLISTIC_AI_API_TOKEN")
VALYU_KEY = os.getenv("VALYU_API_KEY")

import time

# Example 1: Direct LLM Call (Simple)
print("="*70)
print("EXAMPLE 1: Direct LLM Call")
print("="*70)

# Use the helper function - uses Holistic AI Bedrock by default
llm = get_chat_model("claude-3-5-sonnet")  # Uses Holistic AI Bedrock (recommended)

question = "What is quantum computing?"
print(f"\n❓ Question: {question}")

start_time = time.time()
response = llm.invoke(question)
elapsed = time.time() - start_time

print(f"\n💬 Response: {response.content}")
print(f"\n⏱️  Time: {elapsed:.2f}s")
print("\n✅ Simple and fast!")
print("❌ But... can't use tools, can't reason through steps, single response only")